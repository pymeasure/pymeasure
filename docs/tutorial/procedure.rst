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
3) Set source_current and measure_voltage parameters
4) Connect to the Keithley 2400
5) Set up the instrument for the IV characteristic
6) Allocate arrays to store the resulting measurements
7) Loop through the current points, measure the voltage, and record
8) Save the final data to a CSV file
9) Shutdown the instrument

These steps are expressed in code as follows. ::

    # Import necessary packages
    from pymeasure.instruments.keithley import Keithley2400
    import numpy as np
    import pandas as pd
    from time import sleep

    # Set the input parameters
    data_points = 50
    averages = 10
    max_current = 0.001
    min_current = -max_current

    # Set source_current and measure_voltage parameters
    current_range = 10e-3  # in Amps
    compliance_voltage = 10  # in Volts
    measure_nplc = 0.1  # Number of power line cycles
    voltage_range = 1  # in VOlts

    # Connect and configure the instrument
    sourcemeter = Keithley2400("GPIB::24")
    sourcemeter.reset()
    sourcemeter.use_front_terminals()
    sourcemeter.apply_current(current_range, compliance_voltage)
    sourcemeter.measure_voltage(measure_nplc, voltage_range)
    sleep(0.1)  # wait here to give the instrument time to react
    sourcemeter.stop_buffer()
    sourcemeter.disable_buffer()

    # Allocate arrays to store the measurement results
    currents = np.linspace(min_current, max_current, num=data_points)
    voltages = np.zeros_like(currents)
    voltage_stds = np.zeros_like(currents)

    sourcemeter.enable_source()

    # Loop through each current point, measure and record the voltage
    for i in range(data_points):
        sourcemeter.config_buffer(averages)
        sourcemeter.source_current = currents[i]
        sourcemeter.start_buffer()
        sourcemeter.wait_for_buffer()
        # Record the average and standard deviation
        voltages[i] = sourcemeter.means[0]
        sleep(1.0)
        voltage_stds[i] = sourcemeter.standard_devs[0]

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
            """Execute the procedure.

            Loops over each iteration and emits the current iteration,
            before waiting for 0.01 sec, and then checking if the procedure
            should stop.
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
            """Execute the procedure.

            Loops over each iteration and emits the current iteration,
            before waiting for 0.01 sec, and then checking if the procedure
            should stop.
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


Storing metadata
~~~~~~~~~~~~~~~~

Metadata (:class:`pymeasure.experiment.parameters.Metadata`) allows storing information (e.g. the actual starting time, instrument parameters) about the measurement in the header of the datafile.
These Metadata objects are evaluated and stored in the datafile only after the :python:`startup` method has run; this way it is possible to e.g. retrieve settings from an instrument and store them in the file.
Using a Metadata is nearly as straightforward as using a Parameter; extending the example of above to include metadata, looks as follows: ::

    from time import sleep, time
    from pymeasure.experiment import Procedure
    from pymeasure.experiment import IntegerParameter, Metadata

    class SimpleProcedure(Procedure):

        # a Parameter that defines the number of loop iterations
        iterations = IntegerParameter('Loop Iterations')

        # the Metadata objects store information after the startup has ran
        starttime = Metadata('Start time', fget=time)
        custom_metadata = Metadata('Custom', default=1)

        # a list defining the order and appearance of columns in our data file
        DATA_COLUMNS = ['Iteration']

        def startup(self):
            self.custom_metadata = 20

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


As with a Parameter, PyMeasure swaps out the Metadata with their values behind the scene, which makes accessing the values of Metadata very convenient.

The value of a Metadata can be set either using an :python:`fget` method or manually in the startup method.
The :python:`fget` method, if provided, is run after startup method.
It can also be provided as a string; in that case it is assumed that the string contains the name of an attribute (either a callable or not) of the Procedure class which returns the value that is to be stored.
This also allows to retrieve nested attributes (e.g. in order to store a property or method of an instrument) by separating the attributes with a period: e.g. `instrument_name.attribute_name` (or even `instrument_name.subclass_name.attribute_name`); note that here only the final element (i.e. `attribute_name` in the example) is allowed to refer to a callable.
If neither an :python:`fget` method is provided or a value manually set, the Metadata will return to its default value, if set.
The formatting of the value of the Metadata-object can be controlled using the `fmt` argument.


