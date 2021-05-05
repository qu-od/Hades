
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

print("SPP Dev".encode("utf-8").hex())

import logging as log
log.warning("warning_text")
log.info("info_text")

import pathlib
dir_path_str = pathlib.Path(__file__).parent.absolute()
# F = open(f"{dir_path_str}\\05/05/21 19:26_weights_expansion.log", 'w')
F = open(f"{dir_path_str}\\00.00.00 19-26_weights_expansion.log", "w")
F.write("test")