""" To be added to the automation package upon testing
"""
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import Column, Integer, String, DateTime, Float, PickleType
from sqlalchemy import and_, func
from threading import Event
from enum import DeclEnum
from twisted.python import log

Base = declarative_base()

class ExperimentStatus(DeclEnum):
    """ Defines the states that an experiment can be in
    """
    
    Queued = "Queued"
    Paused = "Paused"
    Running = "Running"
    Finished = "Finished"
    Aborted = "Aborted"
    Failed = "Failed"

class ExperimentMixin(object):
    """ Provides columns for experiments, which are used by the worker
    """
    
    id = Column(Integer, primary_key=True)
    status = Column(ExperimentStatus.db_type(), default=ExperimentStatus.Queued)
    created_on = Column(DateTime, default=func.now)
    modified_on = Column(DateTime, default=func.now, onupdate=func.now)
    started_on = Column(DateTime)
    stopped_on = Column(DateTime)

"""
class WorkerAddress(Base):
    "" Stores the network address of the workers so that the update triggers
    can dynamically address their worker
    ""
    
    __tablename__ = 'worker_addresses'
    
    name = Column(String(200))
    host = Column(String(200), default='localhost')
    port = Column(Integer)
"""

class Worker(object):
    """ Manages a queue of ExperimentMixin children classes from the database,
    waking to check for updates when the wake method is called    
    """

    __experiment_class__ = None

    def __init__(self, session):
        if __experiment_class__ == None:
            raise ValueError("Undefined `__experiment_class__` variable")
        self.session = session
        self._listeners = []
        self.shouldAbortEvent = Event()
        self.deferred = None
        self._isRunning = False
        self._runningExperiment = None

    # Database aware methods

    def wake(self):
        """ Interigates the database to update its knowledge of (1) new items
        in the queue and (2) aborted procedures, should be called on update
        or insert of the database
        """
        self.log("Woke up to check database")
        if self.isRunning():
            if self._isAborted():
                self.log("Found current experiment is aborted")
                self.abort()
                self._pauseAll()
        else:
            # Check for new queued experiments
            experiment = self._next()
            if experiment != None:
                self.log("Found the next experiment to run")
                self.run(experiment)

    def _isAborted(self):
        """ Checks for abort flag on running experiment
        """
        cls = self.__experiment_class__
        count = self.session.query(func.count('*')).\
                    select_from(cls).\
                    filter(and_(cls.id == self._runningExperiment.id,
                    cls.status == ExperimentStatus.Aborted)).scalar()
        return count > 0

    def _pauseAll(self):
        """ Pauses all queued experiments, to be used after an abort or
        failure
        """
        cls = self.__experiment_class__
        experiments = self.session.query(cls).\
                        filter(cls.status == ExperimentStatus.Queued).\
                        all()
        for experiment in experiments:
            experiment.status = ExperimentStatus.Paused
        self.session.commit()
        self.log("Paused all queued experiments")

    def _next(self):
        """ Returns the next experiment object in the queue, or None otherwise
        """
        cls = self.__experiment_class__
        return self.session.query(cls).\
                    filter(cls.status == ExperimentStatus.Queued).\
                    order_by(cls.created_on).\
                    first()
                    
    def _setStatus(self, status):
        """ Sets the status of the running experiment
        """
        self._runningExperiment.status = status
        self.session.commit()

    # Synchronous methods (to be called in thread)

    def procedure(self, experiment):
        """ Method that contains the procedure to be executed at run-time,
        which is given the experiment object corresponding to the running entry
        """
        pass
    
    def shouldAbort(self):
        """ Returns a boolean value indicating if the procedure execution
        should be terminated by the procedure. This should be monitored in
        all blocking calls to ensure that an abort is caught properly.        
        """
        return self.shouldAbortEvent.isSet()
        
    def emit(self, keyword, *args, **kwargs):
        """ Sends arguments based on keyword through an internal asynchronous 
        method to listeners in the asyncronous code (e.g. GUI, Twisted
        components).        
        """
        from twisted.internet import reactor
        reactor.callFromThread(self._emit, keyword, *args, **kwargs)
        
    def log(self, message):
        """ Sends a log to the Twisted logging system and to any listeners of the
        keyword 'log'.
        """
        from twisted.internet import reactor
        reactor.callFromThread(log.msg, message)
        self.emit('log', message)
        

    # Asynchronous methods (to be called in reactor)
        
    def run(self):
        """ Runs the next experiment in the thread pool based on the  procedure
        """
        # Get the next experiment object
        experiment = self.__experiment_class__.next()
        self._runningExperiment = experiment
        
        self.deferred = defer.Deferred(self._aborted)
            
        def onResult(success, result):
            if self.deferred.called:
                # the deferred has been called by the abort method
                return
            else:
                if success:
                    reactor.callFromThread(self.deferred.callback, result)
                else:
                    reactor.callFromThread(self.deferred.errback, result)

        from twisted.internet import reactor
        reactor.getThreadPool().callInThreadWithCallback(onResult, 
                                    lambda : self.procedure(experiment))
        self.deferred.addCallbacks(self._finished, self._failed)
        self._isRunning = True
        self._setStatus(ExperimentStatus.Running)
        self.running(self._runningExperiment)
        return self.deferred
       
    def abort(self):
        """ Sets the abort event so that the procedure in the thread
        can catch the abort and end its own execution.        
        """
        if self.isRunning():
            self.shouldAbortEvent.set()
            self.deferred.cancel()
    
    def isRunning(self):
        """ Returns True if an experiment is currently running
        """
        return self._isRunning
        
    def connect(self, keyword, callback):
        """ Add a callback function to be called when a signal
        containing the keyword is sent.        
        """
        self._listeners.append((keyword, callback))

    # Private callback methods
    
    def _finished(self, result):
        """ Callback function that cleans up after running a experiment  
        """
        log.msg("Successfully finished experiment %s" % self._runningExperiment)
        
        self._isRunning, self.deferred = False, None
        
        self._setStatus(ExperimentStatus.Finished)
        self.finished(self._runningExperiment)
        self._runningExperiment = None
        self.wake()
        
    def _failed(self, failure):
        """ Callback function that cleans up after running a experiment
        and catching an exception upon failure. Adds the exception to the
        queue for the experiment in question so the information is accessible.
        The method also accounts for user generated abort events.
        """
        self._isRunning, self.deferred = False, None
        
        if failure.check(defer.CancelledError) == None:
            log.msg("Caught exception in experiment %s" % self._runningExperiment)
            log.msg(failure)
            
            self._setStatus(ExperimentStatus.Failed)
            self._pauseAll()
            self.failed(self._runningExperiment, failure)
            self._runningExperiment = None
        else:
            # The experiment failed because of a user generated abort event
            # which has already been caught by self._aborted
            pass
        
    def _aborted(self, result=None):
        """ Callback function that cleans up after a user generated abort
        """
        log.msg("Caught abort event in experiment %s" % self._runningExperiment)
        
        self._isRunning, self.deferred = False, None
        
        self._setStatus(ExperimentStatus.Aborted)
        self.aborted(self._runningExperiment)
        self._runningExperiment = None    
    

    def _emit(self, keyword, *args, **kwargs):
        """ Send the arguments to those listeners that are interested
        in the keyword by envoking the callback provided.
        """
        for searchKeyword, callback in self._listeners:
            if keyword == searchKeyword:
                callback(*args, **kwargs)
                
    # Public callback methods that can be overwritten

    def running(self, experiment):
        """ Callback that exposes an experiment that has just started running
        """
        pass

    def finished(self, experiment):
        """ Callback that exposes an experiment that has just finished
        """
        pass
        
    def failed(self, experiment, failure):
        """ Callback that exposes an experiment that has just failed, with its
        reason for failure
        """
        pass
        
    def aborted(self, experiment):
        """ Callback that exposes an experiment that has just been aborted
        """
        pass                
