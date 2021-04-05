
'''# print(ord('F'))
import struct
print(struct.pack('B', 136))
print(struct.unpack('=B', b'\x88'))'''

# print(f'string and a digit insertion: {4567}')

# print('A' == 'А')

'''test_list_comprehension = [i for i in range(100)]
for test_item in test_list_comprehension:
    print(type_print(test_item ))'''

test_dict = {1:(11, 111), 2:(22, 222), 3: (33, 333)}
print(type(test_dict))
print(len(test_dict))

print(test_dict.pop(2))
print(len(test_dict))

for val_1, val_2 in test_dict.values():
    print(val_1, '---', val_2)

'''from tenz_serial import CalibrationDict
test_caldict = CalibrationDict()
test_caldict.add_calibration_pair(1., 2.)
test_caldict.add_calibration_pair(1., 2.)
test_caldict.delete_last_calibration_pair()
print(test_caldict)
test_caldict.clear_all_calibration_pairs()
print(test_caldict)'''

td = {}
print(bool(td))
