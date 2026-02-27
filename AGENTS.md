# AGENTS.md

This file provides guidance to agents when working with code in this repository.

## Project Stack

- Language: Python 3.9+
- Build system: setuptools with setuptools_scm
- Package manager: pip
- Dependencies: numpy, pandas, pint, pyvisa, pyserial, pyqtgraph, qtpy
- Testing: pytest with pytest-qt, pytest-cov, pyvisa-sim

## Build/Lint/Test Commands

- Install in development mode: `pip install -e .`
- Run tests: `python -m pytest` or `pytest`
- Run tests with coverage: `python -m pytest --cov=pymeasure`
- Lint with flake8: `flake8` (max-line-length=100, max-complexity=15)
- Format with black: `black .` (line-length=100)
- Sort imports with isort: `isort .`
- Run single test: `python -m pytest tests/test_file.py::test_function`

## Code Style Guidelines

- Line length: 100 characters (flake8, black, ruff)
- Physical units are handled with Pint library
- Comments are only used to describe non-obvious reasons (why)
- Follow PEP8 style guide and PEP257 docstring conventions
- Function and variable names should be lower case with underscores as needed to separate words
- CamelCase should only be used for class names, unless working with Qt, where its use is common
- It is allowed but not required to use the black code formatter
- You may add type hints as you see fit, adhering to the guidelines set out in the typing package
- For typing use Python types like dict, list, if applicable

### Instrument drivers

- Use property creators (control, measurement, setting) for instrument parameters
- Getter and setter functions are discouraged, since properties provide a more fluid experience
- Given the extensive tools available for defining properties, these types of properties are preferred
- Instrument classes inherit from pymeasure.instruments.Instrument
- Adapters handle communication (VISA, Serial, Prologix, etc.)
- Use ProtocolAdapter with expected_protocol for testing instrument communication

#### File Organization

- Place instruments in the directory corresponding to the manufacturer
- Use lowercase for all filenames to distinguish packages from CamelCase Python classes
- Update the manufacturer's __init__.py file to import instruments
- Add test files in the corresponding tests/instruments/manufacturer/ directory
- Add documentation files in docs/api/instruments/manufacturer/

#### Property Creator Details

- Use validators (strict_range, truncated_range, strict_discrete_set, truncated_discrete_set) to restrict property values
- Use map_values parameter when instrument commands require non-physical values
- Implement boolean properties using maps with True/False values
- Use set_process and get_process functions for value transformations (e.g., unit conversions)
- Use preprocess_reply for string processing of device responses
- Enable check_get_errors/check_set_errors for instruments that report errors

#### Channel Implementation

- For instruments with fewer than 16 channels, use Instrument.ChannelCreator for explicit channel declaration
- For instruments with more than 16 channels, use Instrument.MultiChannelCreator
- Channels should inherit from the Channel class and use Channel-specific property creators
- Use the {ch} placeholder in command strings for automatic channel ID insertion
- Override insert_id method for channels with fixed command prefixes

#### Testing Instruments

- Write protocol tests using expected_protocol context manager for communication verification
- Create both protocol tests (without hardware) and device tests (with hardware)
- Use pytest fixtures for device tests to enable easy configuration and skipping
- Name device test files with "_with_device" suffix to distinguish them from protocol tests

### Measurement and GUI

- Procedures inherit from pymeasure.experiment.Procedure

## Documentation Standards

- PyMeasure documents code using reStructuredText and the Sphinx documentation generator
- All functions, classes, and methods should be documented in the code using a docstring
- Descriptive and specific docstrings are important for users to quickly understand properties and methods
- Use triple-quoted strings (`"""`) to delimit docstrings
- Start with one short summary line in imperative voice, with a period at the end
- Optionally, after a blank line, include more detailed information
- For functions and methods, add documentation on their parameters using the reStructuredText docstring format
- For properties, start them with "Control", "Get", "Measure", or "Set" to indicate the kind of property
- Add type and information about validators (if applicable) at the end of the summary line
- Example property docstring: `"""Control the voltage in Volts (float strictly from -1 to 1)."""`
- Docstrings should only contain information relevant for using a property/method, not internal details

## Core Architecture Patterns

- Instruments use Adapter pattern for communication abstraction
- Procedures define experimental workflows with startup/execute/shutdown
- Workers run procedures in separate threads
- Results stored in CSV format with automatic unit parsing
- GUI uses Qt (via QtPy) with Manager/Experiment pattern
- Parameters and Metadata system for procedure configuration

## Non-Obvious Conventions

- Instrument control() method strips command formatting and uses format specifiers
- Dynamic properties allow runtime parameter changes using naming convention
- Channel system uses ChannelCreator class for hierarchical instrument interfaces
- ProtocolAdapter for testing without hardware
- Validators throw ValueError exceptions for invalid inputs
- Instrument properties can have error checking (check_set_errors, check_get_errors)

- DATA_COLUMNS parsing automatically detects Pint units in parentheses
