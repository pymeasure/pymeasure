####################
Making a measurement
####################

.. role:: python(code)
    :language: python

This tutorial will walk you through using PyMeasure to acquire a current-voltage (IV) characteristic using a Keithley 2400. Even if you don't have access to this instrument, this tutorial will explain the method for making measurements with PyMeasure. First we describe using a simple script to make the measurement. From there, we show how :mod:`Procedure <pymeasure.experiment.procedure>` objects greatly simplify the workflow, which leads to making the measurement with a graphical interface. 

Using scripts
=============

Scripts are a quick way to get up and running with a measurement in PyMeasure. For our IV characteristic measurement, we perform the following steps:

1) Import the necessary packages
2) Set the input parameters to define the measurement
3) Connect to the Keithley 2400
4) Set up the instrument for the IV characteristic
5) Allocate arrays to store the resulting measurements
6) Loop through the current points, measure the voltage, and record
7) Save the final data to a CSV file
8) Shutdown the instrument

These steps are expressed in code as follows. ::

    # Import necessary packages
    from pymeasure.instruments.keithley import Keithley2400
    import numpy as np
    import pandas as pd
    from time import sleep

    # Set the input parameters
    data_points = 50
    averages = 50
    max_current = 0.01
    min_current = -max_current

    # Connect and configure the instrument
    sourcemeter = Keithley2400("GPIB::4")
    sourcemeter.reset()
    sourcemeter.use_front_terminals()
    sourcemeter.measure_voltage()
    sourcemeter.config_current_source()
    sleep(0.1) # wait here to give the instrument time to react
    sourcemeter.set_buffer(averages)

    # Allocate arrays to store the measurement results
    currents = np.linspace(min_current, max_current, num=data_points)
    voltages = np.zeros_like(currents)
    voltage_stds = np.zeros_like(currents)

    # Loop through each current point, measure and record the voltage
    for i in range(data_points):
        sourcemeter.current = currents[i]
        sourcemeter.reset_buffer()
        sleep(0.1)
        sourcemeter.start_buffer()
        sourcemeter.wait_for_buffer()

        # Record the average and standard deviation
        voltages[i] = sourcemeter.means
        voltage_stds[i] = sourcemeter.standard_devs

    # Save the data columns in a CSV file
    data = pd.DataFrame({
        'Current (A)': currents,
        'Voltage (V)': voltages,
        'Voltage Std (V)': voltage_stds,
    })
    data.to_csv('example.csv')

    sourcemeter.shutdown()

Running this example script will execute the measurement and save the data to a CSV file. While this may be sufficient for very basic measurements, this example illustrates a number of issues that PyMeasure solves. The issues with the script example include:

* The progress of the measurement is not transparent
* Input parameters are not associated with the data that is saved
* Data is not plotted during the execution (nor at all in this case)
* Data is only saved upon successful completion, which is otherwise lost
* Canceling a running measurement causes the system to end in a undetermined state
* Exceptions also end the system in an undetermined state

The :class:`Procedure <pymeasure.experiment.procedure.Procedure>` class allows us to solve all of these issues. The next section introduces the :class:`Procedure <pymeasure.experiment.procedure.Procedure>` class and shows how to modify our script example to take advantage of these features.


Using Procedures
================
The Procedure object bundles the sequence of steps in an experiment with the parameters required for its successful execution. This simple structure comes with huge benefits, since a number of convenient tools for making the measurement use this common interface.

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
A Procedure is run by a Worker object. The Worker executes the Procedure in a separate Python thread, which allows other code to execute in parallel to the procedure (e.g. a graphical user interface). In addition to performing the measurement, the Worker spawns a Recorder object, which listens for the :python:`'results'` topic in data emitted by the Procedure, and writes those lines to a data file. The Results object provides a convenient abstraction to keep track of where the data should be stored, the data in an accessible form, and the Procedure that pertains to those results.

We first construct a Results object for our Procedure. ::
    
    from pymeasure.experiment import Results

    data_filename = 'example.csv'
    results = Results(procedure, data_filename)

Constructing the Results object for our Procedure creates the file using the :python:`data_filename`, and stores the Parameters for the Procedure. This allows the Procedure and Results objects to be reconstructed later simply by loading the file using :python:`Results.load(data_filename)`. The Parameters in the file are easily readable.

We now construct a Worker with the Results object, since it contains our Procedure. ::

    from pymeasure.experiment import Worker

    worker = Worker(results)

