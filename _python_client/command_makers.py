from PyQt5.QtWidgets import (
    QWidget, QMessageBox
)

from commands import Command

#-------------------ФУНКЦИИ ДЛЯ ВЫПОЛНЕНИЯ КОМАНД-------------------

#---------------------------главная вкладка----------------------------
def expand_all(ui, conn):
    cmd = Command(number = 10)
    give_cmd(ui, cmd.name, cmd.send_and_check(conn))

def contract_all(ui, conn):
    cmd = Command(number = 20)
    give_cmd(ui, cmd.name, cmd.send_and_check(conn))

def all_motors_stop(
        ui, conn, *, button = None, 
        show_status: bool = True, 
        reset_buttons: bool = True):
    cmd = Command(number = 30)
    if show_status:
        give_cmd(ui, cmd.name, cmd.send_and_check(conn))
    if not show_status: 
        give_cmd_no_status(ui, cmd.name, cmd.send_and_check(conn))
    if reset_buttons: 
        set_all_motor_buttons_to_default(ui)
        if button: button.setChecked(True) #костыль! 
        '''# Обратно делаем кнопку нажатой 
            # после того, как она была сброшена в дефолтное состояние 
            # (вместе со всеми остальными кнопками)'''

#---------------------------вкладка рефлектора----------------------------
def reflector_expand(ui, conn):
    cmd = Command(number = 41)
    give_cmd(ui, cmd.name, cmd.send_and_check(conn))

def reflector_contract(ui, conn):
    cmd = Command(number = 51)
    give_cmd(ui, cmd.name, cmd.send_and_check(conn))

def reflector_upper_motor_open(ui, conn):
    cmd = Command(number = 61)
    motor_number: int = 0 #upper reflector motor
    give_cmd(
        ui, 
        cmd.name, 
        cmd.send_and_check(conn, motor_number))

def reflector_upper_motor_close(ui, conn):
    cmd = Command(number = 71)
    motor_number: int = 0 #upper reflector motor
    give_cmd(
        ui, 
        cmd.name, 
        cmd.send_and_check(conn, motor_number))

def reflector_lower_motor_open(ui, conn):
    cmd = Command(number = 61)
    motor_number: int = 1 #lower reflector motor
    give_cmd(
        ui,
        cmd.name,
        cmd.send_and_check(conn, motor_number))

def reflector_lower_motor_close(ui, conn):
    cmd = Command(number = 71)
    motor_number: int = 1 #lower reflector motor
    give_cmd(
        ui,
        cmd.name,
        cmd.send_and_check(conn, motor_number))

#----------------------------вкладка стенда----------------------------

def bench_expand(ui, conn):
    cmd = Command(number = 82)
    give_cmd(ui, cmd.name, cmd.send_and_check(conn))

def bench_contract(ui, conn):
    cmd = Command(number = 92)
    give_cmd(ui, cmd.name, cmd.send_and_check(conn))

def bench_motor_open(ui, conn):
    cmd = Command(number = 112)
    motor_number: int = ui.motor_to_move_number_spinbox.value()
    give_cmd(
        ui,
        cmd.name,
        cmd.send_and_check(conn, motor_number))

def bench_motor_close(ui, conn):
    cmd = Command(number = 122)
    motor_number: int = ui.motor_to_move_number_spinbox.value()
    give_cmd(
        ui,
        cmd.name,
        cmd.send_and_check(conn, motor_number))


#----------------------------вкладка датчиков----------------------------

#tuple of all command makers for fast importing
'''command_maker_funcs = [
    expand_all,
    contract_all,
    all_motors_stop,
    reflector_expand,
    reflector_contract,
    reflector_upper_motor_open,
    reflector_upper_motor_close,
    reflector_lower_motor_open,
    reflector_lower_motor_close,
]'''
#------------------------------прочие функции----------------------------
def give_cmd(ui: QWidget, cmd_name: str, is_cmd_succ: bool):
    status(
        ui, 
        f'command "{cmd_name}" is ' 
        + 'not '*(not is_cmd_succ) + 'succsesful.')
    if not is_cmd_succ: show_error(f'Error in "{cmd_name}" comand!')

def give_cmd_no_status(ui: QWidget, cmd_name: str, is_cmd_succ: bool):
    if not is_cmd_succ: show_error(f'Error in "{cmd_name}" comand!')

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