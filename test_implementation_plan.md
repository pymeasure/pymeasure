# PyMeasure Test Implementation Plan

## Table of Contents
1. [Introduction](#introduction)
2. [Testing Framework Overview](#testing-framework-overview)
3. [Component Testing Categories](#component-testing-categories)
4. [Testing Patterns and Templates](#testing-patterns-and-templates)
5. [Prioritized Implementation Roadmap](#prioritized-implementation-roadmap)
6. [Detailed Component Requirements](#detailed-component-requirements)
7. [Implementation Guidelines](#implementation-guidelines)
8. [Quality Assurance](#quality-assurance)

## Introduction

This document provides a comprehensive plan for implementing tests to improve coverage in the PyMeasure codebase based on the Test Coverage Gap Analysis. The plan focuses on systematically increasing test coverage for critical components while maintaining consistency with existing testing patterns and project standards.

### Objectives
- Increase test coverage for display modules (manager, browser, curves, widgets, windows)
- Improve test coverage for experiment modules (experiment.py, config.py)
- Enhance testing of adapter base classes
- Implement tests for high-priority instruments (power supplies, multimeters, signal generators)
- Establish consistent testing patterns across the codebase

### Scope
This plan covers:
- Unit tests for core functionality
- Integration tests for module interactions
- UI tests for display components using pytest-qt
- Instrument tests using the ProtocolAdapter pattern
- Test file organization and structure

## Testing Framework Overview

PyMeasure uses pytest as its primary testing framework with several specialized tools and patterns:

### Core Testing Tools
- **pytest**: Primary test runner and framework
- **pytest-qt**: For testing Qt-based UI components
- **ProtocolAdapter**: For testing instrument communication without hardware
- **expected_protocol**: Context manager for verifying instrument communication protocols
- **FakeAdapter**: For testing basic adapter functionality

### Test Organization
Tests are organized in a parallel structure to the main codebase:
```
tests/
├── adapters/
├── display/
│   ├── widgets/
│   └── windows/
├── experiment/
└── instruments/
    ├── manufacturer1/
    ├── manufacturer2/
    └── ...
```

### Test Types
1. **Protocol Tests**: Verify instrument communication without hardware
2. **Device Tests**: Test with actual connected devices (skipped by default)
3. **Unit Tests**: Test individual functions and classes
4. **Integration Tests**: Test interactions between components
5. **UI Tests**: Test graphical user interface components

## Component Testing Categories

Based on the Test Coverage Gap Analysis, components are categorized by priority:

### High Priority (Immediate Attention Required)
1. **Display Modules** - Critical for user experience and application stability
   - Manager, browser, curves, and window components
2. **Experiment Modules** - Fundamental to the framework's operation
   - Core experiment functionality and configuration handling
3. **Adapter Base Classes** - Foundation for all instrument communication
   - Improved testing would benefit all instrument implementations

### Medium Priority
4. **Power Supply Instruments** - Safety-critical with widespread usage
   - Keithley, Keysight, TDK power supplies
5. **Multimeter Instruments** - Accuracy-critical measurement devices
   - Keithley, HP multimeters
6. **Signal Generator Instruments** - Frequency/amplitude accuracy critical
   - Keysight, Tektronix, Rigol signal generators

### Lower Priority
7. **Specialized Scientific Instruments** - Niche applications
   - Temperature controllers, oscilloscopes, lock-in amplifiers

## Testing Patterns and Templates

### General Test Structure
All tests should follow the standard pytest structure with appropriate fixtures and parametrization where applicable.

```python
#
# This file is part of the PyMeasure package.
#
# Copyright (c) 2013-2025 PyMeasure Developers
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in
# all copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN
# THE SOFTWARE.
#

import pytest

# Import necessary modules
from pymeasure.module import ClassToTest


class TestClassToTest:
    """Test cases for ClassToTest"""

    def test_example_method(self):
        """Test example method functionality"""
        # Arrange
        obj = ClassToTest()

        # Act
        result = obj.example_method()

        # Assert
        assert result == expected_value
```

### Instrument Protocol Tests Template

For testing instrument communication without hardware:

```python
import pytest
from pymeasure.test import expected_protocol
from pymeasure.instruments.manufacturer import InstrumentClass


def test_property_getter():
    """Verify the communication of the property getter."""
    with expected_protocol(
        InstrumentClass,
        [(":COMMAND?", "EXPECTED_RESPONSE")],
    ) as inst:
        assert inst.property == expected_value


def test_property_setter():
    """Verify the communication of the property setter."""
    with expected_protocol(
        InstrumentClass,
        [(":COMMAND VALUE", None)],
    ) as inst:
        inst.property = value


@pytest.mark.parametrize("input_value, expected_command", [
    (1.0, ":COMMAND 1.0"),
    (2.5, ":COMMAND 2.5"),
])
def test_property_setter_parametrized(input_value, expected_command):
    """Verify the communication of the property setter with multiple values."""
    with expected_protocol(
        InstrumentClass,
        [(expected_command, None)],
    ) as inst:
        inst.property = input_value
```

### Device Tests Template

For testing with actual connected devices:

```python
import pytest
from pymeasure.instruments.manufacturer import InstrumentClass


@pytest.fixture(scope="module")
def instrument(connected_device_address):
    """Fixture to create an instrument instance for testing."""
    instr = InstrumentClass(connected_device_address)
    # Ensure the device is in a defined state
    instr.reset()
    return instr


def test_property_getter(instrument):
    """Test property getter with actual device."""
    # Arrange
    expected_type = float

    # Act
    result = instrument.property

    # Assert
    assert isinstance(result, expected_type)


@pytest.mark.skip(reason="Manual intervention required")
def test_manual_operation(instrument):
    """Test requiring manual intervention."""
    # This test requires manual setup or verification
    pass
```

### UI Tests Template

For testing Qt-based UI components:

```python
import pytest
from unittest import mock
from pymeasure.display.Qt import QtCore
from pymeasure.display.widgets import WidgetClass


class TestWidgetClass:
    """Test cases for WidgetClass"""

    def test_initialization(self, qtbot):
        """Test widget initialization."""
        # Arrange & Act
        widget = WidgetClass()
        qtbot.addWidget(widget)

        # Assert
        assert widget.isVisible() is False


    def test_button_click(self, qtbot):
        """Test button click functionality."""
        # Arrange
        widget = WidgetClass()
        qtbot.addWidget(widget)
        widget.show()

        # Act
        qtbot.mouseClick(widget.button, QtCore.Qt.LeftButton)

        # Assert
        assert widget.some_state == expected_state
```

### Adapter Tests Template

For testing adapter base classes:

```python
import pytest
from pymeasure.adapters import AdapterClass
from pymeasure.test import expected_protocol


def test_adapter_write():
    """Test adapter write functionality."""
    with expected_protocol(
        AdapterClass,
        [("TEST_COMMAND", None)],
        connection_attributes={'write_termination': '\n'}
    ) as adapter:
        adapter.write("TEST_COMMAND")


def test_adapter_read():
    """Test adapter read functionality."""
    with expected_protocol(
        AdapterClass,
        [(None, "TEST_RESPONSE")],
        connection_attributes={'read_termination': '\n'}
    ) as adapter:
        result = adapter.read()
        assert result == "TEST_RESPONSE"
```

## Prioritized Implementation Roadmap

### Phase 1: High Priority Components (Months 1-2)
Focus on display and experiment modules that form the core user experience.

#### Month 1:
- Display Manager module (`pymeasure/display/manager.py`)
- Display Browser module (`pymeasure/display/browser.py`)
- Display Curves module (`pymeasure/display/curves.py`)
- Display Listeners module (`pymeasure/display/listeners.py`)

#### Month 2:
- Display Log module (`pymeasure/display/log.py`)
- Display Thread module (`pymeasure/display/thread.py`)
- Display Qt module (`pymeasure/display/Qt.py`)
- Experiment module (`pymeasure/experiment/experiment.py`)
- Config module (`pymeasure/experiment/config.py`)

### Phase 2: Adapter Base Classes (Month 3)
Enhance testing of foundational adapter components.

- Adapter base class (`pymeasure/adapters/adapter.py`)
- ProtocolAdapter (`pymeasure/adapters/protocol.py`)
- VISA adapter (`pymeasure/adapters/visa.py`)
- Serial adapter (`pymeasure/adapters/serial.py`)
- Prologix adapter (`pymeasure/adapters/prologix.py`)

### Phase 3: High-Priority Instruments (Months 4-6)
Implement tests for safety-critical and commonly used instruments.

#### Month 4:
- Keithley 2400 SourceMeter
- Keithley 2000 Multimeter
- Keithley DMM6500 Multimeter

#### Month 5:
- Keysight E3631A Power Supply
- TDK GEN Series Power Supplies
- HP 34401A Multimeter

#### Month 6:
- Keysight 81160A Signal Generator
- Tektronix AFG3152 Signal Generator
- Rigol DG800 Signal Generator

### Phase 4: Display Widgets and Windows (Months 7-8)
Complete testing of UI components.

#### Month 7:
- All display widgets (`pymeasure/display/widgets/`)
- Managed Window (`pymeasure/display/windows/managed_window.py`)

#### Month 8:
- Managed Dock Window (`pymeasure/display/windows/managed_dock_window.py`)
- Plotter Window (`pymeasure/display/windows/plotter_window.py`)
- Managed Image Window (`pymeasure/display/windows/managed_image_window.py`)

### Phase 5: Medium-Priority Instruments (Months 9-12)
Expand coverage to medium-priority instruments.

#### Months 9-10:
- Temperature Controllers (HCP TC038 series, Temptronic)
- Oscilloscopes (LeCroy T3DSO1204, Keysight DSOX1102G)

#### Months 11-12:
- Specialized Equipment (SRS SR830 Lock-in amplifier, Lakeshore 425 Gaussmeter)

### Phase 6: Lower-Priority Instruments (Ongoing)
Gradually increase coverage for all remaining instrument modules.

## Detailed Component Requirements

### Display Modules

#### Manager Module (`pymeasure/display/manager.py`)
**Components to Test:**
- `Experiment` class initialization and properties
- `ExperimentQueue` class functionality (append, remove, contains, getitem, next, has_next, with_browser_item)
- `BaseManager` class functionality (is_running, running_experiment, load, queue, remove, clear, next, resume, abort)
- `Manager` class functionality (load, remove, finish)
- Signal emissions (queued, running, finished, failed, aborted, abort_returned, log)

**Testing Approach:**
- Unit tests for each class and method
- Mock Qt signals and slots
- Integration tests for queue management
- Test edge cases (empty queue, running experiment, etc.)

#### Browser Module (`pymeasure/display/browser.py`)
**Components to Test:**
- `BaseBrowserItem` abstract methods
- `BrowserItem` class functionality (setStatus, setProgress)
- `Browser` class functionality (add method, header labels, sorting)
- Status label mapping

**Testing Approach:**
- Unit tests for each class
- UI tests with pytest-qt for visual components
- Test data validation and parameter handling

#### Other Display Modules
Similar approach for curves, listeners, log, thread, and Qt modules with focus on:
- Class initialization and properties
- Method functionality
- Error handling
- Integration with other components

### Experiment Modules

#### Experiment Module (`pymeasure/experiment/experiment.py`)
**Components to Test:**
- Array generation functions (get_array, get_array_steps, get_array_zero)
- Filename creation (create_filename)
- `Experiment` class initialization and properties
- Data handling (data property, wait_for_data)
- Plotting functionality (plot_live, plot, clear_plot, update_plot, update_line)

**Testing Approach:**
- Unit tests for array functions
- Mock file system for filename tests
- Test data processing and analysis functions
- Integration tests for plotting functionality

#### Config Module (`pymeasure/experiment/config.py`)
**Components to Test:**
- Configuration file handling (set_file, get_config)
- Matplotlib configuration (set_mpl_rcparams)

**Testing Approach:**
- Unit tests for configuration functions
- Mock environment variables and file system
- Test with various configuration file formats

### Adapter Base Classes

#### Adapter Module (`pymeasure/adapters/adapter.py`)
**Components to Test:**
- `Adapter` base class initialization and properties
- Write/read methods (write, write_bytes, read, read_bytes)
- Abstract methods implementation (_write, _write_bytes, _read, _read_bytes, flush_read_buffer)
- Binary values handling (read_binary_values, _format_binary_values, write_binary_values)
- `FakeAdapter` functionality

**Testing Approach:**
- Unit tests for each method
- Test buffer management in FakeAdapter
- Test binary data handling
- Test error conditions and edge cases

### High-Priority Instruments

#### Keithley 2400 SourceMeter
**Components to Test:**
- All properties (source_mode, source_enabled, auto_output_off, etc.)
- Measurement methods (measure_resistance, measure_voltage, measure_current)
- Application methods (apply_current, apply_voltage)
- Source control methods (enable_source, disable_source)
- Ramping functionality (ramp_to_current, ramp_to_voltage)

**Testing Approach:**
- Protocol tests for all property getters and setters
- Test command sequences for measurement methods
- Parametrized tests for value ranges
- Test error handling and validation

#### Keithley 2000 Multimeter
**Components to Test:**
- Mode selection and configuration
- All measurement properties (current, voltage, resistance, etc.)
- Measurement configuration methods (measure_voltage, measure_current, measure_resistance)
- Range and reference settings

**Testing Approach:**
- Protocol tests for mode switching
- Test all measurement types
- Parametrized tests for range values
- Test AC/DC configuration differences

#### Signal Generators
**Components to Test:**
- Output enabling/disabling
- Waveform type selection
- Frequency, amplitude, and offset controls
- Maximum output amplitude settings

**Testing Approach:**
- Protocol tests for all properties
- Test waveform-specific parameters
- Validate value ranges and constraints
- Test channel-specific functionality

## Implementation Guidelines

### Code Quality Standards
1. Follow PEP8 style guide and PEP257 docstring conventions
2. Use flake8 for linting with max-line-length=100
3. Format code with black (line-length=100) when appropriate
4. Sort imports with isort
5. Add type hints where beneficial

### Test Documentation
1. Include comprehensive docstrings for all test functions
2. Use descriptive test function names following the pattern `test_action_expected_result`
3. Add comments for complex test setups or assertions
4. Document any test-specific assumptions or requirements

### Test Organization
1. Mirror the source code structure in the tests directory
2. Use separate files for different aspects of testing when appropriate
3. Group related tests in classes
4. Use parametrized tests for similar test cases with different inputs

### Test Dependencies
1. Minimize external dependencies in tests
2. Use appropriate fixtures for test setup and teardown
3. Mock external systems when necessary
4. Isolate tests to prevent side effects

### Continuous Integration
1. Ensure all tests pass locally before submitting PRs
2. Follow the existing CI configuration
3. Add tests to increase coverage metrics
4. Avoid tests that are flaky or unreliable

## Quality Assurance

### Code Review Process
1. All test code must undergo peer review
2. Tests should be reviewed for completeness and correctness
3. Verify adherence to project testing patterns
4. Check for unnecessary complexity or redundancy

### Test Maintenance
1. Update tests when modifying existing functionality
2. Remove obsolete tests when deprecating features
3. Regularly review test coverage reports
4. Refactor tests to improve clarity and maintainability

### Performance Considerations
1. Optimize test execution time where possible
2. Use appropriate scoping for fixtures
3. Avoid unnecessary setup in tests
4. Parallelize tests when safe to do so

### Security and Safety
1. Ensure tests don't pose safety risks when run
2. Validate that instrument tests won't damage hardware
3. Sanitize any test data or commands
4. Follow secure coding practices in test code