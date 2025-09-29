# AI Assistant Guidelines

This file provides guidance to AI coding assistants (Claude Code, Cursor, GitHub Copilot, etc.) when working with code in this repository.

## Project Overview

PyMeasure is a scientific measurement library for instruments, experiments, and live-plotting. It provides two main components:
1. **Instruments** - A comprehensive repository of instrument classes for scientific hardware
2. **Experiment Framework** - A system for running experiment procedures with graphical interfaces

## Development Commands

### Testing
```bash
# Run all tests
pytest

# Run tests with coverage
pytest --cov=pymeasure --cov-report=xml

# Run single test file
pytest tests/test_specific_file.py

# Run with graphical interface support (Linux)
xvfb-run -a pytest
```

### Code Quality
```bash
# Lint with flake8 (check syntax errors and undefined names)
flake8 . --count --extend-select=E9,F63,F7,F82 --show-source --statistics

# Format code with black
black .

# Sort imports
isort .
```

### Documentation
```bash
# Build documentation
cd docs && make html

# Run doctests
cd docs && make doctest

# Build with warnings as errors
cd docs && make html SPHINXOPTS="-W --keep-going"
```

### Installation
```bash
# Editable install for development
pip install -e .[tests]

# Full install with all dependencies
pip install .[tests,tcp,docs]
```

## Architecture Overview

### Core Components

- **`pymeasure/instruments/`** - Hardware instrument drivers organized by manufacturer
  - `instrument.py` - Base `Instrument` class that all devices inherit from
  - `common_base.py` - Common functionality shared across instruments
  - Manufacturer subdirectories (e.g., `keithley/`, `rigol/`, `agilent/`)

- **`pymeasure/adapters/`** - Communication layer abstraction
  - `visa.py` - VISA adapter for most instruments
  - `serial.py` - Serial communication adapter
  - `protocol.py` - Protocol definitions for communication

- **`pymeasure/experiment/`** - Experiment framework for automated measurements
  - `procedure.py` - Base `Procedure` class for defining measurement sequences
  - `parameters.py` - Parameter types for experiment configuration
  - `results.py` - Data storage and management
  - `workers.py` - Background execution of procedures
  - `listeners.py` - Event handling and data streaming

- **`pymeasure/display/`** - GUI components for live plotting and experiment management

### Key Design Patterns

1. **Adapter Pattern**: Instruments use adapters to abstract communication protocols (VISA, Serial, etc.)
2. **Property-based Interface**: Instruments expose measurements and settings as Python properties
3. **Procedure-based Experiments**: Measurements are defined as procedures that can be queued and executed
4. **Event-driven Architecture**: The experiment system uses listeners for real-time data handling

### Adding New Instruments

When adding new instrument support:
1. Create manufacturer directory under `pymeasure/instruments/` if needed
2. Inherit from `Instrument` base class
3. Use appropriate adapter (usually `VISAAdapter`)
4. Define properties for measurements and settings
5. Follow existing naming conventions and patterns
6. Add comprehensive tests in `tests/instruments/`

### Configuration Files

- **`pyproject.toml`** - Main project configuration, dependencies, and tool settings
- **`.flake8`** - Flake8 linting configuration
- **`pyrightconfig.json`** - Type checking configuration
- **`.github/workflows/pymeasure_CI.yml`** - CI/CD pipeline configuration

### Testing Strategy

- Unit tests for all instrument classes
- Integration tests with simulated instruments using `pyvisa-sim`
- GUI tests using `pytest-qt`
- Continuous integration across Python 3.9-3.13 on Linux, macOS, and Windows
- Coverage reporting via codecov

### Dependencies

Key dependencies include:
- `pyvisa` - VISA instrument communication
- `pyserial` - Serial communication
- `numpy`/`pandas` - Data handling
- `pyqtgraph` - Real-time plotting
- `qtpy` - Qt abstraction layer
- `pint` - Unit handling