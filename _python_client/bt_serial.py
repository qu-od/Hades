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


#--------------------------------SINGLE PORT CLASS----------------------------------

class TenzSerialPort(object):
    def __init__(self, comport_number: int, name: str = None, baudrate: int = 19200):
        self._ser: Optional[serial.Serial] = None
        self._number: int = comport_number
        self._baudrate: int = baudrate
        self.name: Optional[str] = name
        self.header: int = 42 #key for tenz commands

    def __str__(self): return f"PORT COM-{self._number}" #to ease debug messages
    
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

    def exec_command(
            self, command_number: int, 
            data_value: int = 0):
        #now size of data_value is 4 bytes (signed int)
        #data_value must be an optional field to make most commands 3 times shorter 
        self.write_bytes(
            struct.pack('>2Bi', self.header, command_number, data_value)
        )
        response_header: int
        error_code: int
        response_data_value: float
        response_header, error_code, response_data_value = \

            struct.unpack('>2Bi', self.read_bytes(6)) #NEED TESTING!
            
        #also prints response in console
        if error_code != 0: 
            print(f'ERROR NUMBER {error_code} OCCURED ON ARDUINO')
            return
        elif error_code == 0: 
            return response_data_value

    def tare(self):
        self.exec_command(0)

    def get_value(self) -> float:
        # time.sleep(3)
        value: float = self.exec_command(1)
        return value

    def set_scale(self, scale: int):
        self.exec_command(2, scale)

    def get_units(self) -> float:
        units: float = self.exec_command(3)
        return units



#--------------------------------MULTIPLE PORTS CLASS----------------------------------

class TenzPorts(object):
    def __init__(self, *ports):
        self.ports: list = list(ports)

    def __str__(self):
        pass

    def read_ports_simultaneously(*comports_names):
        pass
        ser_list = [serial.Serial(comport_name) 
            for comport_name in comports_names]
        for ser in ser_list: print(ser)
        for _ in range(100):
            read_line_from_serial(ser_list[0])
            read_line_from_serial(ser_list[1])
        # map(read_line_from_serial, ser_list)


#-----------------------------------MAIN FOR TESTING-------------------------------------
def calibration_test():
    #MAKE CONTEXT MANAGER FOR WirelessSerialPort

    tenz_port = TenzSerialPort(5)
    tenz_port.open()
    # tenz_port.flush_input()
    tenz_port.tare() #TARE WITH NO LOAD
    # weights = [1, 2, 3, 4] #in kilos
    weights = [1, 2] #in kilos
    scales = [  
        tenz_port.get_value() / weights[i] #TRY A BUNCH OF LOADS (better be 5 to 10):
        for i in range(len(weights))
        ]
    mean_scale: float = sum(scales) / len(scales)
    tenz_port.set_scale(mean_scale) #SET_SCALE
    data_in_kilos = [
        tenz_port.get_units() #GET_UNITS in kilos
        for _ in range (100)
      ]  
    # tenz_port.exec_command('100') #wrong command attempt
    tenz_port.close()

if __name__ == '__main__':
    # calibration_test()
    tenz_port = TenzSerialPort(5)
    tenz_port.open()

    tenz_port.tare()
    print(tenz_port.get_value())
    tenz_port.set_scale(15)
    print(tenz_port.get_units())

    tenz_port.close()




