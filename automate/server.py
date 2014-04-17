from twisted.web import xmlrpc, server
from automate.experiment import Experiment, Manager
import importlib

class ManagerServer(xmlrpc.XMLRPC):
    """ Wraps the experiment Manager object to allow remote
    access through XML-RPC. This server should be run as a
    daemon through twistd.    
    """

    def __init__(self):
        self.manager = Manager()
        
    def xmlrpc_addExperiment(self, experimentClass, *args, **kwargs):
        """ Tries to add an experiment to the queue by importing it,
        running the internal checks, and then pushing it onto the queue.
        Returns the qid (Queue ID) if successful, or None upon failure.       
        """
        try:
            ChildExperiment = importlib.import_module(experimentClass)
            if issubclass(ChildExperiment, Experiment):
                try:
                    experiment = Experiment(*args, **kwargs)
                    qid = self.manager.add(experiment)
                    return qid
                except:
                    return None
            else: 
                # Attempt at adding non-Experiment class to queue
                return None
        except ImportError:
            return None
            
    def xmlrpc_removeExperiment(self, qid):
        """ Removes an experiment based on the qid (Queue ID)       
        """
        try:
            self.manager.remove(qid)
            return True
        except:
            return False
            
    def xmlrpc_swapExperiments(self, qid1, qid2):
        """ Swap the order of two experiments in the queue based on
        their qid (Queue ID)
        """
        try:
            self.manager.swap(qid1, qid2)
            return True
        except:
            return False
    
    def xmlrpc_isExperimentRunning(self, qid):
        """ Returns True if the experiment with qid (Queue ID) is running
        """
        return self.manager.isExperimentRunning(qid)
    
    def xmlrpc_isRunning(self):
        """ Returns a boolean that indicates if an experiment is currently
        running.
        """
        return self.manager.isRunning()

if __name__ == '__main__':
    from twisted.internet import reactor
    r = Example()
    reactor.listenTCP(7080, server.Site(r))
    reactor.run()
