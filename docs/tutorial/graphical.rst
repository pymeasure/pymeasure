###########################
Using a graphical interface
###########################

In the previous tutorial we measured the IV characteristic of a sample to show how we can set up a simple experiment in PyMeasure. The real power of PyMeasure comes when we also use the graphical tools that are included to turn our simple example into a full-flegged user interface.

.. _tutorial-plotterwindow:

Using the Plotter
~~~~~~~~~~~~~~~~~

While it lacks the nice features of the ManagedWindow, the Plotter object is the simplest way of getting live-plotting. The Plotter takes a Results object and plots the data at a regular interval, grabbing the latest data each time from the file.

Let's extend our SimpleProcedure with a RandomProcedure, which generates random numbers during our loop. This example does not include instruments to provide a simpler example. ::

    import logging
    log = logging.getLogger(__name__)
    log.addHandler(logging.NullHandler())

    import random
    from time import sleep
    from pymeasure.log import console_log
    from pymeasure.display import Plotter
    from pymeasure.experiment import Procedure, Results, Worker
    from pymeasure.experiment import IntegerParameter, FloatParameter, Parameter

    class RandomProcedure(Procedure):

        iterations = IntegerParameter('Loop Iterations')
        delay = FloatParameter('Delay Time', units='s', default=0.2)
        seed = Parameter('Random Seed', default='12345')

        DATA_COLUMNS = ['Iteration', 'Random Number']

        def startup(self):
            log.info("Setting the seed of the random number generator")
            random.seed(self.seed)

        def execute(self):
            log.info("Starting the loop of %d iterations" % self.iterations)
            for i in range(self.iterations):
                data = {
                    'Iteration': i,
                    'Random Number': random.random()
                }
                self.emit('results', data)
                log.debug("Emitting results: %s" % data)
                sleep(self.delay)
                if self.should_stop():
                    log.warning("Caught the stop flag in the procedure")
                    break


    if __name__ == "__main__":
        console_log(log)

        log.info("Constructing a RandomProcedure")
        procedure = RandomProcedure()
        procedure.iterations = 100

        data_filename = 'random.csv'
        log.info("Constructing the Results with a data file: %s" % data_filename)
        results = Results(procedure, data_filename)

        log.info("Constructing the Plotter")
        plotter = Plotter(results)
        plotter.start()
        log.info("Started the Plotter")

        log.info("Constructing the Worker")
        worker = Worker(results)
        worker.start()
        log.info("Started the Worker")

        log.info("Joining with the worker in at most 1 hr")
        worker.join(timeout=3600) # wait at most 1 hr (3600 sec)
        log.info("Finished the measurement")

The important addition is the construction of the Plotter from the Results object. ::

    plotter = Plotter(results)
    plotter.start()

The Plotter is started in a different process so that it can be run on a separate CPU for higher performance. The Plotter launches a Qt graphical interface using pyqtgraph which allows the Results data to be viewed based on the columns in the data.

.. image:: pymeasure-plotter.png
    :alt: Results Plotter Example

.. _tutorial-managedwindow:

Using the ManagedWindow
~~~~~~~~~~~~~~~~~~~~~~~

The ManagedWindow is the most convenient tool for running measurements with your Procedure. This has the major advantage of accepting the input parameters graphically. From the parameters, a graphical form is automatically generated that allows the inputs to be typed in. With this feature, measurements can be started dynamically, instead of defined in a script.

Another major feature of the ManagedWindow is its support for running measurements in a sequential queue. This allows you to set up a number of measurements with different input parameters, and watch them unfold on the live-plot. This is especially useful for long running measurements. The ManagedWindow achieves this through the Manager object, which coordinates which Procedure the Worker should run and keeps track of its status as the Worker progresses.

Below we adapt our previous example to use a ManagedWindow. ::

    import logging
    log = logging.getLogger(__name__)
    log.addHandler(logging.NullHandler())

    import sys
    import tempfile
    import random
    from time import sleep
    from pymeasure.log import console_log
    from pymeasure.display.Qt import QtGui
    from pymeasure.display.windows import ManagedWindow
    from pymeasure.experiment import Procedure, Results
    from pymeasure.experiment import IntegerParameter, FloatParameter, Parameter

    class RandomProcedure(Procedure):

        iterations = IntegerParameter('Loop Iterations')
        delay = FloatParameter('Delay Time', units='s', default=0.2)
        seed = Parameter('Random Seed', default='12345')

        DATA_COLUMNS = ['Iteration', 'Random Number']

        def startup(self):
            log.info("Setting the seed of the random number generator")
            random.seed(self.seed)

        def execute(self):
            log.info("Starting the loop of %d iterations" % self.iterations)
            for i in range(self.iterations):
                data = {
                    'Iteration': i,
                    'Random Number': random.random()
                }
                self.emit('results', data)
                log.debug("Emitting results: %s" % data)
                sleep(self.delay)
                if self.should_stop():
                    log.warning("Caught the stop flag in the procedure")
                    break


    class MainWindow(ManagedWindow):

        def __init__(self):
            super(MainWindow, self).__init__(
                procedure_class=RandomProcedure,
                inputs=['iterations', 'delay', 'seed'],
                displays=['iterations', 'delay', 'seed'],
                x_axis='Iteration',
                y_axis='Random Number'
            )
            self.setWindowTitle('GUI Example')

        def queue(self):
            filename = tempfile.mktemp()

            procedure = self.make_procedure()
            results = Results(procedure, filename)
            experiment = self.new_experiment(results)

            self.manager.queue(experiment)


    if __name__ == "__main__":
        app = QtGui.QApplication(sys.argv)
        window = MainWindow()
        window.show()
        sys.exit(app.exec_())



