Version 0.13.1 (2023-10-05)
===========================
New release to fix ineffective python version restriction in the project metadata (only affected Python<=3.7 environments installing via pip).

Version 0.13.0 (2023-09-23)
===========================
Main items of this new release:

- Dropped support for Python 3.7, added support for Python 3.11.
- Adds a test generator, which observes the communication with an actual device and writes protocol tests accordingly.
- 2 new instrument drivers have been added.

Deprecated features
-------------------
- Attocube ANC300: The :code:`stepu` and :code:`stepd` properties are deprecated, use the new :code:`move_raw` method instead. (@dkriegner, #938)

Instruments
-----------
- Adds a test generator (@bmoneke, #882)
- Adds Thyracont Smartline v2 vacuum sensor transmitter (@bmoneke, #940)
- Adds Thyracont Smartline v1 vacuum gauge (@dkriegner, #937)
- AddsTeledyne base classes with most of `LeCroyT3DSO1204` functionality (@RobertoRoos, #951)
- Fixes instrument documentation (@mcdo0486, #941, #903, @omahs, #960)
- Fixes Toptica Ibeamsmart's __init__ (@waveman68, #959)
- Fixes VISAAdapter flush_read_buffer() (@ileu, #968)
- Updates Keithley2306 and AFG3152C to Channels (@bilderbuchi, #953)

GUI
---
- Adds console mode (@msmttchr, #500)
- Fixes Dock widget (@msmttchr, #961)

Miscellaneous
-------------
- Change CI from conda to mamba (@bmoneke, #947)
- Add support for python 3.11 (@CasperSchippers, #896)

New Contributors
----------------
@waveman68, @omahs, @ileu

**Full Changelog**: https://github.com/pymeasure/pymeasure/compare/v0.12.0...v0.13.0


Version 0.12.0 (2023-07-05)
===========================
Main items of this new release:

- A :code:`Channel` base class has been added for easier implementation of instruments with channels.
- 19 new instrument drivers have been added.
- Added tests for some commonalities across all instruments.
- We continue to clean up our API in preparation for a future version 1.0. Deprecations and subsequent removals are listed below.

Deprecated features
-------------------
- HP 34401A: :code:`voltage_ac`, :code:`current_dc`, :code:`current_ac`, :code:`resistance`, :code:`resistance_4w` properties, use :code:`function_` and :code:`reading` properties instead.
- Toptica IBeamSmart: :code:`channel1_enabled`, use :code:`ch_1.enabled` property instead (equivalent for channel2). Also :code:`laser_enabled` is deprecated in favor of :code:`emission` (@bmoneke, #819).
- TelnetAdapter: use :code:`VISAAdapter` instead. VISA supports TCPIP connections. Use the resource_name :code:`TCPIP[board]::<hostname>::<port>::SOCKET` to connect to a server (@Max-Herbold, #835).
- Attocube ANC300: :code:`host` argument, pass a resource string or adapter as :code:`Adapter` passed to :code:`Instrument`. Now communicates through the :code:`VISAAdapter` rather than deprecated :code:`TelnetAdapter`. The initializer now accepts :code:`name` as its second keyword argument so all previous initialization positional arguments (`axisnames`, `passwd`, `query_delay`) should be switched to keyword arguments.
- The property creators :code:`control`, :code:`measurement`, and :code:`setting` do not accept arbitrary keyword arguments anymore. Use the :code:`v_kwargs` parameter for arguments you want to pass on to :code:`values` method, instead.
- The property creators :code:`control`, :code:`measurement`, and :code:`setting` do not accept `command_process` anymore. Use a dynamic property or a `Channel` instead, as appropriate (@bmoneke, #878).
- See also the next section.

New adapter and instrument mechanics
------------------------------------
- All instrument constructors are required to accept a :code:`name` argument.
- Changed: :code:`read_bytes` of all Adapters by default does not stop reading on a termination character, unless the new argument :code:`break_on_termchar` is set to `True`.
- Channel class added. :code:`Instrument.channels` and :code:`Instrument.ch_X` (:code:`X` is any channel name) are reserved attributes for channel mechanics.
- The parameters :code:`check_get_errors` and :code:`check_set_errors` enable calling methods of the same name. This enables more systematically dealing with instruments that acknowledge every "set" command.

- Adds Channel feature to instruments (@bmoneke, mcdo0486, #718, #761, #852, #931)
- Adds :code:`maxsplit` parameter to :code:`values` method (@bmoneke, #793)
- Adds (deprecated) global preprocess reply for backward compatibility (@bmoneke, #876)
- Adds fallback version for discarding the read buffer to VISAAdapter (@dkriegner, #836)
- Adds :code:`flush_read_buffer` to SerialAdapter (@RobertoRoos, #865)
- Adds :code:`gpib_read_timeout` to PrologixAdapter (@neuschs, #927)
- Adds command line option to pass resource address for instrument tests (@bleykauf, #789)
- Adds "find all instruments" and channels for testing (@bmoneke, #909, @mcdo0486, #911, #912)
- Adds test that an instrument hands kwargs to the adapter (@bmoneke, #814)
- Adds property docstring check (@bmoneke, #895)
- Improves property factories' docstrings (@bmoneke, #843)
- Improves property factories: do not allow undefined kwargs (@bmoneke, #856)
- Improves property factories: check_set/get_errors argument to call methods of the same name (@bmoneke, #883)
- Improves :code:`read_bytes` of Adapter (@bmoneke, #839)
- Improves the ProtocolAdapter with a mock connection (@bmoneke, #782), and enable it to have empty messages in the protocol (@bmoneke, #818)
- Improves Prologix adapter documentation (@bmoneke, #813) and configurable settings (@bmoneke, #845)
- Improves behavior of :code:`read_bytes(-1)` for :code:`SerialAdapter` (@RobertoRoos, #866)
- Improves all instruments with name kwarg (@bmoneke, #877)
- Improves VisaAdapter: close manager only when using pyvisa-sim (@dkriegner, #900)
- Harmonises instrument name definition pattern, consistently name the instrument connection argument "adapter" (@bmoneke, #659)
- Fixes ProtocolAdapter has list in signature (@bmoneke, #901)
- Fixes VISAAdapter's :code:`read_bytes` (@bmoneke, #867)
- Fixes query_delay usage in VISAAdapter (@bmoneke, #765)
- Fixes VisaAdapter: close resource manager only when using pyvisa-sim (@dkriegner, #900)

Instruments
-----------
- New Advantest R624X DC Voltage/Current Sources/Monitors (@wichers, #802)
- New AJA International DC sputtering power supply (@dkriegner, #778)
- New Anritus MS2090A (@aruznieto, #787)
- New Anritsu MS4644B (@CasperSchippers, #827)
- New DSP 7225 and new DSPBase instrument (@mcdo0486, #902)
- New HP 8560A / 8561B Spectrum Analyzer (@neuschs, #888)
- New IPG Photonics YAR Amplifier series (@bmoneke, #851)
- New Keysight E36312A power supply (@scandey, #785)
- New Keithley 2200 power supply (@ashokbruno, #806)
- New Lake Shore 211 Temperature Monitor (@mcdo0486, #889)
- New Lake Shore 224 and improves Lakeshore instruments (@samcondon4, #870)
- New MKS Instruments 937B vacuum gauge controller (@dkriegner, @bilderbuchi, #637, #772, #936)
- New Novanta FPU60 laser power supply unit (@bmoneke, #885)
- New TDK Lambda Genesys 80-65 DC and 40-38 DC power supplies (@mcdo0486, 906)
- New Teledyne T3AFG waveform generator instrument (@scandey, #791)
- New Teledyne (LeCroy) T3DSO1204 Oscilloscope (@LastStartDust, #697, @bilderbuchi, #770)
- New T&C Power Conversion RF power supply (@dkriegner, #800)
- New Velleman K8090 relay device (@RobertoRoos, #859)
- Improves Agilent 33500 with the new channel feature (@JCarl-OS, #763, #773)
- Improves HP 3478A with calibration data related functions (@tomverbeure, #777)
- Improves HP 34401A (@CodingMarco, #810)
- Improves the Oxford instruments with the new channel feature (@bmoneke, #844)
- Improves Siglent SPDxxxxX with the new channel feature (@AidenDawn 758)
- Improves Teledyne T3DSO1204 device tests (@LastStarDust, #841)
- Fixes Ametek DSP 7270 lockin amplifier issues (@seb5g, #897)
- Fixes DSP 7265 erroneously using preprocess_reply (@mcdo0486, #873)
- Fixes print statement in DSPBase.sensitivity (@mcdo0486, #915)
- Fixes Fluke bath commands (@bmoneke, #874)
- Fixes a frequency limitation in HP 8657B (@LongnoseRob, #769)
- Fixes Keithley 2600 channel calling parent's shutdown (@mcdo0486, #795)

Automation
----------
- Adds tolerance for opening result files with missing parameters (@msmttchr, #780)
- Validate DATA_COLUMNS entries earlier, avoid exceptions in a running procedure (@mcdo0486, #796, #934)

GUI
---
- Adds docking windows (@mcdo0486, #722, #762)
- Adds save plot settings in addition to dock layout (@mcdo0486, #850)
- Adds log widget colouring and format option (@CasperSchippers, #890)
- Adds table widget (@msmttchr, #771)
- New sequencer architecture: decouples it from the graphical tree, adapts it for further expansions (@msmttchr, #518)
- Moves coordinates label to the pyqtgraph PlotItem (@CasperSchippers, #822)
- Fixes crashing ImageWidget at new measurement (@CasperSchippers, #790)
- Fixes checkboxes not working for groups in inputs-widget (@CasperSchippers, #794)

Miscellaneous
-------------
- Adds a collection of solutions for instrument implementation challenges (@bmoneke, #853, #861)
- Updates Tutorials/Making_a_measurement/ example_codes (@sansanda, #749)

New Contributors
----------------
@JCarl-OS, @aruznieto, @scandey, @tomverbeure, @wichers, @Max-Herbold, @RobertoRoos

**Full Changelog**: https://github.com/pymeasure/pymeasure/compare/v0.11.1...v0.12.0

Version 0.11.1 (2022-12-31)
===========================
Adapter and instrument mechanics
--------------------------------
- Fix broken `PrologixAdapter.gpib`. Due to a bug in `VISAAdapter`, you could not get a second adapter with that connection (#765).

**Full Changelog**: https://github.com/pymeasure/pymeasure/compare/v0.11.0...v0.11.1

Dependency updates
------------------
- Required version of `PyQtGraph <https://www.pyqtgraph.org/>`__ is increased from :code:`pyqtgraph >= 0.9.10` to :code:`pyqtgraph >= 0.12` to support new PyMeasure display widgets.

GUI
---
- Added `ManagedDockWindow <https://pymeasure.readthedocs.io/en/latest/tutorial/graphical.html#using-the-manageddockwindow>`__ to allow multiple dockable plots (@mcdo0486, @CasperSchippers, #722)
- Move coordinates label to the pyqtgraph PlotItem (@CasperSchippers, #822)
- New sequencer architecture (@msmttchr, @CasperSchippers, @mcdo0486, #518)
- Added "Save Dock Layout" functionality to DockWidget context menu. (@mcdo0486, #762)

Version 0.11.0 (2022-11-19)
===========================
Main items of this new release:

- 11 new instrument drivers have been added
- A method for testing instrument communication **without** hardware present has been added, see `the documentation <https://pymeasure.readthedocs.io/en/latest/dev/adding_instruments.html#protocol-tests>`__.
- The separation between :code:`Instrument` and :code:`Adapter` has been improved to make future modifications easier. Adapters now focus on the hardware communication, and the communication *protocol* should be defined in the Instruments. Details in a section below.
- The GUI is now compatible with Qt6.
- We have started to clean up our API in preparation for a future version 1.0. There will be deprecations and subsequent removals, which will be prominently listed in the changelog.

Deprecated features
-------------------
In preparation for a stable 1.0 release and a more consistent API, we have now started formally deprecating some features.
You should get warnings if those features are used.

- Adapter methods :code:`ask`, :code:`values`, :code:`binary_values`, use :code:`Instrument` methods of the same name instead.
- Adapter parameter :code:`preprocess_reply`, override :code:`Instrument.read` instead.
- :code:`Adapter.query_delay` in favor of :code:`Instrument.wait_for()`.
- Keithley 2260B: :code:`enabled` property, use :code:`output_enabled` instead.

New adapter and instrument mechanics
------------------------------------
- Nothing should have changed for users, this section is mainly interesting for instrument implementors.
- Documentation in 'Advanced communication protocols' in 'Adding instruments'.
- Adapter logs written and read messages.
- Particular adapters (`VISAAdapter` etc.) implement the actual communication.
- :code:`Instrument.control` getter calls :code:`Instrument.values`.
- :code:`Instrument.values` calls :code:`Instrument.ask`, which calls :code:`Instrument.write`, :code:`wait_for`, and :code:`read`.
- All protocol quirks of an instrument should be implemented overriding :code:`Instrument.write` and :code:`read`.
- :code:`Instrument.wait_until_read` implements waiting between writing and reading.
- reading/writing binary values is in the :code:`Adapter` class itself.
- :code:`PrologixAdapter` is now based on :code:`VISAAdapter`.
- :code:`SerialAdapter` improved to be more similar to :code:`VISAAdapter`: :code:`read`/:code:`write` use strings, :code:`read/write_bytes` bytes. - Support for termination characters added.

Instruments
-----------
- New Active Technologies AWG-401x (@garzetti, #649)
- New Eurotest hpp_120_256_ieee (@sansanda, #701)
- New HC Photonics crystal ovens TC038, TC038D (@bmoneke, #621, #706)
- New HP 6632A/6633A/6634A power supplies (@LongnoseRob, #651)
- New HP 8657B RF signal generator (@LongnoseRob, #732)
- New Rohde&Schwarz HMP4040 power supply. (@bleykauf, #582)
- New Siglent SPDxxxxX series Power Supplies (@AidenDawn, #719)
- New Temptronic Thermostream devices (@mroeleke, #368)
- New TEXIO PSW-360L30 Power Supply (@LastStarDust, #698)
- New Thermostream ECO-560 (@AidenDawn, #679)
- New Thermotron 3800 Oven (@jcarbelbide, #606)
- Harmonize instruments' adapter argument (@bmoneke, #674)
- Harmonize usage of :code:`shutdown` method (@LongnoseRob, #739)
- Rework Adapter structure (@bmoneke, #660)
- Add Protocol tests without hardware present (@bilderbuchi, #634, @bmoneke, #628, #635)
- Add Instruments and adapter protocol tests for adapter rework (@bmoneke, #665)
- Add SR830 sync filter and reference source trigger (@AsafYagoda, #630)
- Add Keithley6221 phase marker phase and line (@AsafYagoda, #629)
- Add missing docstrings to Keithley 2306 battery simulator (@AidenDawn, #720)
- Fix hcp instruments documentation (@bmoneke, #671)
- Fix HPLegacyInstrument initializer API (@bilderbuchi, #684)
- Fix Fwbell 5080 implementation (@mcdo0486, #714)
- Fix broken documentation example. (@bmoneke, #738)
- Fix typo in Keithley 2600 driver (@mcdo0486, #615)
- Remove dynamic use of docstring from ATS545 and make more generic (@AidenDawn, #685)

Automation
----------
- Add storing unitful experiment results (@bmoneke, #642)
- Add storing conditions in file (@CasperSchippers, #503)

GUI
---
- Add compatibility with Qt 6 (@CasperSchippers, #688)
- Add spinbox functionality for IntegerParameter and FloatParameter (@jarvas24, #656)
- Add "delete data file" button to the browser_item_menu (@jarvas24, #654)
- Split windows.py into a folder with separate modules (@mcdo0486, #593)
- Remove dependency on matplotlib (@msmttchr, #622)
- Remove deprecated access to QtWidgets through QtGui (@maederan201, #695)

Miscellaneous
-------------
- Update and extend documentation (@bilderbuchi, #712, @bmoneke, #655)
- Add PEP517 compatibility & dynamically obtaining a version number (@bilderbuchi, #613)
- Add an example and documentation regarding using a foreign instrument (@bmoneke, #647)
- Add black configuration (@bleykauf, #683)
- Remove VISAAdapter.has_supported_version() as it is not needed anymore.

New Contributors
----------------
@jcarbelbide, @mroeleke, @bmoneke, @garzetti, @AsafYagoda, @AidenDawn, @LastStarDust, @sansanda

**Full Changelog**: https://github.com/pymeasure/pymeasure/compare/v0.10.0...v0.11.0

Version 0.10.0 (2022-04-09)
===========================
Main items of this new release:

- 23 new instrument drivers have been added
- New dynamic Instrument properties can change their parameters at runtime
- Communication settings can now be flexibly defined per protocol
- Python 3.10 support was added and Python 3.6 support was removed.
- Many additions, improvements and have been merged

Instruments
-----------
- New Agilent B1500 Data Formats and Documentation (@moritzj29)
- New Anaheim Automation stepper motor controllers (@samcondon4)
- New Andeen Hagerling capacitance bridges (@dkriegner)
- New Anritsu MS9740A Optical Spectrum Analyzer (@md12g12)
- New BK Precision 9130B Instrument (@dennisfeng2)
- New Edwards nXDS (10i) Vacuum Pump (@hududed)
- New Fluke 7341 temperature bath instrument (@msmttchr)
- New Heidenhain ND287 Position Display Unit Driver (@samcondon4)
- New HP 3478A (@LongnoseRob)
- New HP 8116A 50 MHz Pulse/Function Generator (@CodingMarco)
- New Keithley 2260B DC Power Supply (@bklebel)
- New Keithley 2306 Dual Channel Battery/Charger Simulator (@mfikes)
- New Keithley 2600 SourceMeter series (@Daivesd)
- New Keysight N7776C Swept Laser Source (@maederan201)
- New Lakeshore 421 (@CasperSchippers)
- New Oxford IPS120-10 (@CasperSchippers)
- New Pendulum CNT-91 frequency counter (@bleykauf)
- New Rohde&Schwarz - SFM TV test transmitter (@LongnoseRob)
- New Rohde&Schwarz FSL spectrum analyzer (@bleykauf)
- New SR570 current amplifier driver (@pyMatJ)
- New Stanford Research Systems SR510 instrument driver (@samcondon4)
- New Toptica Smart Laser diode (@dkriegner)
- New Yokogawa GS200 Instrument (@dennisfeng2)
- Add output low grounded property to Keithley 6221 (@CasperSchippers)
- Add shutdown function for Keithley 2260B (@bklebel)
- Add phase control for Agilent 33500 (@corna)
- Add assigning "ONCE" to auto_zero to Keithley 2400 (@mfikes)
- Add line frequency controls to Keithley 2400 (@mfikes)
- Add LIA and ERR status byte read properties to the SRS Sr830 driver (@samcondon4)
- Add all commands to Oxford Intelligent Temperature Controller 503 (@CasperSchippers)
- Fix DSP 7265 lockin amplifier (@CasperSchippers)
- Fix bug in Keithley 6517B Electrometer (@CasperSchippers)
- Fix Keithley2000 deprecated call to visa.config (@bklebel)
- Fix bug in the Keithley 2700 (@CasperSchippers)
- Fix setting of sensor flags for Thorlabs PM100D (@bleykauf)
- Fix SCPI used for Keithley 2400 voltage NPLC (@mfikes)
- Fix missing return statements in Tektronix AFG3152C (@bleykauf)
- Fix DPSeriesMotorController bug (@samcondon4)
- Fix Keithley2600 error when retrieving error code (@bicarlsen)
- Fix Attocube ANC300 with new SCPI Instrument properties (@dkriegner)
- Fix bug in wait_for_trigger of Agilent33220A (neal-kepler)

GUI
---
- Add time-estimator widget (@CasperSchippers)
- Add management of progress bar (@msmttchr)
- Remove broken errorbar feature (@CasperSchippers)
- Change of pen width for pyqtgraph (@maederan201)
- Make linewidth changeable (@CasperSchippers)
- Generalise warning in plotter section (@CasperSchippers)
- Implement visibility groups in InputsWidgets (@CasperSchippers)
- Modify navigation of ManagedWindow directory widget (@jarvas24)
- Improve Placeholder logic (@CasperSchippers)
- Breakout widgets into separate modules (@mcdo0486)
- Fix setSizePolicy bug with PySide2 (@msmttchr)
- Fix managed window (@msmttchr)
- Fix ListParameter for numbers (@moritzj29)
- Fix incorrect columns on showing data (@CasperSchippers)
- Fix procedure property issue (@msmttchr)
- Fix pyside2 (@msmttchr)

Miscellaneous
-------------
- Improve SCPI property support (@msmttchr)
- Remove broken safeKeyword management (@msmttchr)
- Add dynamic property support (@msmttchr)
- Add flexible API for defining connection configuration (@bilderbuchi)
- Add write_binary_values() to SerialAdapter (@msmttchr)
- Change an outdated pyvisa ask() to query() (@LongnoseRob)
- Fix ZMQ bug (@bilderbuchi)

- Documentation for passing tuples to control property (@bklebel)
- Documentation bugfix (@CasperSchippers)
- Fixed broken links in documentation. (@samcondon4)
- Updated widget documentation (@mcdo0486)
- Fix typo SCIP->SCPI (@mfikes)

- Remove Python 3.6, add Python 3.10 testing (@bilderbuchi)
- Modernise the code base to use Python 3.7 features (@bilderbuchi)
- Added image data generation to Mock Instrument class (@samcondon4)
- Add autodoc warnings to the problem matcher (@bilderbuchi)
- Update CI & annotations (@bilderbuchi)
- Test workers (@mcdo0486)
- Change copyright date to 2022 (@LongnoseRob)
- Removed unused code (@msmttchr)

New Contributors
----------------
@LongnoseRob, @neal, @hududed, @corna, @Daivesd, @samcondon4, @maederan201, @bleykauf, @mfikes, @bicarlsen, @md12g12, @CodingMarco, @jarvas24, @mcdo0486!

**Full Changelog**: https://github.com/pymeasure/pymeasure/compare/v0.9...v0.10.0

Version 0.9 -- released 2/7/21
==============================
- PyMeasure is now officially at github.com/pymeasure/pymeasure
- Python 3.9 is now supported, Python 3.5 removed due to EOL
- Move to GitHub Actions from TravisCI and Appveyor for CI (@bilderbuchi)
- New additions to Oxford Instruments ITC 503 (@CasperSchippers)
- New Agilent 34450A and Keysight DSOX1102G instruments (@theMashUp, @jlarochelle)
- Improvements to NI VirtualBench (@moritzj29)
- New Agilent B1500 instrument (@moritzj29)
- New Keithley 6517B instrument (@wehlgrundspitze)
- Major improvements to PyVISA compatbility (@bilderbuchi, @msmttchr, @CasperSchippers, @cjermain)
- New Anapico APSIN12G instrument (@StePhanino)
- Improvements to Thorelabs Pro 8000 and SR830 (@Mike-HubGit)
- New SR860 instrument (@StevenSiegl, @bklebel)
- Fix to escape sequences (@tirkarthi)
- New directory input for ManagedWindow (@paulgoulain)
- New TelnetAdapter and Attocube ANC300 Piezo controller (@dkriegner)
- New Agilent 34450A (@theMashUp)
- New Razorbill RP100 strain cell controller (@pheowl)
- Fixes to precision and default value of ScientificInput and FloatParameter (@moritzj29)
- Fixes for Keithly 2400 and 2450 controls (@pyMatJ)
- Improvments to Inputs and open_file_externally (@msmttchr)
- Fixes to Agilent 8722ES (@alexmcnabb)
- Fixes to QThread cleanup (@neal-kepler, @msmttchr)
- Fixes to Keyboard interrupt, and parameters (@CasperSchippers)

Version 0.8 -- released 3/29/19
===============================
- Python 3.8 is now supported
- New Measurement Sequencer allows for running over a large parameter space (@CasperSchippers)
- New image plotting feature for live image measurements (@jmittelstaedt)
- Improvements to VISA adapter (@moritzj29)
- Added Tektronix AFG 3000, Keithley 2750 (@StePhanino, @dennisfeng2)
- Documentation improvements (@mivade)
- Fix to ScientificInput for float strings (@moritzj29)
- New validator: strict_discrete_range (@moritzj29)
- Improvements to Recorder thread joining
- Migrating the ReadtheDocs configuration to version 2
- National Instruments Virtual Bench initial support (@moritzj29)

Version 0.7 -- released 8/4/19
==============================
- Dropped support for Python 3.4, adding support for Python 3.7
- Significant improvements to CI, dependencies, and conda environment (@bilderbuchi, @cjermain)
- Fix for PyQT issue in ResultsDialog (@CasperSchippers)
- Fix for wire validator in Keithley 2400 (@Fattotora)
- Addition of source_enabled control for Keithley 2400 (@dennisfeng2)
- Time constant fix and input controls for SR830 (@dennisfeng2)
- Added Keithley 2450 and Agilent 33521A (@hlgirard, @Endever42)
- Proper escaping support in CSV headers (@feph)
- Minor updates (@dvase)

Version 0.6.1 -- released 4/21/19
=================================
- Added Elektronica SM70-45D, Agilent 33220A, and Keysight N5767A instruments
  (@CasperSchippers, @sumatrae)
- Fixes for Prologix adapter and Keithley 2400 (@hlgirard, @ronan-sensome)
- Improved support for SRS SR830 (@CasperSchippers)

Version 0.6 -- released 1/14/19
===============================
- New VXI11 Adapter for ethernet instruments (@chweiser)
- PyQt updates to 5.6.0
- Added SRS SG380, Ametek 7270, Agilent 4156, HP 34401A, Advantest R3767CG, and
  Oxford ITC503 instrustruments (@sylkar, @jmittelstaedt, @vik-s, @troylf, @CasperSchippers)
- Updates to Keithley 2000, Agilent 8257D, ESP 300, and Keithley 2400 instruments
  (@watersjason, @jmittelstaedt, @nup002)
- Various minor bug fixes (@thosou)

Version 0.5.1 -- released 4/14/18
=================================
- Minor versions of PyVISA are now properly handled
- Documentation improvements (@Laogeodritt and @ederag)
- Instruments now have :code:`set_process` capability (@bilderbuchi)
- Plotter now uses threads (@dvspirito)
- Display inputs and PlotItem improvements (@Laogeodritt)

Version 0.5 -- released 10/18/17
================================
- Threads are used by default, eliminating multiprocessing issues with spawn
- Enhanced unit tests for threading
- Sphinx Doctests are added to the documentation (@bilderbuchi)
- Improvements to documentation (@JuMaD)

Version 0.4.6 -- released 8/12/17
=================================
- Reverted multiprocessing start method keyword arguments to fix Unix spawn issues (@ndr37)
- Fixes to regressions in Results writing (@feinsteinben)
- Fixes to TCP support using cloudpickle (@feinsteinben)
- Restructing of unit test framework

Version 0.4.5 -- released 7/4/17
================================
- Recorder and Scribe now leverage QueueListener (@feinsteinben)
- PrologixAdapter and SerialAdapter now handle Serial objects as adapters (@feinsteinben)
- Optional TCP support now uses cloudpickle for serialization (@feinsteinben)
- Significant PEP8 review and bug fixes (@feinsteinben)
- Includes docs in the code distribution (@ghisvail)
- Continuous integration support for Python 3.6 (@feinsteinben)

Version 0.4.4 -- released 6/4/17
================================
- Fix pip install for non-wheel builds
- Update to Agilent E4980 (@dvspirito)
- Minor fixes for docs, tests, and formatting (@ghisvail, @feinsteinben)

Version 0.4.3 -- released 3/30/17
=================================
- Added Agilent E4980, AMI 430, Agilent 34410A, Thorlabs PM100, and
  Anritsu MS9710C instruments (@TvBMcMaster, @dvspirito, and @mhdg)
- Updates to PyVISA support (@minhhaiphys)
- Initial work on resource manager (@dvspirito)
- Fixes for Prologix adapter that allow read-write delays (@TvBMcMaster)
- Fixes for conda environment on continuous integration

Version 0.4.2 -- released 8/23/16
=================================
- New instructions for installing with Anaconda and conda-forge package (thanks @melund!)
- Bug-fixes to the Keithley 2000, SR830, and Agilent E4408B
- Re-introduced the Newport ESP300 motion controller
- Major update to the Keithely 2400, 2000 and Yokogawa 7651 to achieve a common interface
- New command-string processing hooks for Instrument property functions
- Updated LakeShore 331 temperature controller with new features
- Updates to the Agilent 8257D signal generator for better feature exposure

Version 0.4.1 -- released 7/31/16
=================================
- Critical fix in setup.py for importing instruments (also added to documentation)

Version 0.4 -- released 7/29/16
===============================
- Replaced Instrument add_measurement and add_control with measurement and control functions
- Added validators to allow Instrument.control to match restricted ranges
- Added mapping to Instrument.control to allow more flexible inputs
- Conda is now used to set up the Python environment
- macOS testing in continuous integration
- Major updates to the documentation

Version 0.3 -- released 4/8/16
==============================
- Added IPython (Jupyter) notebook support with significant features
- Updated set of example scripts and notebooks
- New PyMeasure logo released
- Removed support for Python <3.4
- Changed multiprocessing to use spawn for compatibility
- Significant work on the documentation
- Added initial tests for non-instrument code
- Continuous integration setup for Linux and Windows

Version 0.2 -- released 12/16/15
================================
- Python 3 compatibility, removed support for Python 2
- Considerable renaming for better PEP8 compliance
- Added MIT License
- Major restructuring of the package to break it into smaller modules
- Major rewrite of display functionality, introducing new Qt objects for easy extensions
- Major rewrite of procedure execution, now using a Worker process which takes advantage of multi-core CPUs
- Addition of a number of examples
- New methods for listening to Procedures, introducing ZMQ for TCP connectivity
- Updates to Keithley2400 and VISAAdapter

Version 0.1.6 -- released 4/19/15
=================================
- Renamed the package to PyMeasure from Automate to be more descriptive about its purpose
- Addition of VectorParameter to allow vectors to be input for Procedures
- Minor fixes for the Results and Danfysik8500

Version 0.1.5 -- release 10/22/14
=================================
- New Manager class for handling Procedures in a queue fashion
- New Browser that works in tandem with the Manager to display the queue
- Bug fixes for Results loading

Version 0.1.4 -- released 8/2/14
================================
- Integrated Results class into display and file writing
- Bug fixes for Listener classes
- Bug fixes for SR830

Version 0.1.3 -- released 7/20/14
=================================
- Replaced logging system with Python logging package
- Added data management (Results) and bug fixes for Procedures and Parameters
- Added pandas v0.14 to requirements for data management
- Added data listeners, Qt4 and PyQtGraph helpers

Version 0.1.2 -- released 7/18/14
=================================
- Bug fixes to LakeShore 425
- Added new Procedure and Parameter classes for generic experiments
- Added version number in package

Version 0.1.1 -- released 7/16/14
=================================
- Bug fixes to PrologixAdapter, VISAAdapter, Agilent 8722ES, Agilent 8257D, Stanford SR830, Danfysik8500
- Added Tektronix TDS 2000 with basic functionality
- Fixed Danfysik communication to handle errors properly

Version 0.1.0 -- released 7/15/14
=================================
- Initial release
