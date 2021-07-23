
'''# print(ord('F'))
import struct
print(struct.pack('B', 136))
print(struct.unpack('=B', b'\x88'))'''

# print(f'string and a digit insertion: {4567}')

# print('A' == 'А')

'''test_list_comprehension = [i for i in range(100)]
for test_item in test_list_comprehension:
    print(type_print(test_item ))'''

'''test_dict = {1:(11, 111), 2:(22, 222), 3: (33, 333)}
print(type(test_dict))
print(len(test_dict))

print(test_dict.pop(2))
print(len(test_dict))

for val_1, val_2 in test_dict.values():
    print(val_1, '---', val_2)'''

'''from tenz_serial import CalibrationDict
test_caldict = CalibrationDict()
test_caldict.add_calibration_pair(1., 2.)
test_caldict.add_calibration_pair(1., 2.)
test_caldict.delete_last_calibration_pair()
print(test_caldict)
test_caldict.clear_all_calibration_pairs()
print(test_caldict)'''

'''td = {1: 1}
print(bool(td))
print(len(td))'''

# print(float("34.65") + 23)

'''for i in range(0): print(i)

test_mapping = map(int, ('1', '2', '3'))

print(enumerate((1, 2, 43)))
print(max((1, 2.3, 3.4)))


new_val = float("{:.2f}".format(5.23456789078))
print(new_val)'''


'''from tenz_serial import Tenz
test_tenz = Tenz(12)
test_tenz.comport.open()
test_tenz.comport.read_line()
test_tenz.comport.close()'''

'''test_dict = dict(enumerate(list(range(10))))
for test_key in test_dict.keys():
    print(test_key)'''

'''print("SPP Dev".encode("utf-8").hex())

import logging as log
log.warning("warning_text")
log.info("info_text")

import pathlib
dir_path_str = pathlib.Path(__file__).parent.absolute()
# F = open(f"{dir_path_str}\\05/05/21 19:26_weights_expansion.log", 'w')
F = open(f"{dir_path_str}\\00.00.00 00-00_test.log", "w")
F.write("test")'''

'''print("Сделать свои обертки для классов")

import winreg
reg_root_key = winreg.HKEY_CLASSES_ROOT

reg_handle = winreg.CreateKey(reg_root_key)
print("REG HANDLE WORKED:", reg_handle)

levels = [
    "HKEY_LOCAL_MACHINE",
    "SYSTEM", 
    "CurrentControlSet",
    "Enum",
    "BTHENUM"
]

for '''

# print(list({1:2, 3:4}.values()))

# print("".join(['1', '2', '3'][0:2]))

'''import os
print(os.listdir())

from os import listdir
print(listdt())

from os import listdir as lstd
print(lstd())'''

'''empty_dict = {}
empty_dict[1] = 2
empty_dict[2] = 0
empty_dict[1] = 200
print(empty_dict)

a, b, c, d = 1, 2, 3, 4
lsttttb = [a, b, c, d]
print(lsttttb)
lsttttb[2] += 100
print(lsttttb)

print(len(empty_dict))

class TestClass():
    def __init__(self, var: int):
        self.var: int = var

test_inst = TestClass(10)

alias_for_test_inst = test_inst
print(test_inst.var)

alias_for_test_inst.var += 234567
print(alias_for_test_inst.var)
print(test_inst.var) #HOWWW? very convenient though'''

'''from typing import List

class Tenz():
    def __init__(self, var: int):
        self.var: int = var
        # self.int_var: int = int_var
    
    def __str__(self):
        return f"TENZ NUMBER {self.var}"

class MyDict(dict):
    def __init__(self, tenzes: List[Tenz]):
        for tenz in tenzes:
            self[tenz.var] = tenz
        # del self[2]
        print(self)

    def __str__(self):
        for key, value in self.items():
            print(key, ": ",  value)'''
        
# MyDict([Tenz(i) for i in range(3)])

import time 
print(type(time.time())) #float

import serial.tools.list_ports as list_serials
import serial

def get_comports_list():
        port_list = list_serials.comports(include_links=False)
        print("------- Here are the ports -------")
        for port in port_list: print(port)
        return port_list

def open_serial():
    port_str: str = 'COM20'
    try:
        self._ser = serial.Serial(port_str)
        print(f'{port_str} opened ***\\')
    except serial.serialutil.SerialException:
        print(f'{port_str} was not opened! It was not found most probably')

#-----------------------------------------------------
def open_serial_without_catch():
    port_str: str = 'COM10'
    self._ser = serial.Serial(port_str)
    print("open_serial_without_catch worked")


# open_serial()
# print(get_comports_list())
open_serial_without_catch() 
    # получаю в ебло PermissionError(13, 'Отказано в доступе.', None, 5)
