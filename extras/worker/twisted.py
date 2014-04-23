""" Classes for Running Experiments on the Twisted Framework

Author: Colin Jermain <clj72@cornell.edu>
Created: 2013-05-07

Runs on Twisted Python Library

"""
from __future__ import absolute_import
from twisted.python import log
from twisted.internet import defer

from twisted.conch.ssh.common import NS
from twisted.conch.scripts.cftp import ClientOptions
from twisted.conch.ssh.filetransfer import FileTransferClient,  FXF_WRITE, FXF_CREAT
from twisted.conch.client.connect import connect
from twisted.conch.client.default import SSHUserAuthClient, verifyHostKey
from twisted.conch.ssh.connection import SSHConnection
from twisted.conch.ssh.channel import SSHChannel

from threading import Event
from inspect import getcallargs   
from datetime import datetime
import numpy as np
import re
import os
from os.path import basename
        

class Parameter(object):
    
    def __init__(self, unit=None, **kwargs):
        self.unit = unit

class CharParameter(Parameter):
    pass

class IntegerParameter(Parameter):
    pass

class DecimalParameter(Parameter):
    pass
    
class FloatParameter(Parameter):
    pass

        
class Experiment(object):
    """ The Experiment object encapsulates the procedure, its settings,
    and the link that it establishes with asyncronous code.    
    """
    
    def __init__(self, **kwargs):
        """ Construct the experiment object with all of the arguments that would
        be required if calling the procedure directly, as they are stored until
        run-time.
        """                      
        # Collect all the defined parameters
        self._parameters = {}
        for item in dir(self):
            parameter = getattr(self, item)
            if issubclass(parameter.__class__, Parameter):
                self._parameters[item] = parameter
                if item not in kwargs:
                    raise Exception("Missing parameter"
                           " '%s' for experiment '%s'" % (item, self.__class__))
                else:
                    setattr(self, item, kwargs[item])
                
        self._listeners = []
        self.shouldAbortEvent = Event()
        self.failure = None
       
    # Synchronous methods (to be called in thread)
    
    def procedure(self):
        """ Method that contains the procedure to be executed at run-time,
        with arguments that will be required to construct the Experiment
        object.
        """
        pass
        
    def shouldAbort(self):
        """ Returns a boolean value indicating if the procedure execution
        should be terminated by the procedure. This should be monitored in
        all blocking calls to ensure that an abort is caught properly.        
        """
        return self.shouldAbortEvent.isSet()
        
    def emit(self, keyword, *args, **kwargs):
        """ Sends arguments based on keyword through an internal asynchronous method
        to listeners in the asyncronous code (e.g. GUI, Twisted components).        
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
    
    def verify(self):
        """ Checks through the required parameters as determine at construction
        and raise an exception if a parameter is not set (set to None)
        """
        pass
        """
        for parameter in self._requiredParameters:
            if not getattr(self, parameter).isSet():
                raise ValueError("Parameter (%s) is not set in Experiment %s" % (parameter, repr(self)))
        """
    
    def run(self, abortCallback=None):
        """ Returns a Deferred and runs the procedure in the thread pool with an
        optional callback upon an abort event.
        """
        # Check all parameters
        self.verify()
        
        d = defer.Deferred(abortCallback)
            
        def onResult(success, result):
            if d.called: # the deferred has been called by the abort method
                return
            else:
                if success:
                    reactor.callFromThread(d.callback, result)
                else:
                    reactor.callFromThread(d.errback, result)

        from twisted.internet import reactor
        reactor.getThreadPool().callInThreadWithCallback(onResult, self.procedure)
        return d

    def abort(self):
        """ Sets the abort event so that the procedure in the thread
        can catch the abort and end its own execution.        
        """
        self.shouldAbortEvent.set()
        
    def connect(self, keyword, callback):
        """ Add a callback function to be called when a signal
        containing the keyword is sent.        
        """
        self._listeners.append((keyword, callback))
                
    def failed(self, failure):
        """ Store the failure for future interagation. """
        self.failure = failure

    def _emit(self, keyword, *args, **kwargs):
        """ Send the arguments to those listeners that are interested
        in the keyword by envoking the callback provided.
        """
        for searchKeyword, callback in self._listeners:
            if keyword == searchKeyword:
                callback(*args, **kwargs)


class Manager(object):
    """ The Manager allows experiments to be placed on a queue
    and coordinates their execution in an asyncronous fashion.
    It also provides methods for reordering the queue and aborting
    an experiment being run.
    """
    _queue = []
    _isRunning = False
    _isContinuous = True
    _startOnAdd = True
    deferred = None
    _runningExperiment = None

    # Callback methods that can be overwritten

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
        
    # Core methods
            
    def add(self, experiment):
        """ Adds the experiment to the queue and returns a deferred if the
        measurement is scheduled to start automatically, otherwise returning None    
        """
        assert type(experiment.id) == int
        self._queue.append(experiment)
        
        log.msg("Added experiment %s to manager queue" % experiment)
        
        if self.shouldStartOnAdd() and not self.isRunning():
            return self.next()
        return None
    
    def remove(self, experiment_id):
        """ Removes a experiment from the queue given its unique id        
        """
        if self.isRunning() and self.isExperimentRunning(experiment_id):
            raise Exception("Can not remove a experiment while it is running")
        else:
            experiment = self._queue.pop(self._qid(experiment_id))
            log.msg("Removed experiment %s from queue" % experiment)
            
    def swap(self, first_id, second_id):
        """ Swaps the order or two experiments in the queue as long as neither are
        currently running.
        """
        if self.isRunning() and (self.isExperimentRunning(first_id) or
                                 self.isExperimentRunning(second_id)):
            raise Exception("Can not swap a queue that is currently running")
        else:
            first_qid = self._qid(first_id)
            second_qid = self._qid(second_id) 
            tmp = self._queue[firstId]
            self._queue[firstId] = self._queue[secondId]
            self._queue[secondId] = tmp
            log.msg("Swapped experiment (%d) with (%d) in the queue" % (firstId, secondId))
        
    def abort(self):
        """ Stops the currently running experiment by initiating an abort event
        which has to be caught by the running experiment.        
        """
        if not self.isRunning():
            raise Exception("Abort request called when no experiment was running")
        else:
            log.msg("Initiating abort event for experiment %s" % self._runningExperiment)
            self._runningExperiment.abort()
            self.deferred.cancel()
        
    def next(self, result=False):
        """ Initiates the start of the next experiment in the queue as long
        as no other experiment is currently running and there is a experiment
        in the queue. Returns a deferred that has callbacks for success and failure.        
        """
        if self.isRunning():
            raise Exception("Another experiment is already running")
        else:
            if not self.experimentIsQueued():
                raise Exception("No experiments are queued")
            else:
                experiment = self._queue.pop(0) # pop from the left (FIFO)
                
                log.msg("Starting experiment %s" % experiment)
                
                self.deferred = experiment.run(self._aborted)
                self.deferred.addCallbacks(self._finished, self._failed)
                self._runningExperiment = experiment
                self._isRunning = True
                self.running(self._runningExperiment)
                return self.deferred
        
    def _finished(self, result):
        """ Callback function that cleans up after running a experiment  
        """
        log.msg("Successfully finished experiment %s" % self._runningExperiment)
        
        self._isRunning, self.deferred = False, None
        
        self.finished(self._runningExperiment)
        self._runningExperiment = None
        if self.isContinuous() and self.experimentIsQueued():
            self.next()
        
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
            
            self.failed(self._runningExperiment, failure)
            self._runningExperiment = None
        else:
            # The experiment failed because of a user generated abort event
            # which has already been caught by self._abort
            pass
        
    def _aborted(self, result=None):
        """ Callback function that cleans up after a user generated abort
        """
        log.msg("Caught abort event in experiment %s" % self._runningExperiment)
        
        self._isRunning, self.deferred = False, None
        
        self.aborted(self._runningExperiment)
        self._runningExperiment = None
        
        
    def _qid(self, experiment_id):
        """ Returns the position in the queue of the experiment with a given
        unique id
        """
        for qid, experiment in zip(range(len(self._queue)), self._queue):
            if experiment.id == experiment_id:
                return qid
        raise Exception("Experiment with id (%d) is not in the queue" % experiment_id)

    def isRunning(self):
        """ Returns a boolean that indicates if a experiment is currently
        running.
        """
        return self._isRunning

    def isExperimentRunning(self, experiment_id):
        """ Returns True if a specific experiment is running based on its
        unique identifier.        
        """
        return self._runningExperiment != None and self._runningExperiment == experiment_id

    def isContinuous(self):
        """ Returns a boolean that indicates if the manager should
        continue to call the next experiment in the queue upon success.        
        """
        return self._isContinuous
        
    def setContinuous(self, enable=True):
        """ Sets the manager to continue calling the next experiment upon
        success if True.        
        """
        self._isContinuous = enable
        
    def shouldStartOnAdd(self):
        """ Returns a boolean that indicates if the manager should
        start a experiment when added if there are no currently running
        experiments.        
        """
        return self._startOnAdd
        
    def setStartOnAdd(self, enable=True):
        """ Sets the manager to start a experiment upon adding it to the
        queue when no experiments are running if True.        
        """
        self._startOnAdd = enable   
    
    def experimentIsQueued(self):
        """ Returns True if there is another experiment waiting in the queue.
        """
        return len(self._queue) != 0
       
       
class SFTPSession(SSHChannel):
    """ Defines an SFTP session over SSH    
    """
    name = 'session'

    def channelOpen(self, whatever):
        d = self.conn.sendRequest(
            self, 'subsystem', NS('sftp'), wantReply=True)
        d.addCallbacks(self._cbSFTP)

    def _cbSFTP(self, result):
        client = FileTransferClient()
        client.makeConnection(self)
        self.dataReceived = client.dataReceived
        self.conn._sftp.callback(client)

class SFTPConnection(SSHConnection):
   
    def serviceStarted(self):
        self.openChannel(SFTPSession())

def connectSFTP(user, host, port):
    """ Opens a SFTP connection for the given user and 
    """
    options = ClientOptions()
    options['host'] = host
    options['port'] = port
    conn = SFTPConnection()
    conn._sftp = defer.Deferred()
    auth = SSHUserAuthClient(user, options, conn)
    connect(host, port, options, verifyHostKey, auth)
    return conn._sftp

class RemoteFile(object):
    """ Accesses a remote file over SSH given the connection is already made,
    will not handle multiple RemoteFiles on the same connection and does not
    handle reading the file yet
    """
    
    def __init__(self, connection, path, flags=FXF_CREAT|FXF_WRITE, attr={}):
        """ Opens the file given a SFTP connection based on the flags
        and attrs        
        """
        self.conn = connection
        self.path = path
        self.flags = flags
        self.conn.addCallback(lambda client: client.openFile(path, flags, attr))
        self.conn.addCallback(self._storeFileRef)
        self.offset = 0
        
    def _storeFileRef(self, fileRef):
        self.f = fileRef
        
    def write(self, string):
        self.conn.addCallback(lambda ignore: self._write(string))
    
    def _write(self, string):
        d = self.f.writeChunk(self.offset, string)
        self.offset += len(string)
        return d

class RemoteCSV(RemoteFile):
    """ Allows writing to a remote CSV file through an SFTP connection
    """
    
    DELIMITER = ','
    LINEBREAK = "\n"
    
    def __init__(self, connection, path, fields, flags=FXF_CREAT|FXF_WRITE, attr={}):
        self.fields = fields
        RemoteFile.__init__(self, connection, path, flags, attr)
        RemoteFile.write(self, self._format(fields))
    
    def _format(self, data):
        return self.DELIMITER.join([str(x) for x in data]) + self.LINEBREAK
    
    def write(self, data):
        RemoteFile.write(self, self._format([data[x] for x in self.fields]))
        
        

