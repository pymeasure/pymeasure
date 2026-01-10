import pymeasure.experiment.parameters as parameters
from .Qt import QtCore, QtGui, QtWidgets
from .inputs import (BooleanInput, Input, IntegerInput, ListInput, ScientificInput,
                      StringInput, UncertQuantInput, VectorInput, TrailingButton)

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

    def paintEvent(self, e: QtGui.QPaintEvent):
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
        
        self.vlayout = QtWidgets.QVBoxLayout(self)
        self.vlayout.setAlignment(QtCore.Qt.AlignmentFlag.AlignTop)
        self.vlayout.setContentsMargins(0,0,0,0)

        self.header_layout = QtWidgets.QHBoxLayout()
        self.vlayout.addLayout(self.header_layout)

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
        self.vlayout.addWidget(self.contents)
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

class Range1DInputGroup(InputGroup):
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

class Range2DInputGroup(InputGroup):
    selection_triggered = QtCore.Signal(object)
    def __init__(self, group: parameters.ParameterGroup, *args, **kwargs) -> None:
        super().__init__(group, *args, **kwargs)
        self.select_trailing_button = TrailingButton(
            "◱", lambda: self.selection_triggered.emit(self.get_range()), "Select range"
        )
        self.header_layout.addWidget(self.select_trailing_button)
        self.select_trailing_button.setVisible(True)

    def set_range(self, r: tuple):
        self.elements["Start x"].set_value(r[0])
        self.elements["Stop x"].set_value(r[1])
        self.elements["Start y"].set_value(r[2])
        self.elements["Stop y"].set_value(r[3])
        
    def get_range(self):
        return self.elements["Start x"].get_value(), self.elements["Stop x"].get_value(), self.elements["Start y"].get_value(), self.elements["Stop y"].get_value()
