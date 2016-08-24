# Examples

There are a number of examples for learning how to use PyMeasure. Many of them make a great starting point for your own graphical user interface (GUI) or command line script.

Run one of the examples in the command line (or "Anaconda prompt").

```bash
python gui.py
```

## Basic

The following examples simulate data using a random number generator, so they do not require an instrument to be connected. They show off the basic structure for setting up your measurement.

1. [gui.py](Basic/gui.py) - A graphical user interface example with live-plotting and full features.
2. [script_plotter.py](Basic/script.py) - A command line example, which also has a live-plot.
3. [script.py](Basic/script.py) - A simple command line example.
4. [gui_custom_inputs.py](Basic/gui_custom_inputs.py) - An extension of [gui.py](Basic/gui.py), which uses a [custom Qt Creator file](Basic/gui_custom_inputs.ui) for the inputs.

Notice in all of these examples, the Procedure class is the same. Once you define your Procedure, the choice of interface is up to you.

## Current-Voltage Measurements

There are two examples of for measuring current-voltage (IV) characteristics, which use different instruments to make the measurement. They are based on [gui.py](Basic/gui.py).

1. [iv_yokogawa.py](Current-Voltage Measurements/iv_yokogawa.py) - Uses the Yokogawa 7651 Programmable Source to provide a current and measures the voltage with a Keithley 2000 Multimeter.
2. [iv_keithley.py](Current-Voltage Measurements/iv_keithley.py) - Uses the Keithley 2400 SourceMeter to provide a current and measures the voltage with a Keithley 2000 Multimeter. This has higher precision in the voltage than using the SourceMeter allow.

## Notebook Experiments

Besides the interfaces shown in the [Basic examples](#basic), you can also make measurements in Jupyter notebooks. It is recommended that you use caution when using this technique, as the notebooks allow scripts to be executed out of order and they do not provide the same level of performance as the standard interfaces. Despite these caveats, the notebooks can be a flexible method for running custom experiments, where the Procedure needs to be modified often.

1. [script.ipynb](Notebook Experiments/script.ipynb) - Runs the simulated random number Procedure from [gui.py](Basic/gui.py) in a notebook.
2. [script2.ipynb](Notebook Experiments/script2.ipynb) - Extends [script.ipynb](Notebook Experiments/script.ipynb), using custom configurations and Measureable parameters.
