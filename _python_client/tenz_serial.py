from typing import List, Tuple, Dict, Optional
import struct
import time
import winreg

import serial.tools.list_ports as list_serials
import serial

from wheels import crop_float
from dataclasses import WeightPoint, WeightTimeline



#----------------TYPE ALIASES-----------------
Line = str
Lines = List[Line]

#--------------NAMING DICTIONARIES-----------------
device_number_to_port_number: Dict[int, int] = {
    #dict need updating in case of new pairing event
    #port 0 means that the outgoing port is unknown
    1  : 13,
    2  : 14,
    3  : 16,
    4  : 18,
    5  : 21,
    6  : 24,
    7  : 25, #25 порт - CSR
    8  : 20, #20 порт - CSR
    9  : 17, #17 порт - CSR # NEED TESTING (имя не распозналось)
    10 : 15, #15 порт - CSR
    11 : 19, #19 порт - CSR
    12 : 26, #26 порт - CSR
    13 : 4, #отладочный девайс (будет привязываться и к встройке и к CSR)
    14 : 0,
    15 : 0,
}

device_number_to_tenz_name: Dict[int, 'str'] = { 
    # dict need updating in case of new pairing event
    # tenz_name 0 means that tenz is epsent
    # letter b stands for "blue arduino" i. e. arduino with 328 processor
    # letter T in names is latin
    1  : 'T-1b',
    2  : 'T-2' ,
    3  : 'T-3' ,
    4  : 'T-4' ,
    5  : 'T-5' ,
    6  : 'T-6b',
    7  : 'T-7b',
    8  : 'T-8b',
    9  : 'T-9b',
    10 : 'T-10',
    11 : 'T-11',
    12 : 'T-12',
    13 : 'T-13', 
    14 : 'T-0',
    15 : 'T-0',
}

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
        self._timeout_in_secs: float = 0.5 #NEED HUGE TESTING

    def __str__(self): return f"PORT COM-{self._number}" #to ease debug messages
    
    #---------------------------методы для пересылок----------------------------
    def open(self):
        raise NotImplementedError("Use open_with_flag instead")
        try:
            self._ser = serial.Serial(f'COM{self._number}')
            print(f'{self} opened ***\\')
        except serial.serialutil.SerialException:
            print(f'{self} was not opened! It was not found most probably')

    def _open_with_flag(self) -> bool:
        is_opening_succ: bool = False
        try:
            self._ser = serial.Serial(
                f'COM{self._number}', timeout=self._timeout_in_secs
                )
            # print("self._ser.timeout =", self._ser.timeout) 
            print(f'{self} opened ***\\')
            is_opening_succ = True
        except serial.serialutil.SerialException:
            print(f'{self} was not opened! It was not found most probably')
            is_opening_succ = False
        return is_opening_succ

    def flush_input(self):
        if self._ser:
            self._ser.flushInput()
            print('Input flushed')
    
    def close(self):
        if self._ser: 
            self._ser.close()
            self._ser = None
            # self = None 
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

    def read_bytes(self, bytes_number: int) -> bytes: #DEPRECATED
        raise NotImplementedError("Use read_bytes_with_flag instead")
        data: bytes = self._ser.read(size = bytes_number)
        print(f'--- FROM {self} --- :', data)
        return data

    def read_bytes_with_flag( #NEED TESTING
            self, bytes_number: int
            ) -> Tuple[Optional[bytes], bool]: #WITH TIMEOUT HANDLING
        try:
            data: bytes = self._ser.read(size = bytes_number)
            print(f'--- FROM {self} --- :', data)
            if (len(bytearray(data)) != bytes_number):
                raise IndexError("Answer from serial port has wrong length!")
            return data, True
        except IndexError:
            return None, False

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
        raise NotImplementedError
        reg_root_key = winreg.HKEY_CLASSES_ROOT
        reg_handle = winreg.CreateKey(reg_root_key)
        print("REG HANDLE WORKED:", reg_handle)
        
        key_path = (R"Компьютер\HKEY_LOCAL_MACHINE\\SYSTEM\CurrentControlSet" +
                "\Enum\BTHENUM\Dev_002113002876"+
                "\\7&13438a0b&1&BluetoothDevice_002113002876")
        key_name = "FriendlyName"
        tenz_names_list: List[str] = list(device_number_to_tenz_name.values())
        port_numbers_list: List[int] = []

        return tenz_names, port_numbers

    def get_devices_numbers_with_ports_assigned_in_dict(self) -> List[int]:
        numbers_of_devices_with_ports: List[int] = [
            key
            for key, value in device_number_to_port_number.items()
            if value != 0
            ]
        print(f"Devices {numbers_of_devices_with_ports} "
                +"have assigned ports")
        return numbers_of_devices_with_ports

    def get_tenz_comports_numbers(self) -> List[int]: #NEED TESTING
        raise NotImplementedError
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
    """
    Type of a dict is Dict[int, Tuple[float, float]]
    Namely: Dict[calibration_pair_number, Tuple[weight, value]]
    Чтобы не делать калибровку каждый раз при включении питания датчиков,
    Калибровочные словари всех датчиков будут сохранены в файле
    """
    """calib_file format is:
    TENZ {self.tenz_name} START 
    1, weight, value
    2, weight, value
    3, weight, value
    ...
    TENZ {self.tenz_name} END
    
    TENZ {next tenz name} START 
    ...
    TENZ {next tenz name} END
    sorting by tenz is not implemented
    """

    def __init__(self, tenz_name: str):
        self.tenz_name: str = tenz_name #WILL IT INTERFERE WITH TENZ.TENZ_NAME?
        self.calib_file: str = "Калибровка.txt" #один файл для всех
        self.load_calib_dict_from_file()
        print("Calibration dict loaded") 
            # при создании инстанса Tenz загрузили из файла

    def add_calibration_pair(self, weight: float, value: float):
        calib_pairs_number = self.__len__()
        self[calib_pairs_number] = weight, value #STARTING KEYS FROM ZERO
        print('Calibration pair added')
        # апдейтим файл после добавления каждой калибровочной точки
            # почему бы бля и нет
        self.update_calib_dict_in_file()

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
    
    def _create_file_entry(self) -> List[Line]:
        lines_to_write: Lines = [ #with EOL symbol already!
            f"TENZ {self.tenz_name} START\n",
            *[f"{calib_pair_index}, {calib_pair[0]}, {calib_pair[1]}\n"
                for calib_pair_index, calib_pair in self.items()
                ],
            f"TENZ {self.tenz_name} END\n",
        ]
        return lines_to_write

    def _write_file_entry_to_dict(self, loaded_entry: Lines):
        tenz_name_from_entry: str = loaded_entry[0].split(' ')[1]
        if tenz_name_from_entry != self.tenz_name:
            raise NameError("Wrong name in CalibDict file entry")
        self.clear_all_calibration_pairs()
        for line in loaded_entry[1: -1]:
            weight: float = line.split(', ')[1]
            value:  float = line.split(', ')[2]
            print("weight and value from dict:", weight, value)
            self.add_calibration_pair(weight, value)

    def update_calib_dict_in_file(self): #or rewrite
        with open(self.calib_file, 'r') as F:
            file_buffer: List[Line] = [line for line in F] #preserving EOL symbols!
        start_line_num: Optional[int] = None
        end_line_num:   Optional[int] = None
        for i, line in enumerate(file_buffer):
            if line is f"TENZ {self.tenz_name} START\n":
                start_line_num: int = i
            if line is f"TENZ {self.tenz_name} END\n":
                end_line_num: int = i
        if start_line_num == None: 
            # then entry is not found in buffer
            updated_file_buffer: List[Line] = (
                file_buffer
                +self._create_file_entry()
            )
        if start_line_num != None:
            updated_file_buffer: List[Line] = (
                file_buffer[:start_line_num]
                +self._create_file_entry()
                +file_buffer[(end_line_num + 1) :] #NEED TESTING
            )
        with open(self.calib_file, 'w') as F:
            F.write("".join(updated_file_buffer))

    def load_calib_dict_from_file(self):
        with open(self.calib_file, 'r') as F:
            file_buffer: List[Line] = [line for line in F] #preserving EOL symbols!
        start_line_num: Optional[int] = None
        end_line_num:   Optional[int] = None
        for i, line in enumerate(file_buffer):
            if line is f"TENZ {self.tenz_name} START\n":
                start_line_num: int = i
            if line is f"TENZ {self.tenz_name} END\n":
                end_line_num: int = i
        if (start_line_num == None) or (end_line_num == None):
            print("Calib dict file entry was not found")
            return
        loaded_entry: Lines = \
            file_buffer[start_line_num : (end_line_num + 1)]
        self._write_file_entry_to_dict(loaded_entry)
        print("calib_dict loaded from file")

    def __del__(self):
        print("Updating in file test (during Calib_dict deletion)")
        self.update_calib_dict_in_file()

