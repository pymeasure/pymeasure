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

import logging

from functools import partial
from typing import Any, Type

from ..inputs import (BooleanInput, Input, IntegerInput, ListInput, ScientificInput,
                      StringInput, UncertQuantInput, VectorInput, TrailingButton)
from ..Qt import QtWidgets, QtCore, QtGui
from ...experiment import parameters, Procedure

log = logging.getLogger(__name__)
log.addHandler(logging.NullHandler())

# tuple of Input classes that do not need an external label
NO_LABEL_INPUTS = (BooleanInput, )

class ArrowButton(QtWidgets.QToolButton):
    def __init__(self, parent=None):
        super().__init__(parent)

        self._angle = 0
        self.anim = QtCore.QPropertyAnimation(self, b"angle")
        self.setFixedSize(20, 20)
        self.setStyleSheet("QToolButton { border: none; }")
        self.setCheckable(True)
        self.setChecked(True)
        self.toggled.connect(self.animate)

        
    def paintEvent(self, e):
        p = QtGui.QPainter(self)
        p.setRenderHint(QtGui.QPainter.RenderHint.Antialiasing)
        p.setPen(QtGui.QPen(QtGui.QColor(0,0,0), 2))
        p.setBrush(QtGui.QBrush(QtGui.QColor(0,0,0)))

        w, h = self.width(), self.height()

        # arrow pointing down in checked state
        arrow = QtGui.QPolygonF([
            QtCore.QPointF(w*0.5, h*0.8),
            QtCore.QPointF(w*0.2, h*0.2),
            QtCore.QPointF(w*0.8, h*0.2),
            QtCore.QPointF(w*0.5, h*0.8),
        ])

        # rotate around center
        p.translate(w/2, h/2)
        p.rotate(self._angle)
        p.translate(-w/2, -h/2)

        p.drawPolygon(arrow)

    def getAngle(self) -> float:
        return self._angle

    def setAngle(self, v: float):
        self._angle = v
        self.update()

    angle = QtCore.Property(float, getAngle, setAngle)

    def animate(self, checked: bool):
        self.anim.stop()
        self.anim.setDuration(500)
        self.anim.setStartValue(self._angle)
        self.anim.setEndValue(self._angle + (1 if checked else -1)*90)
        self.anim.start()

class InputGroup(QtWidgets.QWidget):
    def __init__(self, group: parameters.ParameterGroup, *args, **kwargs) -> None:
        super().__init__(*args, **kwargs)

        self.parameter = group
        
        self.layout = QtWidgets.QVBoxLayout(self)
        self.layout.setAlignment(QtCore.Qt.AlignmentFlag.AlignTop)
        self.layout.setContentsMargins(0,0,0,0)

        self.header_layout = QtWidgets.QHBoxLayout()
        self.layout.addLayout(self.header_layout)

        self.collapse_button = ArrowButton()
        self.collapse_button.setFixedSize(15,15)
        self.toggled = self.collapse_button.toggled
        self.header_layout.addWidget(self.collapse_button)
        
        self.header_label = QtWidgets.QLabel(self.parameter.name)
        self.header_layout.addWidget(self.header_label)
        
        self.contents = QtWidgets.QWidget()
        self.contents.setObjectName("inputGroupContents")
        self.contents.setStyleSheet("""
            #inputGroupContents {
                border: 1px solid #999;
                border-radius: 5px
            }
        """)
        self.layout.addWidget(self.contents)
        self.contents_layout = QtWidgets.QVBoxLayout(self.contents)

        self.anim_contents = QtCore.QPropertyAnimation(self.contents, b"maximumHeight")
        self.anim_contents.setDuration(500)
        self.anim_contents.setEasingCurve(QtCore.QEasingCurve.Type.InOutCubic)
        
        self._height = None
        self.toggled.connect(self.animate)
        self.setup_ui()
        
    def setup_ui(self):
        self.elements = {}
        for _,parameter in self.parameter.parameters.items():
            if parameter.ui_class is not None:
                element = parameter.ui_class(parameter)
                
            elif isinstance(parameter,parameters.ParameterGroup):
                element = InputGroup(parameter)
                
            elif isinstance(parameter, parameters.FloatParameter):
                element = ScientificInput(parameter)

            elif isinstance(parameter, parameters.PhysicalParameter):
                element = UncertQuantInput(parameter)

            elif isinstance(parameter, parameters.IntegerParameter):
                element = IntegerInput(parameter)

            elif isinstance(parameter, parameters.BooleanParameter):
                element = BooleanInput(parameter)

            elif isinstance(parameter, parameters.ListParameter):
                element = ListInput(parameter)

            elif isinstance(parameter, parameters.VectorParameter):
                element = VectorInput(parameter)

            elif isinstance(parameter, parameters.Parameter):
                element = StringInput(parameter)

            self.add_input(element, parameter.name)
            self.elements[parameter.name] = element
            
    def add_input(self, input_widget: Input, label: str | None = None):
        if label and not isinstance(input_widget, NO_LABEL_INPUTS):
            label_widget = QtWidgets.QLabel()
            label_widget.setText(f"{label}:")
            self.contents_layout.addWidget(label_widget)
        self.contents_layout.addWidget(input_widget)

    def animate(self, checked: bool):
        if self._height is None:
            self._height = self.contents.sizeHint().height()
        self.anim_contents.stop()
        self.anim_contents.setStartValue(self.contents.height())
        self.anim_contents.setEndValue(self._height if checked else 1)
        self.anim_contents.start()

