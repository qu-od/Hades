from typing import Tuple, List, Optional

from PyQt5.QtWidgets import (
    QWidget, QMessageBox, QTableWidget, QTableWidgetItem
)
from tenz_serial import Tenz

#--------------------------разные функции для окошка--------------------------

def show_error(text: str):
    msg = QMessageBox()
    msg.setIcon(QMessageBox.Critical)
    msg.setText(text)
    msg.exec()

def show_info(text: str):
    msg = QMessageBox()
    msg.setIcon(QMessageBox.Information)
    msg.setText(text)
    msg.exec()

def status(ui: QWidget, status_message: str): #alias
    ui.statusbar.showMessage(status_message)

def set_all_motor_buttons_to_default(ui):
    motor_buttons_info = [
        (ui.expand_all_button     , 'Раскрывать всё'),
        (ui.contract_all_button   , 'Складывать всё'),
        # (ui.all_motors_stop_button здесь не нужна),

        (ui.reflector_expand_button           , 'Раскрывать'),
        (ui.reflector_contract_button         , 'Складывать'),
        (ui.reflector_upper_motor_open_button , 'Открывать'),
        (ui.reflector_upper_motor_close_button, 'Закрывать'),
        (ui.reflector_lower_motor_open_button , 'Открывать'),
        (ui.reflector_lower_motor_close_button, 'Закрывать'),

        (ui.bench_expand_button     , 'Раскрывать'),
        (ui.bench_contract_button   , 'Складывать'),
        (ui.bench_motor_open_button , 'Открывать'),
        (ui.bench_motor_close_button, 'Закрывать')
    ]
    for button, default_text in motor_buttons_info:
        button.setText(default_text)
        button.setChecked(False)
    print('All buttons have been set into default state (is_checked and text)')

def update_calibration_table(
        table: QTableWidget, calib_dict):
    table.clear() #clear items in table
    number_of_rows: int = table.rowCount()
    for _ in range(number_of_rows): table.removeRow(0)
    for _ in range(len(calib_dict)): #рисуем колонки
        table.insertRow(table.rowCount())
    for i in range(len(calib_dict)): #заполняем колонки
        weight, value = calib_dict[i]
        scale = value / weight
        set_row_with_floats_tuple(table, i, weight, value, scale)
        QTableWidget.removeRow

def clear_contents_of_calibration_table(table: QTableWidget):
    table.clearContents() #NEED TESTING


def set_row_with_floats_tuple(
        table: QTableWidget, row_number: int, *values: Tuple[float]):
    for i, value in enumerate(values):
        value_twi = QTableWidgetItem(str(value))
        table.setItem(row_number, i, value_twi)


