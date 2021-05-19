from typing import List, Tuple, Dict, Optional
import struct
import time
import winreg

import serial.tools.list_ports as list_serials
import serial

from wheels import crop_float

'''def toggle_arduino_led(ser: serial.Serial, is_turn_on: bool) -> Tuple[str, bool]:
    # compatible with bt_test.ino program
    ser.write(b'1') if is_turn_on else ser.write(b'0')
    ser.flushInput()
    answer: str = ser.readline().decode("utf-8")
    is_succ: bool = False
    if (is_turn_on == True)  and  (answer is "LED: ON"): is_succ = True
    if (is_turn_on == False) and (answer is "LED: OFF"): is_succ = True        
    return answer, is_succ'''

#--------------------------------CLASSES FOR TENZ----------------------------------

class ComPort():
    def __init__(self, comport_number: int, baudrate: int = 19200):
        self._ser: Optional[serial.Serial] = None
        self._number: int = comport_number
        self._baudrate: int = baudrate

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
            # self = None #NEED HUGE TESTING
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


class ComPortUtils(): #NEED TESTING #есть костыли
    def __init__(self):
        self.info = "Service functions for comports setup"

    def get_comports_list(self):
        port_list = list_serials.comports(include_links=False)
        print("------- Here are the ports -------")
        for port in port_list: print(port)
        return port_list
    
    def _print_some_comport_info(self, comport):
        print("\n_________NEW_COMPORT_____________")
        print(comport.name)
        print(comport.hwid)

    def get_names_and_ports_from_registry(self):
        reg_root_key = winreg.HKEY_CLASSES_ROOT
        reg_handle = winreg.CreateKey(reg_root_key)
        print("REG HANDLE WORKED:", reg_handle)
        
        key_path = (R"Компьютер\HKEY_LOCAL_MACHINE\\SYSTEM\CurrentControlSet" +
                "\Enum\BTHENUM\Dev_002113002876"+
                "\\7&13438a0b&1&BluetoothDevice_002113002876")
        key_name = "FriendlyName"
        tenz_names_list: List[str] = []
        port_numbers_list: List[int] = []

        return tenz_names_list, port_numbers_list

    def get_tenz_comports_numbers(self) -> List[int]: #NEED TESTING
        port_list = list(list_serials.comports())
        outgoing_ports_numbers = []
        for port in port_list:
            # self._print_some_comport_info(port)
            if port.hwid.endswith("C00000000"): 
                # print(f"Looks like {port.name} it's outgoing")
                outgoing_ports_numbers.append(port.name.split("COM")[-1])
        if len(outgoing_ports_numbers) == 0:
            print("No suitable ports found!")
            return
        elif len(outgoing_ports_numbers) > 0:
            print(f"{len(outgoing_ports_numbers)} outgoing ports have been found")
            print("Вот они, слева направо:", outgoing_ports_numbers)
            return outgoing_ports_numbers
    
    def find_tenz_comport_number(self) -> int: #DEPRECATED
        outgoing_ports_numbers = self.get_outgoing_ports_numbers()
        if len(outgoing_ports_numbers) == 0:
            print("No suitable ports found!")
            return
        elif len(outgoing_ports_numbers) == 1:
            print("Outgoing port has been found")
            outgoing_port_number: int = int(outgoing_ports_numbers[0].name.split("COM")[-1])
            return outgoing_port_number
        elif len(outgoing_ports) > 1:
            print("Cannot pick particular outgoing port! There are too many")
            return


    #-------------------------CALIBRATION PAIR CLASS----------------------------

class CalibrationDict(dict):
    def __init__(self):
        # self_type = Dict[int, Tuple[float, float]]
        print("Calibration dict created")

    def add_calibration_pair(self, weight: float, value: float):
        calib_pairs_number = self.__len__()
        self[calib_pairs_number] = weight, value #STARTING KEYS FROM ZERO
        print('Calibration pair added')

    def clear_all_calibration_pairs(self):
        self.clear()
        print('Calibration pairs cleared')

    def delete_last_calibration_pair(self):
        calib_pairs_number = self.__len__()
        deleted_pair: tuple = self.pop(calib_pairs_number)
        print("Deleted calibration pair is", deleted_pair)

    def dumb_scales_tuple_for_tenz(self) -> Tuple[float]:
        scales = tuple([value / weight for weight, value in self.values()])
        # мышца "а почему-бы и нет" прокачана
        return scales

    def dumb_mean_scale_for_tenz(self) -> float:
        scales = self.dumb_scales_tuple_for_tenz()
        return crop_float(sum(scales) / len(scales))

    def are_scales_converge(self, convergence_rate: float = 0.9) -> bool:
        scales = self.dumb_scales_tuple_for_tenz()
        min_to_max_scale_ratio: float = min(scales) / max(scales)
        print("Scale convergence rate =", min_to_max_scale_ratio)
        return min_to_max_scale_ratio > convergence_rate


#---------------------------------TENZ CLASS ITSELF-----------------------------

class Tenz():

    def __init__(self, tenz_name: str, comport_number: int):
        # tenz_name format: "TN" (T in latin, N is a tenz_number)
        self.comport = ComPort(comport_number)
        self.protocol_key: int = 42 #key for tenz commands. Could be secured
        self.tenz_name: str = tenz_name
        self.tenz_number: int = int(tenz_name.split('T')[-1])
        self.calib_dict = CalibrationDict()

    def exec_command(
            self, command_number: int, 
            data_value: float = 0.):
        #now size of data_value is 4 bytes (signed int)
        #data_value must be an optional field to make most commands 3 times shorter 
        self.comport.write_bytes(
            struct.pack('=2Bf', self.protocol_key, command_number, data_value)
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
        scale = self.calib_dict.dumb_mean_scale_for_tenz()
        print("Scale calculated:", scale)
        return scale

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

    def set_loop_delay(self, delay: int) -> int:
        delay_echo: float = self.exec_command(4, float(delay))
        return int(delay_echo)

    def set_times_to_measur(self, times_to_measur: int) -> int:
        times_to_measur_echo: float = self.exec_command(5, float(times_to_measur))
        return int(times_to_measur_echo)

    def flush_arduino_serial_buffer_input_and_output(self):
        pass

    def force_set_offset(self):
        pass

    def get_info(self):
        pass



#--------------------------------MULTIPLE PORTS CLASS----------------------------------

class Tenzes(dict):
    # TENZ_NAME is the key
    # TENZ is the value
    def __init__(self, port_numbers_list: Optional[List[int]] = None):
        if not port_numbers_list:
            print("Attempting to search all ports automaticly...")
            # port_numbers_list = ComPortUtils().get_tenz_comports_numbers() 
            tenz_names_list, port_numbers_list = \
                ComPortUtils().get_names_and_ports_from_registry()
        for port_number in zip(tenz_names_list, port_numbers_list):
            
            # mind the difference between the tenz_number and the port_number
            self[tenz_number] = Tenz(tenz_name, port_number) #NEED TESTING

    def open_ports_of_all_tenzes(self):
        for tenz in self: tenz.comport.open()

    def close_ports_of_all_tenzes(self):
        for tenz in self: tenz.comport.close()



#-----------------------------------MAIN FOR TESTING-------------------------------------
def calibration_test(): #outdated
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
    tenz = Tenz()
    tenz.comport.open()
    for _ in range(100):
        print(tenz.comport.read_line())
