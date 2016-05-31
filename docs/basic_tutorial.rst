Basic tutorial
==============

.. role:: python(code)
    :language: python

This tutorial explains the basics of using Procedures and Results objects to make a quick measurement.

Writing Procedures
~~~~~~~~~~~~~~~~~~
The Procedure object bundles the sequence of steps in an experiment with the parameters required for a its successful execution. This simple structure comes with huge benefits, since a number of convenient tools for making the measurement use this common interface.

Let's start with a simple example of a procedure which loops over a certain number of iterations. We make the SimpleProcedure object as a sub-class of Procedure, since SimpleProcedure *is a* Procedure. ::

    from time import sleep
    from pymeasure.experiment import Procedure
    from pymeasure.experiment import IntegerParameter

    class SimpleProcedure(Procedure):

        # a Parameter that defines the number of loop iterations
        iterations = IntegerParameter('Loop Iterations')

        # a list defining the order and appearance of columns in our data file
        DATA_COLUMNS = ['Iteration']

        def execute(self):
            """ Loops over each iteration and emits the current iteration,
            before waiting for 0.01 sec, and then checking if the procedure
            should stop
            """
            for i in range(self.iterations):
                self.emit('results', {'Iteration': i})
                sleep(0.01)
                if self.should_stop():
                    break

At the top of the SimpleProcedure class we define the required Parameters. In this case, :python:`iterations` is a IntegerParameter that defines the number of loops to perform. Inside our Procedure class we reference the value in the iterations Parameter by the class variable where the Parameter is stored (:python:`self.iterations`). PyMeasure swaps out the Parameters with their values behind the scene, which makes accessing the values of parameters very convenient.

We define the data columns that will be recorded in a list stored in :python:`DATA_COLUMNS`. This sets the order by which columns are stored in the file. In this example, we will store the Iteration number for each loop iteration.

The :python:`execute` methods defines the main body of the procedure. Our example method consists of a loop over the number of iterations, in which we emit the data to be recorded (the Iteration number). The data is broadcast to any number of listeners by using the :code:`emit` method, which takes a topic as the first argument. Data with the :python:`'results'` topic and the proper data columns will be recorded to a file. The sleep function in our example provides two very useful features. The first is to delay the execution of the next lines of code by the time argument in units of seconds. The seconds is that during this delay time, the CPU is free to perform other code. Successful measurements often require the intelligent use of sleep to deal with instrument delays and ensure that the CPU is not hogged by a single script. After our delay, we check to see if the Procedure should stop by calling :python:`self.should_stop()`. By checking this flag, the Procedure will react to a user canceling the procedure execution.

This covers the basic requirements of a Procedure object. Now let's construct our SimpleProcedure object with 100 iterations. ::

    procedure = SimpleProcedure()
    procedure.iterations = 100

Next we will show how to run the procedure.

Running Procedures
~~~~~~~~~~~~~~~~~~
A Procedure is run by a Worker object. The Worker executes the Procedure in a separate process, which has a speed advantage on computers with multiple processors and allows other scripts to execute asynchronously with the procedure (e.g. a graphical user interface). In addition to performing the measurement, the Worker spawns a Recorder object, which listens for the :python:`'results'` topic in data emitted by the Procedure, and writes those lines to a data file. The Results object provides a convenient abstraction to keep track of where the data should be stored, the data in an accessible form, and the Procedure that pertains to those results.

We first construct a Results object for our Procedure. ::
    
    from pymeasure.experiment import Results

    data_filename = 'example.csv'
    results = Results(procedure, data_filename)

Constructing the Results object for our Procedure creates the file using the :python:`data_filename`, and stores the Parameters for the Procedure. This allows the Procedure and Results objects to be reconstructed later simply by loading the file using :python:`Results.load(data_filename)`. The Parameters in the file are easily readable.

We now construct a Worker with the Results object, since it contains our Procedure. ::

    from pymeasure.experiment import Worker

    worker = Worker(results, port=5888)

The Worker publishes data and other run-time information onto the local network over a specific TCP port, 5888 in this case. Other Listener objects can tune in to the published information on that port, which allows our program to communicate across processes and threads easily.

Now we are ready to start the worker. ::

    worker.start()

The Worker process will be launched in a separate process, which allows us to perform other tasks while it is running. When writing a script that should block (wait for the Worker to finish), we need to join the Worker back into the main process. ::

    worker.join(timeout=3600) # wait at most 1 hr (3600 sec)

