#модуль с командами
from typing import List, Tuple, Dict, Optional, Union
import struct
import socket

from tcp_client import Connection


class Command(object):
    def __init__(self, *, number: int = None, name: str = None):
        self.init_err_info: Optional[str] = None
        self.header: Optional[bytes] = None
        self.is_there_info_field: Optional[bool] = None
        self.is_there_data_field_in_response: Optional[bool] = None
        if number == 0: #in boolean expression 0 equals None. It can confuse a lot 
            self.init_err_info = ('Wrong command number! '
                +'0 is forbidden value for a command number')
            print(self.init_err_info)
            return
        if not number: #init by name
            self.name = name
            self.number = command_num_from_name(name)
            if not self.number:
                self.init_err_info = (
                    f'Command by the name of "{name}" was not found')
                print(self.init_err_info)
                return
        if not name: #init by number
            if type(number) != int:
                self.init_err_info = (
                    'Wrong command number! Command number must be an integer')
                print(self.init_err_info)
                return
            self.number = number
            self.name = command_name_from_num(number)
            if not self.name:
                self.init_err_info = (
                    f'Command by the number of {number} was not found')
                print(self.init_err_info)
                return
        if number and name:
            self.init_err_info = (
                'Unexpected command constructor args! '
                +'Either number or name should be provided. Not both of them')
            print(self.init_err_info)
            return
        # if __init__ err_info is empty then "command" instance should be 
        # constructed and it should has proper command_name and command_number

    def __str__(self) -> str:
        return f'--- Command "{self.name}" (number {self.number})'

    '''def command_header_from_name(self) -> bytes:
        for command_tuple in command_info_list:
            return command_tuple[2] if command_tuple[1] == self.number else None'''

    def make_bytes_message(self, *info_field_params) -> bytes:
        for command_tuple in command_info_list:
            if command_tuple[1] == self.number:
                self.is_there_info_field: bool = command_tuple[3]
                self.header: bytes = bytes(command_tuple[2]) #NEED TESTING
        if not self.is_there_info_field: #если у команды нет "информационного поля"
            bytes_message = self.header
        elif self.is_there_info_field: #если у команды есть "информационное поле"
            info_field: Optional[bytes] = None
            if self.number == 61:
                info_field = reflector_motor_open_info(
                    self.name, *info_field_params)
            if self.number == 71:
                info_field = reflector_motor_close_info(
                    self.name, *info_field_params)
            if self.number == 102:
                info_field = bench_tension_setup_info(
                    self.name, *info_field_params)
            if self.number == 112:
                info_field = bench_motor_open_info(
                    self.name, *info_field_params)
            if self.number == 122:
                info_field = bench_motor_close_info(
                    self.name, *info_field_params)
            if self.number == 132:
                info_field = bench_motor_tension_setup_info(
                    self.name, *info_field_params)
            if self.number == 143:
                info_field = get_sensor_value_info(
                    self.name, *info_field_params)
            if not info_field: #если инф. поле так и не сформировалось
                print('info_field was not formed')
                return
            bytes_message = concatenate_bytes(self.header, info_field)
        return bytes_message

    def check_response(self, actual_response: bytes) -> bool:
        if self.number == 143:
            is_command_succ = check_get_sensor_value(actual_response)
        elif self.number == 153:
            is_command_succ = check_get_all_sensors_values(actual_response)
        else: #standard response (without info_field)
            for command_tuple in command_info_list:
                if command_tuple[1] == self.number:
                    command_code_in_header: int = int(bytearray(command_tuple[2])[1])
                    ideal_response: bytearray = standard_response
                    ideal_response[1] = command_code_in_header
            is_command_succ = actual_response == ideal_response     
        return is_command_succ

    def send_and_check(
            self, conn: socket.socket, *info_field_params,
            get_response: bool = False) -> Union[Tuple[bool, bytes], bool]:
        message: bytes = self.make_bytes_message(*info_field_params)
        if not conn: 
            print('No connection. Make connection first.')
            return
        if not message: 
            print('Bytes message was not formed')
            return
        response: bytes = conn.send_message(message)
        is_command_succ = self.check_response(response)
        if not is_command_succ: 
            print(f'WARNING! Command {self.name} have not worked properly')
        return (is_command_succ, response) if get_response else is_command_succ 

    def decode_response_data(self, response: bytes) -> Optional[Tuple[int, ...]]:
        btray_response = bytearray(response)
        for command_tuple in command_info_list:
            if command_tuple[1] == self.number:
                self.is_there_data_field_in_response: bool = command_tuple[4]
        if not self.is_there_data_field_in_response:
            print("You've tried to decode data_field of the command which "
                + " doesn't have any data_field")
            return
        elif self.is_there_data_field_in_response:
            if self.number == 143:
                data_field = btray_response[6:]
                if len(data_field) != 5:
                    print('Wrong data_field length in response '
                        +f'for "{self.name}" command.')
                decoded_response_data = tuple(struct.unpack('=Bl', data_field))
            if self.number == 153:
                data_field = btray_response[6:]
                if len(data_field) != 104:
                    print('Wrong data_field length in response '
                          + f'for "{self.name}" command.')
                decoded_response_data = tuple(struct.unpack('l'*26, data_field))
        return decoded_response_data
