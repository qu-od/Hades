# developed by Andrey Rahimov. Organisation:SDIMPI
# command protocol provided by Fedya

from typing import List, Tuple, Dict, Optional
from importlib import reload
# import time

from PyQt5.QtWidgets import (
    QApplication, QWidget, QFileDialog, QStatusBar,
    QListWidgetItem, QErrorMessage, QMessageBox, QPushButton
)
from PyQt5 import uic
# from PyQt5.QtCore import
from PyQt5.QtNetwork import QTcpSocket

from commands import Command
from tcp_client import Connection
from command_makers import *
from bt_serial import toggle_arduino_led, open_port_by_name

class Window(object):
    def __init__(self):
        app = QApplication([])
        self.ui = uic.loadUi("mainwindow.ui")
        self.ui.show()

        self.conn = None
        self.ser = None

        #----------вкладка установки соединения и отправки сообщений вручную---------
        self.ui.send_hex_message_button.clicked.connect(
            self.send_hex_message)
        self.ui.connect_button.clicked.connect(
            self.make_connection)
        self.ui.disconnect_button.clicked.connect(
            self.close_connection)

        #-----------------вкладка поиска отправки команд по номеру-----------------
        self.ui.command_number_spinbox.valueChanged.connect(
            self.ui.command_name_ledit.clear)
        self.ui.command_name_ledit.textEdited.connect(
            self.set_null_in_command_number_spinbox)
        self.ui.fetch_command_button.clicked.connect(
            self.fetch_command)
        self.ui.send_command_button.clicked.connect(
            self.send_command)

        #---------------------вкладка общего раскрытия--------------------------
        self.ui.expand_all_button.clicked.connect(
            self.toggle_expand_all)
        self.ui.contract_all_button.clicked.connect(
            self.toggle_contract_all)
        self.ui.all_motors_stop_button.clicked.connect(
            self.all_motors_stop_method)

        #------------------вкладка раскрытия рефлектора-----------------------
        self.ui.reflector_expand_button.clicked.connect(
            self.toggle_reflector_expand)
        self.ui.reflector_contract_button.clicked.connect(
            self.toggle_reflector_contract)
        self.ui.reflector_upper_motor_open_button.clicked.connect(
            self.toggle_reflector_upper_motor_open)
        self.ui.reflector_upper_motor_close_button.clicked.connect(
            self.toggle_reflector_upper_motor_close)
        self.ui.reflector_lower_motor_open_button.clicked.connect(
            self.toggle_reflector_lower_motor_open)
        self.ui.reflector_lower_motor_close_button.clicked.connect(
            self.toggle_reflector_lower_motor_close)

        #--------------------вкладка раскрытия стенда--------------------------
        self.ui.bench_expand_button.clicked.connect(
            self.toggle_bench_expand)
        self.ui.bench_contract_button.clicked.connect(
            self.toggle_bench_contract)
        self.ui.bench_motor_open_button.clicked.connect(
            self.toggle_bench_motor_open)
        self.ui.bench_motor_close_button.clicked.connect(
            self.toggle_bench_motor_close)
        self.ui.bench_motor_tension_setup_button.clicked.connect(
            self.bench_motor_tension_setup)
        self.ui.bench_tension_setup_button.clicked.connect(
            self.bench_tension_setup)

        #--------------------вкладки показаний датчиков--------------------------
        self.ui.get_sensor_value_button.clicked.connect(
            self.get_sensor_value)
        self.ui.get_all_sensors_values_button.clicked.connect(
            self.get_all_sensors_values)

        #-----------------вкладка показаний тензодатчиков----------------------
        self.ui.open_comport_button.clicked.connect(
            self.open_comport)
        self.ui.arduino_led_on_button.clicked.connect(
            self.arduino_led_on)
        self.ui.arduino_led_off_button.clicked.connect(
            self.arduino_led_off)

        exit(app.exec())
    
    #------------------------функции для кнопок----------------------

    def make_connection(self):
        self.conn = Connection()
        if self.conn.is_refused: return
        self.ui.ip_adress_label.setText(self.conn.host)
        self.ui.port_label.setText(str(self.conn.port))

    def close_connection(self):
        if self.conn: self.conn.close()
        self.conn = None
        self.ui.ip_adress_label.setText('None')
        self.ui.port_label.setText('None')

    def send_command(self):
        command_number = self.ui.command_number_spinbox.value()
        command = Command(number = command_number)
        command_param_1_str: str = self.ui.param_1_ledit.text()
        command_param_2_str: str = self.ui.param_2_ledit.text()
        info_field_params: Optional[Tuple] = tuple()
        if command_param_1_str:
            if not command_param_2_str: 
                info_field_params = (int(command_param_1_str), )
            elif command_param_2_str:
                info_field_params = (
                    int(command_param_1_str), int(command_param_2_str))
        message: bytes = command.make_bytes_message(*info_field_params)
        if not message: return
        self.ui.message_ledit.setText(str(message))
        response: bytes = self.conn.send_message(message)
        self.ui.response_ledit.setText(str(response))
        is_command_succ = command.check_response(response)
        self.ui.response_check_label.setText(str(is_command_succ))

    def fetch_command(self):
        command_number: Optional[int] = None
        command_name: Optional[str] = None
        if self.ui.command_number_spinbox.value(): #если значение не ноль
            command_number = self.ui.command_number_spinbox.value()
        if self.ui.command_name_ledit.text(): #если строка не пуста
            command_name = self.ui.command_name_ledit.text()
        #test None values from line edits
        command = Command(name = command_name, number = command_number)
        if command.init_err_info: #in case of a command init error
            show_error(command.init_err_info)
            return
        self.ui.command_number_spinbox.setValue(command.number)
        self.ui.command_name_ledit.setText(command.name)
        print('fetch_command func worked')
        return command

    def set_null_in_command_number_spinbox(self):
        self.ui.command_number_spinbox.setValue(0)

    def send_hex_message(self):
        bytes_message_str: str = self.ui.bytes_message_ledit.text()
        if not bytes_message_str: 
            show_error('Enter the message first!')
            return
        # bytes_message_str: str = '550300000000'
        print('str_msg:', bytes_message_str)
        bytes_message: bytes = bytes.fromhex(bytes_message_str)
        print('bytes_msg:', bytes_message)
        bytes_response = self.conn.send_message(bytes_message)
        print('bytes_response:', bytes_response)
        self.ui.bytes_response_ledit.setText(str(bytes_response))


    #----------------функции для общего раскрытия----------------

    def toggle_expand_all(self):
        button: QPushButton = self.ui.expand_all_button
        pushed: bool = button.isChecked()
        if pushed:
            all_motors_stop(
                self.ui, self.conn, button = button,
                show_status=False)
            expand_all(self.ui, self.conn)
            button.setText('Идет раскрытие...')
        else: 
            all_motors_stop(self.ui, self.conn)
            button.setText('Раскрывать всё')

    def toggle_contract_all(self):
        button: QPushButton = self.ui.contract_all_button
        pushed: bool = button.isChecked()
        if pushed:
            all_motors_stop(
                self.ui, self.conn, button = button, 
                show_status=False)
            contract_all(self.ui, self.conn)
            button.setText('Идет складывание...')
        else:
            all_motors_stop(self.ui, self.conn)
            button.setText('Складывать всё')

    def all_motors_stop_method(self): #wrapper for func outside the window class
        all_motors_stop(self.ui, self.conn)


    #----------------функции для раскрытия рефлектора----------------

    def toggle_reflector_expand(self):
        button: QPushButton = self.ui.reflector_expand_button
        pushed: bool = button.isChecked()
        if pushed: 
            all_motors_stop(
                self.ui, self.conn, button = button, 
                show_status=False)
            reflector_expand(self.ui, self.conn)
            button.setText('Идет раскрытие...')
        else: 
            all_motors_stop(self.ui, self.conn)
            button.setText('Раскрывать')

    def toggle_reflector_contract(self):
        button: QPushButton = self.ui.reflector_contract_button
        pushed: bool = button.isChecked()
        if pushed:
            all_motors_stop(
                self.ui, self.conn, button = button, 
                show_status=False)
            reflector_contract(self.ui, self.conn)
            button.setText('Идет складывание...')
        else:
            all_motors_stop(self.ui, self.conn)
            button.setText('Складывать')

    def toggle_reflector_upper_motor_open(self):
        button: QPushButton = self.ui.reflector_upper_motor_open_button
        pushed: bool = button.isChecked()
        if pushed: 
            all_motors_stop(
                self.ui, self.conn, button = button, 
                show_status=False)
            reflector_upper_motor_open(self.ui, self.conn)
            button.setText('Идет открытие...')
        else: 
            all_motors_stop(self.ui, self.conn)
            button.setText('Открывать')

    def toggle_reflector_upper_motor_close(self):
        button: QPushButton = self.ui.reflector_upper_motor_close_button
        pushed: bool = button.isChecked()
        if pushed: 
            all_motors_stop(
                self.ui, self.conn, button = button, 
                show_status=False)
            reflector_upper_motor_close(self.ui, self.conn)
            button.setText('Идет закрытие...')
        else: 
            all_motors_stop(self.ui, self.conn)
            button.setText('Закрывать')

    def toggle_reflector_lower_motor_open(self):
        button: QPushButton = self.ui.reflector_lower_motor_open_button
        pushed: bool = button.isChecked()
        if pushed: 
            all_motors_stop(
                self.ui, self.conn, button = button, 
                show_status=False)
            reflector_lower_motor_open(self.ui, self.conn)
            button.setText('Идет открытие...')
        else:
            all_motors_stop(self.ui, self.conn)
            button.setText('Открывать')

    def toggle_reflector_lower_motor_close(self):
        button: QPushButton = self.ui.reflector_lower_motor_close_button
        pushed: bool = button.isChecked()
        if pushed: 
            all_motors_stop(
                self.ui, self.conn, button = button, 
                show_status=False)
            reflector_lower_motor_close(self.ui, self.conn)
            button.setText('Идет закрытие...')
        else: 
            all_motors_stop(self.ui, self.conn)
            button.setText('Закрывать')


    #----------------функции для раскрытия стенда----------------

    def toggle_bench_expand(self):
        button: QPushButton = self.ui.bench_expand_button
        pushed: bool = button.isChecked()
        if pushed: 
            all_motors_stop(
                self.ui, self.conn, button = button, 
                show_status=False)
            bench_expand(self.ui, self.conn)
            button.setText('Идет раскрытие...')
        else: 
            all_motors_stop(self.ui, self.conn)
            button.setText('Раскрывать')

    def toggle_bench_contract(self):
        button: QPushButton = self.ui.bench_contract_button
        pushed: bool = button.isChecked()
        if pushed:
            all_motors_stop(
                self.ui, self.conn, button = button, 
                show_status=False)
            bench_contract(self.ui, self.conn)
            button.setText('Идет складывание...')
        else:
            all_motors_stop(self.ui, self.conn)
            button.setText('Складывать')

    def toggle_bench_motor_open(self):
        button: QPushButton = self.ui.bench_motor_open_button
        pushed: bool = button.isChecked()
        if pushed: 
            all_motors_stop(
                self.ui, self.conn, button = button, 
                show_status=False)
            bench_motor_open(self.ui, self.conn)
            button.setText('Идет открытие...')
        else: 
            all_motors_stop(self.ui, self.conn)
            button.setText('Открывать')

    def toggle_bench_motor_close(self):
        button: QPushButton = self.ui.bench_motor_close_button
        pushed: bool = button.isChecked()
        if pushed: 
            all_motors_stop(
                self.ui, self.conn, button = button, 
                show_status=False)
            bench_motor_close(self.ui, self.conn)
            button.setText('Идет закрытие...')
        else: 
            all_motors_stop(self.ui, self.conn)
            button.setText('Закрывать')

    def bench_motor_tension_setup(self):
        cmd = Command(number = 132)
        motor_number: int = self.ui.motor_to_setup_number_spinbox.value()
        tension_value: int = self.ui.tension_value_spinbox.value()
        give_cmd(
            self.ui,
            cmd.name,
            cmd.send_and_check(self.conn, motor_number, tension_value))

    def bench_tension_setup(self):
        cmd = Command(number = 102)
        tension_value: int = self.ui.tension_value_spinbox.value()
        give_cmd(
            self.ui,
            cmd.name,
            cmd.send_and_check(self.conn, tension_value))

    #----------функции для показаний датчиков оборотов-------------

    def get_sensor_value(self):
        cmd = Command(number = 143)
        sensor_number = self.ui.sensor_number_spinbox.value()
        response: bytes
        is_command_succ, response = \
            cmd.send_and_check(self.conn, sensor_number, get_response=True)
        give_cmd(self.ui, cmd.name, is_command_succ)
        if not response: return
        sensor_value_tuple: Tuple[int] = cmd.decode_response_data(response) #tuple type NEED TESTING
        self.ui.sensors_values_label.setText(str(sensor_value_tuple[1]))

    def get_all_sensors_values(self):
        cmd = Command(number = 153)
        response: bytes
        is_command_succ, response = \
            cmd.send_and_check(self.conn, get_response=True)
        give_cmd(self.ui, cmd.name, is_command_succ)
        if not response: return
        all_sensors_values: Tuple[int] = cmd.decode_response_data(response)
        self.ui.sensors_values_label.setText(str(all_sensors_values))

    '''def old_get_sensor_value(self): #DEPRECATED
        is_command_succ, response\
             = Command(number = 153).send_and_check(25, get_response=True)
        self.ui.status_label.setText(str(is_command_succ))
        sensor_values_tuple = Command(number = 153).decode_response_data(response)
        self.ui.status_label.setText(f'{is_command_succ}, svt: {sensor_values_tuple}')'''

    #----------функции для показаний тензодатчиков -------------

    

    def open_comport(self):
        port_name = self.ui.port_name_ledit.text()
        self.ser = open_port_by_name(port_name)

    def arduino_led_on(self):
        if not self.ser:
            show_error("Open comport first!")
            return
        answer, is_succ = toggle_arduino_led(self.ser, True)
        self.ui.serial_input_ledit.setText(answer)
        self.ui.statusbar.showMessage(str(is_succ))

    def arduino_led_off(self):
        if not self.ser:
            show_error("Open comport first!")
            return
        answer, is_succ = toggle_arduino_led(self.ser, False)
        self.ui.serial_input_ledit.setText(answer)
        self.ui.statusbar.showMessage(str(is_succ))


# -----------------------вспомогательные функции---------------------
def show_error(text: str):
    msg = QMessageBox()
    msg.setIcon(QMessageBox.Critical)
    msg.setText(text)
    msg.exec()

'''def reload_modules():
    reload(commands)
    reload(tcp_client)
    reload(command_makers)'''

Window() #запуск гуйни
# window_2 = Window()