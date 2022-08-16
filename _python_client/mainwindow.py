# developed by Andrew R.

from typing import List, Tuple, Dict, Optional
from importlib import reload
import os
import time

from PyQt5.QtNetwork import QTcpSocket
from PyQt5.QtCore import QTimer
from PyQt5 import uic
from PyQt5.QtWidgets import (
    QApplication, QWidget, QFileDialog, QStatusBar, QLabel, QDoubleSpinBox, 
    QListWidgetItem, QErrorMessage, QMessageBox, QPushButton, QTableWidget
)

from commands import Command
from tcp_client import Connection
from command_makers import *
from window_misc import (
    update_calibration_table, clear_contents_of_calibration_table,
    show_error, show_info
    )
from tenz_serial import Tenz, Tenzes, ComPortUtils
from wheels import crop_float


class Window(object):
    def __init__(self):
        app = QApplication([])
        ui_path = os.path.dirname(os.path.abspath(__file__))
        self.ui = uic.loadUi(os.path.join(ui_path, "mainwindow.ui"))
        self.ui.show()

        self.conn = None

        self.number_of_tenzes: int = 15
            # number_of_tenzes should be a parameter
            # cuz there probably will be more tenzes
        self.tenzes = None
        self.dev_num: int = self.ui.device_number_spinbox.value()
            # dev_num is an alias for devica_number
            #в гуйне дефолтное значение спинбокса было установлено = 0
        self.client_sample_rate: int = self.ui.sample_rate_spinbox.value() #default was 100
        self.oversampling_rate: int = self.ui.oversampling_spinbox.value() #default was 1


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

        #-----------------вкладка калибровки тензодатчиков----------------------
        self.ui.device_number_spinbox.valueChanged.connect(
            self.change_current_device_number)
        self.ui.tenz_tare_button.clicked.connect(
            self.tenz_tare)
        self.ui.tenz_sign_weight_button.clicked.connect(
            self.tenz_sign_weight)
        self.ui.tenz_calibrate_button.clicked.connect(
            self.tenz_calibrate)

        #-----------------вкладка чтения тензодатчиков----------------------

        for clicked_signal in self.ui.units_widget.get_signals_of_clicked_visibility_checkboxes():
            clicked_signal.connect(
                self.prepare_update_for_graphs_visibility
                )

        self.ui.sample_rate_spinbox.valueChanged.connect(
            self.change_sample_rate)
        self.ui.oversampling_spinbox.valueChanged.connect(
            self.change_oversampling_rate)
        self.ui.tenz_start_units_button.clicked.connect(
            self.tenz_start_units)
        self.ui.tenz_stop_units_button.clicked.connect(
            self.tenz_stop_units)

        #----------вкладка установки соединения и отправки сообщений вручную---------
        self.ui.send_hex_message_button.clicked.connect(
            self.send_hex_message)
        self.ui.connect_button.clicked.connect(
            self.make_connection)
        self.ui.disconnect_button.clicked.connect(
            self.close_connection)
        self.ui.tenz_open_comports_button.clicked.connect(
            self.tenz_open_comports)
        self.ui.tenz_close_comports_button.clicked.connect(
            self.tenz_close_comports)

        #-----------------вкладка поиска отправки команд по номеру-----------------
        self.ui.command_number_spinbox.valueChanged.connect(
            self.ui.command_name_ledit.clear)
        self.ui.command_name_ledit.textEdited.connect(
            self.set_null_in_command_number_spinbox)
        self.ui.fetch_command_button.clicked.connect(
            self.fetch_command)
        self.ui.send_command_button.clicked.connect(
            self.send_command)

        exit(app.exec())
    

    #--------------------------------ФУНКЦИИ------------------------------------

    #-----------------------функции для общего раскрытия------------------------

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


    #------------------функции для показаний тензодатчиков----------------------

    def change_current_device_number(self):
        new_device_number: int = self.ui.device_number_spinbox.value()
        if not self.check_device_number_in_tenzes(new_device_number):
            clear_contents_of_calibration_table(self.ui.tenz_calibration_table)
            print(f"Device number {new_device_number} "
                  +"haven't been found in Tenzes")
            self.ui.device_number_spinbox.setValue(self.dev_num)
                # возвратили старое значение в спинбокс
            return
        self.dev_num = new_device_number
        self.redraw_calib_table()
        print(f"Device_number changed to {self.dev_num}")

    def tenz_open_comports(self):
        text: str = self.ui.tenz_open_device_ledit.text()
        if not text:
            # self.tenz = Tenz() #автопоиск порта #deprecated
            self.tenzes = Tenzes()
        elif text:
            devices_numbers = list(map(int, text.split(', ')))
            self.tenzes = Tenzes(devices_numbers)
        self.ui.units_widget.enable_unitswidgets_by_device_numbers(
            self.tenzes.keys()
            )

    def tenz_close_comports(self): #NEED TESTING
        if not self.check_tenzes_dict(): return
        text: str = self.ui.tenz_open_device_ledit.text()
        if not text:
            self.tenzes.close_all()
            del self.tenzes
            self.tenzes = None
            print("All devices closed")
            show_info("Соединение со всеми датчиками разорвано")
        elif text:
            devices_numbers = list(map(int, text.split(', ')))
            self.tenzes.close_some(devices_numbers)
            print("Requested devices closed")
            show_info("Соединение с указанными датчиками разорвано")

    def tenz_tare(self):
        if not self.check_tenz(): return
        self.tenzes[self.dev_num].tare()
        show_info(f"Тензодатчик {self.dev_num} тарирован.\n" + 
            "Сейчас он не должен был быть ничем нагружен")

    def tenz_sign_weight(self):
        if not self.check_tenz(): return
        tenz = self.tenzes[self.dev_num] #CLASS ALIAS NEED HUUGE TESTING (already worked in testing)
        weight: float = float(self.ui.tenz_sign_weight_d_spinbox.value())
        tenz.sign_weight(weight)

        self.redraw_calib_table() #NEED TESTING

        if not tenz.calib_dict.are_scales_converge():
            print("Scales don't converge properly")
            show_info("Значение множителя не сходится с заданной точностью")

    def tenz_calibrate(self):
        if not self.check_tenz(): return
        tenz = self.tenzes[self.dev_num] #CLASS ALIAS NEED HUUGE TESTING (already worked in testing)

        scale: float = tenz.calc_scale()
        tenz.set_scale(scale)
        show_info(f"Калибровка завершена.\nУстановлен множитель {scale}")

    def tenz_start_units(self):
        if not self.check_tenzes_dict(): return
        client_reading_timer_delay: int = self.change_sample_rate()
        self.tenz_get_units_timer = QTimer()
        self.tenz_get_units_timer.timeout.connect(self.get_and_show_units)
        self.tenz_get_units_timer.start(client_reading_timer_delay)
        self.change_oversampling_rate()

    def get_and_show_units(self):
        if not self.check_tenzes_dict(): return
        for tenz in self.tenzes.values():
            tenz.append_weight_point()
        weight_timelines: List[WeightTimeline] = [
            tenz.weight_timeline for tenz in self.tenzes.values() #NEED TESTING
            ]
        self.ui.units_graph_gview.clear()
        self.ui.units_graph_gview.plot_timelines(weight_timelines)
        self.ui.units_widget.update_and_show_all_units(
            self.tenzes.get_last_absolute_units()
            )
        
    def tenz_stop_units(self):
        if not self.check_tenzes_dict(): return
        self.tenz_get_units_timer.stop()
        for tenz in self.tenzes.values():
            tenz.weight_timeline.__del__() #to close logfiles

    def prepare_update_for_graphs_visibility(self):
        graph_visibility_for_each_device: Dict[int, bool] = {}
        for tenz_units_widget in self.ui.units_widget.tenz_units_widgets:
            # alias for check_box_device_number
            ch_box_dev_num: int = \
                tenz_units_widget.device_number
            # alias for check_box_state
            ch_box_state: bool = \
                tenz_units_widget._visibility_checkbox.isChecked()
            graph_visibility_for_each_device[ch_box_dev_num] = ch_box_state
        self.ui.units_graph_gview.update_graphs_visibility(
            graph_visibility_for_each_device
            )
        print("Update for visibility graph is prepared")
        
    
    def change_sample_rate(self):
        new_sample_rate: int = self.ui.sample_rate_spinbox.value()
        minimum_sample_rate: int = 1 
        maximum_sample_rate: int = 100 #протестировать предельное значение
        if new_sample_rate < minimum_sample_rate:
            show_error("Частота отсчетов слишком мала")
            raise ValueError("Частота отсчетов слишком мала")
            self.ui.sample_rate_spinbox.setValue(self.client_sample_rate) #откат
            return
        if new_sample_rate > maximum_sample_rate:
            show_error("Частота отсчетов слишком велика")
            raise ValueError("Частота отсчетов слишком велика")
            self.ui.sample_rate_spinbox.setValue(self.client_sample_rate) #откат
            return
        client_reading_timer_delay: int = int(1000 / new_sample_rate) #in microseconds
        server_reading_timer_delay: int = \
            int(client_reading_timer_delay * (3 / 4))
        for tenz in self.tenzes.values():
            tenz.set_loop_delay(server_reading_timer_delay)
        self.client_sample_rate = new_sample_rate #обновление аттрибута
        print("ARDUINO DELAY WAS SET AS:", server_reading_timer_delay)
        return client_reading_timer_delay

    def change_oversampling_rate(self):
        new_oversampling_rate: int = self.ui.oversampling_spinbox.value()
        minimum_oversampling_rate: int = 1
        maximum_oversampling_rate: int = 30 #можно больше, но зачем?
        if new_oversampling_rate < minimum_oversampling_rate: #оверкилл вообще-то
            show_error("Cлишком мало измерений на отсчет")
            raise ValueError("Cлишком мало измерений на отсчет")            
            self.ui.oversampling_spinbox.setValue(self.oversampling_rate) #откат
            return
        if new_oversampling_rate > maximum_oversampling_rate:
            show_error("Cлишком много измерений на отсчет")
            raise ValueError("Cлишком много измерений на отсчет")
            self.ui.oversampling_spinbox.setValue(self.oversampling_rate) #откат
            return
        for tenz in self.tenzes.values():
            tenz.set_times_to_measur(new_oversampling_rate)
        self.oversampling_rate = new_oversampling_rate #обновление аттрибута
        print("ARDUINO TIMES_TO_MEASUR SET AS:", new_oversampling_rate)

    def check_device_number_in_tenzes(self, device_number: int) -> bool:
        return device_number in self.tenzes.keys()

    def check_tenz(self) -> bool:
        # print(self.dev_num in self.tenzes.keys())
        if self.dev_num == 0: show_error(
            "Сначала нужно выбрать номер подключенного датчика!")
        print("Current KEYS in Tenzes:", self.tenzes.keys())
        # print("DEBUG: DEVNUM:", self.dev_num)
        return self.dev_num in self.tenzes.keys()
        # предполагается, что если с датчиком что-то случилось,
            # он удаляется от словаря Tenzes
    
    def check_tenzes_dict(self) -> bool:
        return bool(self.tenzes)

    def clear_calib_table(self):
        self.ui.tenz_calibration_table.clear()

    def redraw_calib_table(self):
        table = self.ui.tenz_calibration_table #alias
        tenz = self.tenzes[self.dev_num] #alias
        update_calibration_table(table, tenz.calib_dict)

    #-------функции для установки соединения и отправки сообщений вручную-------

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

    


# -----------------------вспомогательные функции---------------------

def is_tenz(tenz: Tenz) -> bool: #DEPRECATED
    raise NotImplementedError("sigle self.tenz WAS REMOVED from Mainwindow")
    if not tenz: 
        # raise TypeError("Create tenz object first!")
        show_error("Серийный порт недоступен!")
        return False
    elif tenz:
        return True

def is_tenzes(tenzes: Tenzes) -> bool: #DEPRECATED
    raise NotImplementedError(
        'Function is deprecated. Try to use "check_device_number_in_tenzes"'
        + "function instead"
        )
    if not tenzes: 
        # raise TypeError("Create Tenzes object first!")
        print("There is no tenzes")
        show_error("Серийный порты недоступны!")
        return False
    elif tenzes:
        return True

async def get_units_n_times(tenz: Tenz, output_label: QLabel): #NEED TESTING
    for _ in range(100):
        # await asyncio.sleep(3)
        if not is_tenz(tenz): return
        units = crop_float(tenz.get_units())
        output_label.setText(f"Вес на ТД1: {units}кг")
        


'''def reload_modules():
    reload(commands)
    reload(tcp_client)
    reload(command_makers)'''


Window() #запуск гуйни
# window_2 = Window()