This results in the following graphical display.

.. image:: pymeasure-managedwindow.png
    :alt: ManagedWindow Example

In the code, the MainWindow class is a sub-class of the ManagedWindow class. We override the constructor to provide information about the procedure class and its options. The :code:`inputs` are a list of Parameters class-variable names, which the display will generate graphical fields for. The :code:`displays` is a similar list, which instead defines the parameters to display in the browser window. This browser keeps track of the experiments being run in the sequential queue.

The :code:`queue` method establishes how the Procedure object is constructed. We use the :code:`self.make_procedure` method to create a Procedure based on the graphical input fields. Here we are free to modify the procedure before putting it on the queue. In this context, the Manager uses an Experiment object to keep track of the Procedure, Results, and its associated graphical representations in the browser and live-graph. This is then given to the Manager to queue the experiment.

.. image:: pymeasure-managedwindow-queued.png
    :alt: ManagedWindow Queue Example

By default the Manager starts a measurement when its procedure is queued. The abort button can be pressed to stop an experiment. In the Procedure, the :code:`self.should_stop` call will catch the abort event and halt the measurement. It is important to check this value, or the Procedure will not be responsive to the abort event.

.. image:: pymeasure-managedwindow-resume.png
    :alt: ManagedWindow Resume Example

If you abort a measurement, the resume button must be pressed to continue the next measurement. This allows you to adjust anything, which is presumably why the abort was needed.

.. image:: pymeasure-managedwindow-running.png
    :alt: ManagedWindow Running Example

Now that you have learned about the ManagedWindow, you have all of the basics to get up and running quickly with a measurement and produce an easy to use graphical interface with PyMeasure.

Customising the plot options
~~~~~~~~~~~~~~~~~~~~~~~~~~~~

For both the PlotterWindow and ManagedWindow, plotting is provided by the pyqtgraph_ library. This library allows you to change various plot options, as you might expect: axis ranges (by default auto-ranging), logarithmic and semilogarithmic axes, downsampling, grid display, FFT display, etc. There are two main ways you can do this:

1. You can right click on the plot to manually change any available options. This is also a good way of getting an overview of what options are available in pyqtgraph. Option changes will, of course, not persist across a restart of your program.
2. You can programmatically set these options using pyqtgraph's PlotItem_ API, so that the window will open with these display options already set, as further explained below.

For :class:`~pymeasure.display.plotter.Plotter`, you can make a sub-class that overrides the :meth:`~pymeasure.display.plotter.Plotter.setup_plot` method. This method will be called when the Plotter constructs the window. As an example ::

    class LogPlotter(Plotter):
        def setup_plot(self, plot):
            # use logarithmic x-axis (e.g. for frequency sweeps)
            plot.setLogMode(x=True)

For :class:`~pymeasure.display.windows.ManagedWindow`, Similarly to the Plotter, the :meth:`~pymeasure.display.windows.ManagedWindow.setup_plot` method can be overridden by your sub-class in order to do the set-up ::

    class MainWindow(ManagedWindow):

        # ...

        def setup_plot(self, plot):
            # use logarithmic x-axis (e.g. for frequency sweeps)
            plot.setLogMode(x=True)

        # ...

It is also possible to access the :attr:`~pymeasure.display.windows.ManagedWindow.plot` attribute while outside of your sub-class, for example we could modify the previous section's example ::

    if __name__ == "__main__":
        app = QtGui.QApplication(sys.argv)
        window = MainWindow()
        window.plot.setLogMode(x=True) # use logarithmic x-axis (e.g. for frequency sweeps)
        window.show()
        sys.exit(app.exec_())

See pyqtgraph's API documentation on PlotItem_ for further details.

.. _pyqtgraph: http://www.pyqtgraph.org/
.. _PlotItem: http://www.pyqtgraph.org/documentation/graphicsItems/plotitem.html