#-------------------------функции для класса команд---------------------

def command_num_from_name(name: str) -> Optional[int]:
    for command_tuple in command_info_list:
        if command_tuple[0] == name:
            return command_tuple[1]

def command_name_from_num(number: int) -> Optional[str]:
    for command_tuple in command_info_list:
        if command_tuple[1] == number:
            return command_tuple[0]

def concatenate_bytes(bytes_1: bytes, bytes_2: bytes) -> bytes:
    # NEED TESTING
    return bytes(bytearray(bytes_1) + bytearray(bytes_2))

#-----------------------------список команд------------------------

command_info_list: List[Tuple[str, int, str, bool]] = [
# (name_of_the_command, command_number, command_header, 
    # is there additional info, is response standard)
# number regarded as a key parameter (therefore all numbers must be unique)
# more than that, command names editing won't break this module. 
    # Though, it'll break others  
    ('expand_all'               , 10,  b'\x55\x01\x00\x00\x00\x00', False, False), #01h
    ('contract_all'             , 20,  b'\x55\x02\x00\x00\x00\x00', False, False), #02h
    ('all_motors_stop'          , 30,  b'\x55\x03\x00\x00\x00\x00', False, False), #03h 

    ('reflector_expand'         , 41,  b'\x55\x14\x00\x00\x00\x00', False, False), #14h
    ('reflector_contract'       , 51,  b'\x55\x15\x00\x00\x00\x00', False, False), #15h
    ('reflector_motor_open'     , 61,  b'\x55\x16\x01\x00\x00\x00', True , False), #16h
    ('reflector_motor_close'    , 71,  b'\x55\x17\x01\x00\x00\x00', True , False), #17h

    ('bench_expand'             , 82,  b'\x55\x28\x00\x00\x00\x00', False, False), #28h
    ('bench_contract'           , 92,  b'\x55\x29\x00\x00\x00\x00', False, False), #29h
    ('bench_tension_setup'      , 102, b'\x55\x2A\x04\x00\x00\x00', True , False), #2Ah
    ('bench_motor_open'         , 112, b'\x55\x2B\x01\x00\x00\x00', True , False), #2Bh
    ('bench_motor_close'        , 122, b'\x55\x2C\x01\x00\x00\x00', True , False), #2Ch
    ('bench_motor_tension_setup', 132, b'\x55\x2D\x05\x00\x00\x00', True , False), #2Dh

    ('get_sensor_value'         , 143, b'\x55\x3C\x01\x00\x00\x00', True , True), #3Ch
    ('get_all_sensors_values'   , 153, b'\x55\x00\x00\x00\x00\x00', False, True), #00h 
    # (last command moved to the bootom to exclude 0 command)
]

standard_response: bytearray = bytearray(b'\x55\xff\x02\x00\x00\x00\x01\xff')
# standard_response[2] = 16*15+13


#----преобразователи параметров команды в информационное поле битового сообщения----

def reflector_motor_open_info(cmd_name: str, *info_field_params) -> bytes:
    if len(info_field_params) != 1: 
        print(f'Wrong parameters for "{cmd_name}" command. '
             +'Wrong length of parameters list')
        return
    motor_number: int = info_field_params[0]
    if type(motor_number) is not int:
        print(f'Wrong parameters for "{cmd_name}" command. '
             +'Parameter must be an int')
        return
    if motor_number not in [0, 1]:
        print(f'Wrong parameters for "{cmd_name}" command. '
             +'Wrong parameter value')
        return
    info_field: bytes = struct.pack('B', motor_number)
    print(f'info field for "{cmd_name}" command is', info_field)
    return info_field

def reflector_motor_close_info(cmd_name: str, *info_field_params) -> bytes:
    if len(info_field_params) != 1: 
        print(f'Wrong parameters for "{cmd_name}" command. '
             +'Wrong length of parameters list')
        return
    motor_number: int = info_field_params[0]
    if type(motor_number) is not int:
        print(f'Wrong parameters for "{cmd_name}" command. '
             +'Parameter must be an int')
        return
    if motor_number not in [0, 1]:
        print(f'Wrong parameters for "{cmd_name}" command. '
             +'Wrong parameter value')
        return
    info_field: bytes = struct.pack('B', motor_number)
    print(f'info field for "{cmd_name}" command is', info_field)
    return info_field