Let's put all the pieces together. Our SimpleProcedure can be run in a script by the following. ::

    from time import sleep
    from pymeasure.experiment import Procedure, Results, Worker
    from pymeasure.experiment import IntegerParameter

    class SimpleProcedure(Procedure):

        # a Parameter that defines the number of loop iterations
        iterations = IntegerParameter('Loop Iterations')

        # a list defining the order and appearance of columns in our data file
        DATA_COLUMNS = ['Iteration']

        def execute(self):
            """ Loops over each iteration and emits the current iteration,
            before waiting for 0.01 sec, and then checking if the procedure
            should stop
            """
            for i in range(self.iterations):
                self.emit('results', {'Iteration': i})
                sleep(0.01)
                if self.should_stop():
                    break

    if __name__ == "__main__":
        procedure = SimpleProcedure()
        procedure.iterations = 100

        data_filename = 'example.csv'
        results = Results(procedure, data_filename)

        worker = Worker(results, port=5888)
        worker.start()

        worker.join(timeout=3600) # wait at most 1 hr (3600 sec)

Here we have included an if statement to only run the script if the __name__ is __main__. This precaution allows us to import the SimpleProcedure object without running the execution.

Using Logs
~~~~~~~~~~

Logs keep track of important details in the execution of a procedure. We describe the use of the Python logging module with PyMeasure, which makes it easy to document the execution of a procedure and provides useful insight when diagnosing issues or bugs.

Let's extend our SimpleProcedure with logging. ::

    import logging
    log = logging.getLogger(__name__)
    log.addHandler(logging.NullHandler())

    from time import sleep
    from pymeasure.log import console_log
    from pymeasure.experiment import Procedure, Results, Worker
    from pymeasure.experiment import IntegerParameter

    class SimpleProcedure(Procedure):

        iterations = IntegerParameter('Loop Iterations')

        DATA_COLUMNS = ['Iteration']

        def execute(self):
            log.info("Starting the loop of %d iterations" % self.iterations)
            for i in range(self.iterations):
                data = {'Iteration': i}
                self.emit('results', data)
                log.debug("Emitting results: %s" % data)
                sleep(0.01)
                if self.should_stop():
                    log.warning("Caught the stop flag in the procedure")
                    break

    if __name__ == "__main__":
        console_log(log)

        log.info("Constructing a SimpleProcedure")
        procedure = SimpleProcedure()
        procedure.iterations = 100

        data_filename = 'example.csv'
        log.info("Constructing the Results with a data file: %s" % data_filename)
        results = Results(procedure, data_filename)

        port = 5888
        log.info("Constructing the Worker on port: %d" % port)
        worker = Worker(results, port=port)
        worker.start()
        log.info("Started the Worker")

        log.info("Joining with the worker in at most 1 hr")
        worker.join(timeout=3600) # wait at most 1 hr (3600 sec)
        log.info("Finished the measurement")

First, we have imported the Python logging module and grabbed the logger using the __name__ argument. This gives us logging information specific to the current file. Conversely, we could use the '' argument to get all logs, including those of pymeasure. We use the console_log function to conveniently output the log to the console. Further details on how to use the logger are addressed in the Python logging documentation.

Plotting data
~~~~~~~~~~~~~

Plotting data in a graphical interface is easily achieved with the Plotter object. The Plotter takes a Results object and plots the data at a regular interval, grabbing the latest data each time from the file.

Let's extend our SimpleProcedure with a RandomProcedure, which generates random numbers during our loop. ::

    import logging
    log = logging.getLogger(__name__)
    log.addHandler(logging.NullHandler())

    import random
    from time import sleep
    from pymeasure.log import console_log
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

        log.info("Constructing a SimpleProcedure")
        procedure = SimpleProcedure()
        procedure.iterations = 100

        data_filename = 'random.csv'
        log.info("Constructing the Results with a data file: %s" % data_filename)
        results = Results(procedure, data_filename)

        log.info("Constructing the Plotter")
        plotter = Plotter(results)
        plotter.start()
        log.info("Started the Plotter")

        port = 5888
        log.info("Constructing the Worker on port: %d" % port)
        worker = Worker(results, port=port)
        worker.start()
        log.info("Started the Worker")

        log.info("Joining with the worker in at most 1 hr")
        worker.join(timeout=3600) # wait at most 1 hr (3600 sec)
        log.info("Finished the measurement")

The important addition is the construction of the Plotter from the Results object. ::

    plotter = Plotter(results)
    plotter.start()

Just like the Worker, the Plotter is started in a different process so that it can be run on a separate CPU for higher performance. The Plotter launches a Qt graphical interface using pyqtgraph which allows the Results data to be viewed based on the columns in the data.