Modifying our script
~~~~~~~~~~~~~~~~~~~~

Now that you have a background on how to use the different features of the Procedure class, and how they are run, we will revisit our IV characteristic measurement using Procedures. Below we present the modified version of our example script, now as a IVProcedure class. ::

    # Import necessary packages
    from pymeasure.instruments.keithley import Keithley2400
    from pymeasure.experiment import Procedure, Results, Worker
    from pymeasure.experiment import IntegerParameter, FloatParameter
    from time import sleep
    import numpy as np

    from pymeasure.log import log, console_log

    class IVProcedure(Procedure):

        data_points = IntegerParameter('Data points', default=20)
        averages = IntegerParameter('Averages', default=8)
        max_current = FloatParameter('Maximum Current', units='A', default=0.001)
        min_current = FloatParameter('Minimum Current', units='A', default=-0.001)

        DATA_COLUMNS = ['Current (A)', 'Voltage (V)', 'Voltage Std (V)']

        def startup(self):
            log.info("Connecting and configuring the instrument")
            self.sourcemeter = Keithley2400("GPIB::24")
            self.sourcemeter.reset()
            self.sourcemeter.use_front_terminals()
            self.sourcemeter.apply_current(100e-3, 10.0)  # current_range = 100e-3, compliance_voltage = 10.0
            self.sourcemeter.measure_voltage(0.01, 1.0)  # nplc = 0.01, voltage_range = 1.0
            sleep(0.1)  # wait here to give the instrument time to react
            self.sourcemeter.stop_buffer()
            self.sourcemeter.disable_buffer()

        def execute(self):
            currents = np.linspace(
                self.min_current,
                self.max_current,
                num=self.data_points
            )
            self.sourcemeter.enable_source()
            # Loop through each current point, measure and record the voltage
            for current in currents:
                self.sourcemeter.config_buffer(IVProcedure.averages.value)
                log.info("Setting the current to %g A" % current)
                self.sourcemeter.source_current = current
                self.sourcemeter.start_buffer()
                log.info("Waiting for the buffer to fill with measurements")
                self.sourcemeter.wait_for_buffer()
                data = {
                    'Current (A)': current,
                    'Voltage (V)': self.sourcemeter.means[0],
                    'Voltage Std (V)': self.sourcemeter.standard_devs[0]
                }
                self.emit('results', data)
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
        procedure.data_points = 20
        procedure.averages = 8
        procedure.max_current = -0.001
        procedure.min_current = 0.001

        data_filename = 'example.csv'
        log.info("Constructing the Results with a data file: %s" % data_filename)
        results = Results(procedure, data_filename)

        log.info("Constructing the Worker")
        worker = Worker(results)
        worker.start()
        log.info("Started the Worker")

        log.info("Joining with the worker in at most 1 hr")
        worker.join(timeout=3600)  # wait at most 1 hr (3600 sec)
        log.info("Finished the measurement")

The parentheses in the :code:`COLUMN` entries indicate the physical unit of the data in the corresponding column, e.g. :code:`'Voltage Std (V)'` indicates Volts. If you want to indicate a dimensionless value, e.g. Mach number, you can use `(1)` instead. Combined units like `(m/s)` or the long form `(meter/second)` are also possible. The class :class:`Results` ensures, that the data is stored in the correct unit, here Volts. For example a :python:`pint.Quantity` of 500 mV will be stored as 0.5 V. A string will be converted first to a `Quantity` and a mere number (e.g. float, int, ...) is assumed to be already in the right unit (e.g 5 will be stored as 5 V).
If the data entry is not compatible, either because it has the wrong unit, e.g. meters which is not a unit of voltage, or because it is no number at all, a warning is logged and `'nan'` will be stored in the file.
If you do not specify a unit (i.e. no parentheses), no unit check is performed for this column, unless the data entry is a `Quantity` for that column. In this case, this column's unit is set to the base unit (e.g. meter if unit of the data entry is kilometers) of the data entry. From this point on, unit checks are enabled for this column. Also use columns without unit checks (i.e. without parentheses) for strings or booleans.


At this point, you are familiar with how to construct a Procedure sub-class. The next section shows how to put these procedures to work in a graphical environment, where will have live-plotting of the data and the ability to easily queue up a number of experiments in sequence. All of these features come from using the Procedure object.