#---------------------------------TENZ CLASS ITSELF-----------------------------

class Tenz():

    def __init__(self, device_number: int, tenz_name: str, comport_number: int):
        # tenz_name format: "TN" (T in latin, N is a tenz_number)
        self.device_number: int = device_number
        self.comport = ComPort(comport_number)
        self.protocol_key: int = 42 #key for tenz commands. Could be secured
        self.tenz_name: str = tenz_name
        # self.tenz_number: int = int(tenz_name.split('T')[-1]) #REMOVED CUZ IAGNI
        self.calib_dict = CalibrationDict(tenz_name)
        self.weight_timeline = WeightTimeline(self.device_number)

    def __str__(self):
        return (
            "--------------TENZ INSTANCE--------------\n"
            + f"Tenz name: {self.tenz_name}\n"
            + f"Comport number: {self.comport._number}\n"
            + f"Protocol key: {self.protocol_key}\n"
            )

    def open_comport(self) -> bool:
        is_opening_succ: bool = False
        is_opening_succ = self.comport._open_with_flag()
        if not is_opening_succ:
            print("Port opening is not succ so DEL SELF")
            del self # cuz there must not be tenz in tenzes with closed ports
            return False
        elif is_opening_succ:
            return True

    def close_comport(self):
        self.comport.close()

    def exec_command(
            self, command_number: int, 
            data_value: float = 0.):
        #now size of data_value is 4 bytes (signed int)
        #data_value must be an optional field to make most commands 3 times shorter 
        self.comport.write_bytes(
            struct.pack('=2Bf', self.protocol_key, command_number, data_value)
        )

        response_tuple: Tuple[int, int, float]
        data, is_reading_succ = self.comport.read_bytes_with_flag(6)
        if not is_reading_succ:
            print("ОШИБКА ВЫПОЛНЕНИЯ КОМАНДЫ." 
                + f"DELETING TENZ... device_number = {self.device_number}")
            del self #NEED TESTING
            return
        response_tuple = struct.unpack('=2Bf', data) #NEED TESTING!
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

    def append_weight_point(self):
        units: float = crop_float(self.get_units())
        new_weight_point = WeightPoint(time.time(), units)
        self.weight_timeline.append_point(new_weight_point)

    def plot_data(self) -> WeightTimeline: #NEED TESTING
        raise NotImplementedError(
            "Obsolete method! Use methods of WeightTimeline class instead!"
            )

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
    '''
    device_name is a key
    Tenz instance is a value 

    THE IDEA is that only Tenzes with open ports can be contained in Tenzes!
    So tenz'es comport shoult be opened in a constructor
    And if port is was not opened (or closed somehow) Tenz should be deleted from Tenzes

    CALIB DICT загружается в конструкторе Tenz.
    Живет в классе Tenz, как его аттрибут
    При добавлении каждой calib_pair апдейтится файл с калибровками
    Соответственно при удалении Tenz calib_dict еще раз апдейтит себя в файл
    '''
    def __init__(self, user_input_devices_numbers: Optional[List[int]] = None):
        if not user_input_devices_numbers: 
            # then look up all devices with non-zero ports
            devices_numbers: List[int] = \
                ComPortUtils().get_devices_numbers_with_ports_assigned_in_dict()
            '''print("Attempting to search all ports automaticly...")
            # port_numbers_list = ComPortUtils().get_tenz_comports_numbers() 
            tenz_names, port_numbers = ComPortUtils().get_names_and_ports_from_registry()'''
            print("Looking for ports in the dictionary. " 
                 +"Attempting to open them...")
        if user_input_devices_numbers:
            devices_numbers: List[int] = user_input_devices_numbers

        tenz_names:   List[str] = []
        port_numbers: List[int] = []
        for dev_num in devices_numbers:
            try: 
                tenz_name: str = device_number_to_tenz_name[dev_num]
                port_number: int = device_number_to_port_number[dev_num]
            except KeyError:
                   print(f"Тензодатчика с номером {dev_num} нет. "
                        +"Попробуйте вводить номера от 1 до 15 или"
                        +"проверьте словарь портов.")
            new_tenz = Tenz(dev_num, tenz_name, port_number)
            is_opening_succ = new_tenz.open_comport()
            if is_opening_succ:
                #we need new_tenz in tenzes if only its port opened
                self[dev_num] = new_tenz #NEED TESTING
        print(self)
        print(self.keys())

    def __str__(self):
        return "".join([
            f"\nDevice number {dev_num}\n{tenz}"
            for dev_num, tenz in self.items()
            ])

    def close_all(self):
        dev_nums = self.keys()
        for dev_num in dev_nums:
            self[dev_num].close_comport()
            del self[dev_num] #tenz destructor
            # del self[dev_num] #remove from Tenzes dict. overkill. NEED TESTING
        print(self.keys())

    def close_some(self, devices_numbers: List[int]):
        for dev_num in devices_numbers:
            self[dev_num].close_comport()
            del self[dev_num] #tenz destructor
            # del self[dev_num] #remove from Tenzes dict. overkill. NEED TESTING
        print(self.keys())

    def get_all_plot_data(self) -> List[WeightTimeline]: #DEPRECATED
        raise NotImplementedError("Obsolete method!")
        return [
            tenz.plot_data()
            for tenz in self.values()
        ]

    def get_some_tenzes_plot_data(self, device_numbers: List[int]) -> List[Tuple[List[float], List[float]]]:
        raise NotImplementedError("Obsolete method!")
        return [
            self[dev_num].plot_data()
            for dev_num in device_numbers
        ]

    def get_last_absolute_units(self) -> Dict[int, float]:
        return {
            dev_num : tenz.weight_timeline[-1].weight
            for dev_num, tenz in self.items()
        }

#-----------------------------------MAIN FOR TESTING-------------------------------------
def calibration_test(): #OUTDATED
    raise NotImplementedError("Outdated function!")
    tenz = Tenz(11)
    tenz.open_comport()

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

    tenz.close_comport()


if __name__ == '__main__':
    tenz = Tenz()
    tenz.open_comport()
    for _ in range(100):
        print(tenz.comport.read_line())
