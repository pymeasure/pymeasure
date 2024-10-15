##################
MSO44 Oscilloscope
##################

.. autoclass:: pymeasure.instruments.tektronix.MSO44
    :members:
    :show-inheritance:

Waveform plotting
=================

This code shows how you can retrieve waveform data from multiple channels simultaneously and plot them using Matplotlib.

.. code-block:: python

    import matplotlib.pyplot as plt
    import numpy as np
    from pymeasure.instruments.tektronix.mso44 import MSO44, MeasurementType

    scope = MSO44(<Connection Name>)

    # Get waveforms from multiple channels simultaneously
    channels = ["CH1", "CH2", "CH3", "CH4"]  # Adjust based on available channels
    sources, encoding, preamble, data = scope.get_waveforms(channels, width=2)

    # Process the waveform data
    waveforms = scope.process_waveforms(sources, encoding, preamble, data)

    # Create the plot
    plt.figure(figsize=(12, 8))

    # Color cycle for different channels
    colors = ['y', 'c', 'r', 'g']

    for i, (source, waveform) in enumerate(waveforms.items()):
        plt.plot(waveform['times'], waveform['voltages'], color=colors[i % len(colors)], label=source)

    # Add labels and title
    plt.title('Simultaneously Captured Oscilloscope Waveforms')
    plt.xlabel('Time (s)')
    plt.ylabel('Voltage (V)')
    plt.grid(True)
    plt.legend()

    # Add some margins to the x and y axes
    plt.margins(x=0.01, y=0.1)

    # Show the plot
    plt.show()

    # Access individual channel data
    ch1_data = waveforms['CH1']
    ch2_data = waveforms['CH2']

    print(f"CH1 time array shape: {ch1_data['times'].shape}")
    print(f"CH1 voltage array shape: {ch1_data['voltages'].shape}")
    print(f"CH2 time array shape: {ch2_data['times'].shape}")
    print(f"CH2 voltage array shape: {ch2_data['voltages'].shape}")

    # You can now use these arrays for further processing
    # For example, to get the maximum voltage of CH1:
    ch1_max_voltage = np.max(ch1_data['voltages'])
    print(f"CH1 maximum voltage: {ch1_max_voltage} V")
