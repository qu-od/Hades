from typing import List, Tuple, Dict, Optional
import struct
import time

import serial.tools.list_ports as list_serials
import serial

'''def toggle_arduino_led(ser: serial.Serial, is_turn_on: bool) -> Tuple[str, bool]:
    # compatible with bt_test.ino program
    ser.write(b'1') if is_turn_on else ser.write(b'0')
    ser.flushInput()
    answer: str = ser.readline().decode("utf-8")
    is_succ: bool = False
    if (is_turn_on == True)  and  (answer is "LED: ON"): is_succ = True
    if (is_turn_on == False) and (answer is "LED: OFF"): is_succ = True        
    return answer, is_succ'''

def get_comports_list():
    port_list = list_serials.comports(include_links=False)
    print("------- Here are the ports -------")
    for port in port_list: print(port)
    return port_list


#--------------------------------CLASSES FOR TENZ----------------------------------

class ComPort(object):
    def __init__(self, comport_number: int, name: str = None, baudrate: int = 19200):
        self._ser: Optional[serial.Serial] = None
        self._number: int = comport_number
        self._baudrate: int = baudrate
        self.name: Optional[str] = name

    def __str__(self): return f"PORT COM-{self._number}" #to ease debug messages
    
    #---------------------------методы для пересылок----------------------------
    def open(self):
        try:
            self._ser = serial.Serial(f'COM{self._number}') #self means "COM1" for COM1 port
            print(f'{self} opened ***\\')
        except serial.serialutil.SerialException:
            print(f'{self} was not opened! It was not found most probably')

    def flush_input(self):
        if self._ser:
            self._ser.flushInput()
            print('Input flushed')
    
    def close(self):
        if self._ser: 
            self._ser.close()
            self._ser = None
            print(f'{self} closed ___/')
        else: 
            print(f'{self} already has been closed.')
            return

    def write_char(self, char: str): #string must contain only one symbol
        if self._ser: self._ser.write(char.encode("utf-8"))
        print(f'--- Char IN {self} --- : {char}')

    def write_bytes(self, data: bytes):
        self._ser.write(data)
        print(f'--- Line IN {self} --- : {data}')

    def write_line(self, line: str):
        self._ser.write((line + '\n').encode("utf-8"))
        print(f'--- Line IN {self} --- : {line}')

    def read_bytes(self, bytes_number) -> bytes:
        data: bytes = self._ser.read(size = bytes_number)
        print(f'--- FROM {self} --- :', data)
        return data

    def read_line(self) -> str:
        line: str = self._ser.readline().decode("utf-8")
        print(f'--- FROM {self} --- :', line[:-1])
        return line


    #-------------------------CALIBRATION PAIR CLASS----------------------------

class CalibrationDict(dict):
    def __init__(self):
        # self_type = Dict[int, Tuple[float, float]]
        print("Calibration dict created")

    def add_calibration_pair(self, weight: float, value: float):
        calib_pairs_number = self.__len__()
        self[calib_pairs_number+1] = weight, value
        print('Calibration pair added')

    def clear_all_calibration_pairs(self):
        self.clear()
        print('Calibration pairs cleared')

    def delete_last_calibration_pair(self):
        calib_pairs_number = self.__len__()
        deleted_pair: tuple = self.pop(calib_pairs_number)
        print("Deleted calibration pair is", deleted_pair)

    def dumb_mean_scale_for_tenz(self) -> float:
        scales: list = [value / weight for weight, value in self.values()]
        # мышца "а почему-бы и нет" прокачана
        return sum(scales) / len(scales)


#---------------------------------TENZ CLASS ITSELF-----------------------------

class Tenz(object):

    def __init__(self, comport_number: int):
        self.comport = ComPort(comport_number)
        self.header: int = 42 #key for tenz commands
        self.calib_dict = CalibrationDict()

    def exec_command(
            self, command_number: int, 
            data_value: float = 0.):
        #now size of data_value is 4 bytes (signed int)
        #data_value must be an optional field to make most commands 3 times shorter 
        self.comport.write_bytes(
            struct.pack('=2Bf', self.header, command_number, data_value)
        )

        response_tuple: Tuple[int, int, float]
        response_tuple = struct.unpack('=2Bf', self.comport.read_bytes(6)) #NEED TESTING!
        response_header, error_code, response_data_value = response_tuple
        print('DECODED RESPONSE:', response_header, error_code, response_data_value)

        #also prints response in console
        if error_code != 0: 
            print(f'ERROR NUMBER {error_code} OCCURED ON ARDUINO')
            return
        elif error_code == 0: 
            return response_data_value
    
    def sign_weight(self, weight_in_kilos: float = 1.):
        self.calib_dict.add_calibration_pair(weight_in_kilos, self.get_value())

    def calc_scale(self) -> float:
        if not self.calib_dict: 
            print("Calibration dict is empty! Can't calculate scale for tenz.")
            return
        return self.calib_dict.dumb_mean_scale_for_tenz()

    #---------------------------command methods---------------------------------
    def tare(self):
        self.exec_command(0)

    def get_value(self) -> float:
        value: float = self.exec_command(1)
        return value

    def set_scale(self, scale: float):
        self.exec_command(2, scale)

    def get_units(self) -> float:
        units: float = self.exec_command(3)
        return units

    def set_loop_delay(self):
        pass

    def flush_arduino_serial_buffer_input_and_output(self):
        pass

    def force_set_offset(self):
        pass

    def get_info(self):
        pass



#--------------------------------MULTIPLE PORTS CLASS----------------------------------

'''class TenzList(list):
    def __init__(self, *ports):
        pass
        self.ports: list = list(ports)

    def read_ports_simultaneously(*comports_names):
        pass
        ser_list = [serial.Serial(comport_name) 
            for comport_name in comports_names]
        for ser in ser_list: print(ser)
        for _ in range(100):
            read_line_from_serial(ser_list[0])
            read_line_from_serial(ser_list[1])
        # map(read_line_from_serial, ser_list)'''


#-----------------------------------MAIN FOR TESTING-------------------------------------
def calibration_test():
    tenz = Tenz(11)
    tenz.comport.open()

    tenz.tare()

    time.sleep(5)
    tenz.sign_weight(weight_in_kilos = 1.)
    time.sleep(5)
    tenz.sign_weight(weight_in_kilos = 2.)
    time.sleep(5)
    tenz.sign_weight(weight_in_kilos = 3.)

    tenz.set_scale(tenz.calc_scale())

    for _ in range(100):
        print(tenz.get_units())

    tenz.comport.close()


if __name__ == '__main__':
    calibration_test()