def bench_tension_setup_info(cmd_name: str, *info_field_params) -> bytes:
    if len(info_field_params) != 1: 
        print(f'Wrong parameters for "{cmd_name}" command. '
             +'Wrong length of parameters list')
        return
    tension_value: int = info_field_params[0]
    if type(tension_value) is not int:
        print(f'Wrong parameters for "{cmd_name}" command. '
             +'Parameter must be an int')
        return
    if (tension_value < -(2**31)) or (tension_value > 2**31 - 1 ):
        print(f'Wrong parameters for "{cmd_name}" command. '
             +'Wrong parameter value')
        return
    info_field: bytes = struct.pack('l', tension_value)
    print(f'info field for "{cmd_name}" command is', info_field)
    return info_field

def bench_motor_open_info(cmd_name: str, *info_field_params) -> bytes:
    if len(info_field_params) != 1: 
        print(f'Wrong parameters for "{cmd_name}" command. '
             +'Wrong length of parameters list')
        return
    motor_number: int = info_field_params[0]
    if type(motor_number) is not int:
        print(f'Wrong parameters for "{cmd_name}" command. '
             +'Parameter must be an int')
        return
    if motor_number not in list(range(2, 26)): #26 is excluded
        print(f'Wrong parameters for "{cmd_name}" command. '
             +'Wrong parameter value')
        return
    info_field: bytes = struct.pack('B', motor_number)
    print(f'info field for "{cmd_name}" command is', info_field)
    return info_field

def bench_motor_close_info(cmd_name: str, *info_field_params) -> bytes:
    if len(info_field_params) != 1: 
        print(f'Wrong parameters for "{cmd_name}" command. '
             +'Wrong length of parameters list')
        return
    motor_number: int = info_field_params[0]
    if type(motor_number) is not int:
        print(f'Wrong parameters for "{cmd_name}" command. '
             +'Parameter must be an int')
        return
    if motor_number not in list(range(2, 26)):
        print(f'Wrong parameters for "{cmd_name}" command. '
             +'Wrong parameter value')
        return
    info_field: bytes = struct.pack('B', motor_number)
    print(f'info field for "{cmd_name}" command is', info_field)
    return info_field

def bench_motor_tension_setup_info(cmd_name: str, *info_field_params) -> bytes:
    if len(info_field_params) != 2: 
        print(f'Wrong parameters for "{cmd_name}" command. '
             +'Wrong length of parameters list')
        return
    motor_number: int = info_field_params[0]
    if type(motor_number) is not int:
        print(f'Wrong parameters for "{cmd_name}" command. '
             +'Parameter must be an int')
        return
    if motor_number not in list(range(2, 26)):
        print(f'Wrong parameters for "{cmd_name}" command. '
             +'Wrong parameter value')
        return
    tension_value: int = info_field_params[1]
    if type(tension_value) is not int:
        print(f'Wrong parameters for "{cmd_name}" command. '
             +'Parameter must be an int')
        return
    if (tension_value < -(2**31)) or (tension_value > 2**31 - 1 ):
        print(f'Wrong parameters for "{cmd_name}" command. '
             +'Wrong parameter value')
        return
    info_field: bytes = struct.pack('Bl', motor_number, tension_value)
    print(f'info field for "{cmd_name}" command is', info_field)
    return info_field

def get_sensor_value_info(cmd_name: str, *info_field_params) -> bytes:
    if len(info_field_params) != 1: 
        print(f'Wrong parameters for "{cmd_name}" command. '
             +'Wrong length of parameters list')
        return
    sensor_number: int = info_field_params[0]
    if type(sensor_number) is not int:
        print(f'Wrong parameters for "{cmd_name}" command. '
             +'Parameter must be an int')
        return
    if sensor_number not in list(range(0, 25)):
        print(f'Wrong parameters for "{cmd_name}" command. '
             +'Wrong parameter value')
        return
    info_field: bytes = struct.pack('B', sensor_number)
    print(f'info field for "{cmd_name}" command is', info_field)
    return info_field


#-------------проверка ответа сервера (response check funcs)-------------

def check_get_sensor_value(actual_response: bytes) -> bool:
    actual_response_btray = bytearray(actual_response)
    ideal_response_prefix = bytearray(b'\x55\x3C\x05\x00\x00\x00')
    ideal_response_length: int = 11
    is_command_succ = \
        (len(actual_response_btray) == ideal_response_length) and \
        (ideal_response_prefix in actual_response_btray)
    return is_command_succ

def check_get_all_sensors_values(actual_response: bytes) -> bool:
    actual_response_btray = bytearray(actual_response)
    ideal_response_prefix = bytearray(b'\x55\x00\x68\x00\x00\x00')
    ideal_response_length: int = 110
    is_command_succ = \
        (len(actual_response_btray) == ideal_response_length) and \
        (ideal_response_prefix in actual_response_btray)
    return is_command_succ

#-------------response data decode funcs-----------------------
