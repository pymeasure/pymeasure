from PyQt4.QtGui import QApplication
from PyQt4.QtCore import QCoreApplication, QTimer

def QTwistedApplication(args=[]):
    """ Creates an application instance if one does not already exist
    and starts up the Twisted reactor through qt4reactor, returning the 
    QApplication
    """
    app = QCoreApplication.instance()
    if app is None:
        app = QApplication([])
    try:
        import qt4reactor
        qt4reactor.install()
        from twisted.internet import reactor
        QTimer.singleShot(0, reactor.runReturn)
    except:
        pass
    return app