The Worker publishes data and other run-time information through specific queues, but can also publish this information over the local network on a specific TCP port (using the optional :python:`port` argument. Using TCP communication allows great flexibility for sharing information with Listener objects. Queues are used as the standard communication method because they preserve the data order, which is of critical importance to storing data accurately and reacting to the measurement status in order.

Now we are ready to start the worker. ::

    worker.start()

This method starts the worker in a separate Python thread, which allows us to perform other tasks while it is running. When writing a script that should block (wait for the Worker to finish), we need to join the Worker back into the main thread. ::

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

        worker = Worker(results)
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

        log.info("Constructing the Worker")
        worker = Worker(results)
        worker.start()
        log.info("Started the Worker")

        log.info("Joining with the worker in at most 1 hr")
        worker.join(timeout=3600) # wait at most 1 hr (3600 sec)
        log.info("Finished the measurement")

First, we have imported the Python logging module and grabbed the logger using the :python:`__name__` argument. This gives us logging information specific to the current file. Conversely, we could use the :python:`''` argument to get all logs, including those of pymeasure. We use the :python:`console_log` function to conveniently output the log to the console. Further details on how to use the logger are addressed in the Python logging documentation.


Modifying our script
~~~~~~~~~~~~~~~~~~~~

Now that you have a background on how to use the different features of the Procedure class, and how they are run, we will revisit our IV characteristic measurement using Procedures. Below we present the modified version of our example script, now as a IVProcedure class. ::

    # Import necessary packages
    from pymeasure.instruments.keithley import Keithley2400
    from pymeasure.experiment import Procedure
    from pymeasure.experiment import IntegerParameter, FloatParameter
    from time import sleep

    class IVProcedure(Procedure):

        data_points = IntegerParameter('Data points', default=50)
        averages = IntegerParameter('Averages', default=50)
        max_current = FloatParameter('Maximum Current', unit='A', default=0.01)
        min_current = FloatParameter('Minimum Current', unit='A', default=-0.01)

        DATA_COLUMNS = ['Current (A)', 'Voltage (V)', 'Voltage Std (V)']

        def startup(self):
            log.info("Connecting and configuring the instrument")
            self.sourcemeter = Keithley2400("GPIB::4")
            self.sourcemeter.reset()
            self.sourcemeter.use_front_terminals()
            self.sourcemeter.measure_voltage()
            self.sourcemeter.config_current_source()
            sleep(0.1) # wait here to give the instrument time to react
            self.sourcemeter.set_buffer(averages)

        def execute(self):
            currents = np.linspace(
                self.min_current, 
                self.max_current,
                num=self.data_points
            )

            # Loop through each current point, measure and record the voltage
            for current in currents:
                log.info("Setting the current to %g A" % current)
                self.sourcemeter.current = current
                self.sourcemeter.reset_buffer()
                sleep(0.1)
                self.sourcemeter.start_buffer()
                log.info("Waiting for the buffer to fill with measurements")
                self.sourcemeter.wait_for_buffer()

                self.emit('results', {
                    'Current (A)': current,
                    'Voltage (V)': self.sourcemeter.means,
                    'Voltage Std (V)': self.sourcemeter.standard_devs
                })
                sleep(0.01)
                if self.should_stop():
                    log.info("User aborted the procedure")
                    break

        def shutdown(self):
            self.sourcemeter.shutdown()
            log.info("Finished measuring")

    if __name__ == "__main__":
        console_log(log)

        log.info("Constructing an IVProcedure")
        procedure = IVProcedure()
        procedure.data_points = 100
        procedure.averages = 50
        procedure.max_current = -0.01
        procedure.min_current = 0.01

        data_filename = 'example.csv'
        log.info("Constructing the Results with a data file: %s" % data_filename)
        results = Results(procedure, data_filename)

        log.info("Constructing the Worker")
        worker = Worker(results)
        worker.start()
        log.info("Started the Worker")

        log.info("Joining with the worker in at most 1 hr")
        worker.join(timeout=3600) # wait at most 1 hr (3600 sec)
        log.info("Finished the measurement")

At this point, you are familiar with how to construct a Procedure sub-class. The next section shows how to put these procedures to work in a graphical environment, where will have live-plotting of the data and the ability to easily queue up a number of experiments in sequence. All of these features come from using the Procedure object.