class RangeInputGroup(InputGroup):
    selection_triggered = QtCore.Signal(object)
    def __init__(self, group: parameters.ParameterGroup, *args, **kwargs) -> None:
        super().__init__(group, *args, **kwargs)
        self.select_trailing_button = TrailingButton(
            "◱", lambda: self.selection_triggered.emit(self.get_range()), "Select range"
        )
        self.header_layout.addWidget(self.select_trailing_button)
        self.select_trailing_button.setVisible(True)

    def set_range(self, r: tuple):
        self.elements["Start"].set_value(r[0])
        self.elements["Stop"].set_value(r[1])

    def get_range(self):
        return self.elements["Start"].get_value(), self.elements["Stop"].get_value()
        
class InputsWidget(QtWidgets.QWidget):
    """
    Widget wrapper for various :doc:`inputs`
    """
    selection_triggered = QtCore.Signal(str, object)
    def __init__(self,
                 procedure_class: Type[Procedure],
                 inputs: tuple[str] | None = None,
                 hide_groups: bool=True,
                 inputs_in_scrollarea: bool=False,
                 **kwargs):
        super().__init__(**kwargs)
        self._procedure_class = procedure_class
        self._procedure = procedure_class()
        self._inputs = inputs if inputs else ()
        self._setup_ui()
        self._layout(inputs_in_scrollarea)
        self._hide_groups = hide_groups
        self._setup_visibility_groups()

    def _setup_ui(self) -> None:
        parameter_objects = self._procedure.parameter_objects()
        for name in self._inputs:
            parameter = parameter_objects[name]
            
            if isinstance(parameter, parameters.Range1DParameterGroup):
                element = RangeInputGroup(parameter)
                element.selection_triggered.connect(lambda x: self.selection_triggered.emit(name, x))
                setattr(self, "set_range", element.set_range)
            
            elif isinstance(parameter,parameters.ParameterGroup):
                element = InputGroup(parameter)
                
            elif parameter.ui_class is not None:
                element = parameter.ui_class(parameter)
                
            elif isinstance(parameter, parameters.FloatParameter):
                element = ScientificInput(parameter)

            elif isinstance(parameter, parameters.PhysicalParameter):
                element = UncertQuantInput(parameter)

            elif isinstance(parameter, parameters.IntegerParameter):
                element = IntegerInput(parameter)

            elif isinstance(parameter, parameters.BooleanParameter):
                element = BooleanInput(parameter)

            elif isinstance(parameter, parameters.ListParameter):
                element = ListInput(parameter)

            elif isinstance(parameter, parameters.VectorParameter):
                element = VectorInput(parameter)

            elif isinstance(parameter, parameters.Parameter):
                element = StringInput(parameter)

            setattr(self, name, element)
        
    def _layout(self, inputs_in_scrollarea):
        vbox = QtWidgets.QVBoxLayout(self)
        vbox.setSpacing(6)
        vbox.setContentsMargins(0, 0, 0, 0)

        self.labels = {}
        parameters = self._procedure.parameter_objects()
        """groups = {
            parameters[name].group_name: InputGroup(parameters[name].group_name)
            for name in self._inputs
            if parameters[name].group_name
        }"""
        for name in self._inputs:
            input_inst: Input = getattr(self, name)
            """if (group := groups.get(parameters[name].group_name, None)):
                group.add_input(input_inst,
                                parameters[name].name
                                if not isinstance(input_inst, self.NO_LABEL_INPUTS)
                                else None)"""
            if not isinstance(input_inst, NO_LABEL_INPUTS) and not isinstance(input_inst, InputGroup):
                label = QtWidgets.QLabel(self)
                label.setText("%s:" % parameters[name].name)
                vbox.addWidget(label)
                vbox.addWidget(input_inst)
                self.labels[name] = label
            else:
                vbox.addWidget(input_inst)
        """for _, group in groups.items():
            vbox.addWidget(group)"""

        if inputs_in_scrollarea:
            scroll_area = QtWidgets.QScrollArea()
            scroll_area.setWidgetResizable(True)
            scroll_area.setFrameStyle(QtWidgets.QScrollArea.Shape.NoFrame)
            scroll_area.setHorizontalScrollBarPolicy(QtCore.Qt.ScrollBarPolicy.ScrollBarAlwaysOff)

            inputs = QtWidgets.QWidget(self)
            inputs.setLayout(vbox)
            inputs.setSizePolicy(QtWidgets.QSizePolicy.Policy.Minimum,
                                 QtWidgets.QSizePolicy.Policy.Fixed)
            scroll_area.setWidget(inputs)

            vbox = QtWidgets.QVBoxLayout(self)
            vbox.setContentsMargins(0, 0, 0, 0)
            vbox.addWidget(scroll_area, 1)

        self.setLayout(vbox)

    def _setup_visibility_groups(self):
        groups = {}
        parameters = self._procedure.parameter_objects()
        for name in self._inputs:
            parameter = parameters[name]
            
            group_state = {g: True for g in parameter.group_by}

            for group_name, condition in parameter.group_by.items():
                if group_name not in self._inputs or group_name == name:
                    continue

                if isinstance(getattr(self, group_name), BooleanInput):
                    # Adjust the boolean condition to a condition suitable for a checkbox
                    condition = bool(condition)

                if group_name not in groups:
                    groups[group_name] = []

                groups[group_name].append((name, condition, group_state))

        #TODO: Functions for grouping should not depend on Qt.
        for group_name, group in groups.items():
            toggle = partial(self.toggle_group, group_name=group_name, group=group)
            group_el = getattr(self, group_name)
            if isinstance(group_el, BooleanInput):
                group_el.widget.toggled.connect(toggle)
                toggle(group_el.widget.isChecked())
            elif isinstance(group_el, (StringInput, VectorInput)):
                group_el.widget.textChanged.connect(toggle)
                toggle(group_el.widget.text())
            elif isinstance(group_el, (IntegerInput, ScientificInput)):
                group_el.widget.valueChanged.connect(toggle)
                toggle(group_el.widget.value())
            elif isinstance(group_el, ListInput):
                group_el.widget.currentTextChanged.connect(toggle)
                toggle(group_el.widget.currentText())
            else:
                raise NotImplementedError(
                    f"Grouping based on {group_name} ({group_el}) is not implemented.")

    def toggle_group(self, state, group_name, group):
        for (name, condition, group_state) in group:
            if callable(condition):
                group_state[group_name] = condition(state)
            else:
                group_state[group_name] = (state == condition)

            visible = all(group_state.values())

            if self._hide_groups:
                getattr(self, name).setHidden(not visible)
            else:
                getattr(self, name).setDisabled(not visible)

            if name in self.labels:
                if self._hide_groups:
                    self.labels[name].setHidden(not visible)
                else:
                    self.labels[name].setDisabled(not visible)

    def set_parameters(self, parameter_objects):
        for name in self._inputs:
            element = getattr(self, name)
            element.set_parameter(parameter_objects[name])

    def get_procedure(self):
        """ Returns the current procedure """
        self._procedure = self._procedure_class()
        parameter_values = {}
        for name in self._inputs:
            element = getattr(self, name)
            parameter_values[name] = element.parameter.value
        self._procedure.set_parameters(parameter_values)
        return self._procedure
