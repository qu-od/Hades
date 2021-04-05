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
        calib_table: QTableWidget, calib_dict):
    calib_table.clear()
    for i in range(calib_dict.values()):
        weight, value = calib_dict[i]
        weight_twi = QTableWidgetItem(str(weight))
        value_twi = QTableWidgetItem(str(value))
        calib_table.insertRow(i)
        calib_table.setItem(i, 1, weight_twi)
        calib_table.setItem(i, 1, value_twi)
