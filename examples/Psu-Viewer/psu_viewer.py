import configparser
import gc
import os
import re
import sys

from pymeasure.instruments.keysight import KeysightN5767A
from PyQt5.QtCore import Qt, QTimer, pyqtSlot
from PyQt5.QtGui import QIcon, QPalette
from PyQt5.QtWidgets import QApplication, QDialog, QMainWindow, QMessageBox
from PyQt5.uic import loadUi


class HistoryConfig():
    def __init__(self):
        self.config = configparser.ConfigParser()
        self.python_config_path = './psu.ini'
        if not os.path.exists(self.python_config_path):
            self.config['HISTORY'] = {'address': "GPIB0::1::INSTR",
                                      'voltage_range': 5.0,
                                      'current_range': 1.0}
            with open(self.python_config_path, "w+") as f:
                self.config.write(f)

    def get(self, key):
        self.config.read(self.python_config_path)
        return self.config.get("HISTORY", key)

    def set(self, key, value):
        self.config.read(self.python_config_path)
        self.config.set("HISTORY", key, str(value))
        with open(self.python_config_path, "w") as f:
            self.config.write(f)


class PSU_Viewer(QDialog):
    def __init__(self, *args):
        super(PSU_Viewer, self).__init__(*args)

        self.timer = QTimer(self)
        self.timer.timeout.connect(self.update)

        self.psu_viewer = loadUi("psu_viewer.ui", self)
        self.psu_viewer.setWindowIcon(QIcon('psu.png'))

        self.config = HistoryConfig()

        self.pe = QPalette()
        self.psu_viewer.label_status_value.setAutoFillBackground(True)

        self.address = self.config.get("address")
        self.psu_viewer.lineEdit_address.setText(self.address)

        self.voltage_range = self.config.get("voltage_range")
        self.current_range = self.config.get("current_range")

        self.psu_viewer.lineEdit_voltage.setText(str(self.voltage_range))
        self.psu_viewer.lineEdit_current.setText(str(self.current_range))

        self.psu_controller = PSU_Controller()
        try:
            self.psu_controller.create_instance(self.address)

            self.current_range = self.psu_controller.get_current_range()
            self.voltage_range = self.psu_controller.get_voltage_range()

            self.psu_viewer.lineEdit_voltage.setText(str(self.voltage_range))
            self.psu_viewer.lineEdit_current.setText(str(self.current_range))

            self.config.set("voltage_range", self.voltage_range)
            self.config.set("current_range", self.current_range)

            self.update()
            self.timer.start(1000)

        except Exception as e:
            print(e)

    @pyqtSlot()
    def on_pushButtonSetAddress_clicked(self):
        self.timer.stop()
        address = self.get_lineEdit_address()
        if not self.check_address_valid(address):
            QMessageBox.information(self, "Info",
                                    "Input format err",
                                    QMessageBox.Ok)
            return

        try:
            self.set_default_view()
            self.address = address
            ret = self.psu_controller.create_instance(self.address)
            if ret != True:
                QMessageBox.information(self, "Info",
                                        "Failed,please check address and physical connection",
                                        QMessageBox.Ok)
                return

            self.model = self.psu_controller.psu.id
            if self.model:
                self.psu_viewer.label_model_value.setText(self.model)

                self.config.set("address", self.address)

                self.update()

                self.timer.start(1000)

                QMessageBox.information(self, "Info",
                                        "Connect success",
                                        QMessageBox.Ok)

        except Exception as e:
            QMessageBox.information(self, "Info",
                                    "Failed,please check address and physical connection",
                                    QMessageBox.Ok)

    @pyqtSlot()
    def on_pushButtonSwitch_clicked(self):
        try:
            self.psu_enable_status = self.psu_controller.is_enabled()
            if self.psu_enable_status:
                self.psu_controller.psu.disable()

            else:
                self.psu_controller.psu.enable()

            self.update()
        except Exception as e:
            QMessageBox.information(self, "Info",
                                    "Failed,please connect psu first,{}".format(e),
                                    QMessageBox.Ok)

    @pyqtSlot()
    def on_pushButtonSetVoltageCurrent_clicked(self):
        current_range = self.get_lineEdit_current()
        if not self.check_digital_valid(current_range):
            QMessageBox.information(self, "Info",
                                    "Input format err",
                                    QMessageBox.Ok)

            return
        self.current_range = current_range

        voltage_range = self.get_lineEdit_voltage()
        if not self.check_digital_valid(voltage_range):
            QMessageBox.information(self, "Info",
                                    "Input format err",
                                    QMessageBox.Ok)
            return
        self.voltage_range = voltage_range

        try:
            self.psu_controller.set_voltage_range(float(self.voltage_range))
            self.psu_controller.set_current_range(float(self.current_range))

            self.voltage_range = self.psu_controller.get_voltage_range()
            self.current_range = self.psu_controller.get_current_range()

            self.config.set("voltage_range", self.voltage_range)
            self.config.set("current_range", self.current_range)

            self.update()
        except Exception as e:
            QMessageBox.information(self, "Info",
                                    "Fail to set,{}".format(e),
                                    QMessageBox.Ok)

    def get_lineEdit_address(self):
        address = self.psu_viewer.lineEdit_address.text()
        address = address.strip().upper()
        return address

    def get_lineEdit_current(self):
        current = self.psu_viewer.lineEdit_current.text()
        current = current.strip()
        return current

    def get_lineEdit_voltage(self):
        voltage = self.psu_viewer.lineEdit_voltage.text()
        voltage = voltage.strip()
        return voltage

    def check_address_valid(self, address):
        regx = "^GPIB\d+::\d+::INSTR$"
        return bool(re.match(regx, address))

    def check_digital_valid(self, i):
        regx = "^\d+(\.\d*)?$"
        re.match(regx, i)
        return bool(re.match(regx, i))

    def update(self):
        try:
            self.model = self.psu_controller.get_model()
            self.psu_viewer.label_model_value.setText(self.model)
            if self.model:
                self.psu_viewer.pushButtonSwitch.setEnabled(True)
                self.psu_viewer.pushButtonSetVoltageCurrent.setEnabled(True)
            else:
                self.psu_viewer.pushButtonSwitch.setEnabled(False)
                self.psu_viewer.pushButtonSetVoltageCurrent.setEnabled(False)

            self.switch_status = self.psu_controller.is_enabled()
            if self.switch_status:
                self.psu_viewer.pushButtonSwitch.setText("off")
                self.psu_viewer.label_status_value.setText("OUTPUT ON")

                self.pe.setColor(QPalette.Window, Qt.green)

            else:
                self.psu_viewer.pushButtonSwitch.setText("on")
                self.psu_viewer.label_status_value.setText("OUTPUT OFF")

                self.pe.setColor(QPalette.Window, Qt.white)

            self.psu_viewer.label_status_value.setPalette(self.pe)

            self.measurement_voltage = self.psu_controller.measure_voltage()
            self.measurement_current = self.psu_controller.measure_current()
            self.psu_viewer.label_measurement_voltage_value.setText(str(self.measurement_voltage))
            self.psu_viewer.label_measurement_current_value.setText(str(self.measurement_current))
        except Exception as e:
            pass

    def set_default_view(self):
        self.psu_viewer.label_model_value.setText("")

        self.psu_viewer.pushButtonSwitch.setText("on")
        self.psu_viewer.label_status_value.setText("OUTPUT OFF")

        self.pe.setColor(QPalette.Window, Qt.white)
        self.psu_viewer.label_status_value.setPalette(self.pe)

        self.psu_viewer.label_measurement_voltage_value.setText("")
        self.psu_viewer.label_measurement_current_value.setText("")

        self.psu_viewer.pushButtonSwitch.setEnabled(False)
        self.psu_viewer.pushButtonSetVoltageCurrent.setEnabled(False)


class PSU_Controller():
    def __init__(self):
        self.psu = None

    def create_instance(self, address):
        del self.psu

        gc.collect()

        self.psu = KeysightN5767A(address)

        return self.check_connect_status()

    def get_model(self):
        return ",".join(self.psu.id.split(",")[1::-1])

    def check_connect_status(self):
        return bool(self.psu.id)

    def is_enabled(self):
        return self.psu.is_enabled()

    def get_voltage_range(self):
        return self.psu.voltage_range

    def set_voltage_range(self, voltage_range):
        self.psu.voltage_range = voltage_range

    def get_current_range(self):
        return self.psu.current_range

    def set_current_range(self, current_range):
        self.psu.current_range = current_range

    def measure_voltage(self):
        return self.psu.voltage

    def measure_current(self):
        return self.psu.current


app = QApplication(sys.argv)
widget = PSU_Viewer()
widget.show()
sys.exit(app.exec_())
