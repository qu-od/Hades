# ДАННЫЙ МОДУЛЬ СЕЙЧАС ИМПОРТИРУЕТСЯ В МАЙННЕЯВНО
    # С ПОМОЩЬЮ МЕТОДА PROMOTE_WIDGET В QT_DESIGNER

from typing import List, Tuple, Dict, Optional
import math

from PyQt5 import QtCore, QtGui, QtWidgets
# from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import QLabel, QCheckBox, QWidget, QFrame
from PyQt5.QtGui import QPalette, QColor

from wheels import crop_float, grow_string

class _TenzUnitsWidget(QWidget):
    '''
    In _TenzUnitsWidget there are four widgets in a row:
    1) Label with a tenz number 
    2) Label with an absolute value in kilos
    3) Label with a difference between abs value and a target value 
        (target values are equal for all tenzes
        cuz we want to have equal weights under all tenzes)
    4) CheckBox to show/hide plot on a graphwidget
    '''

    def __init__(self, device_number, parent = None):
        super().__init__(parent)

        # MAKE THIS SEVERAL PARAMETERS AN OBJECT ATTRIBUTE
            # do not use self
        self.number_of_tenzes_on_a_bench: int = 12
        self.REFLECTOR_M2_WEIGHT: int = 25 #NEED UPDATING 
        self.REFLECTOR_M3_WEIGHT: int = 15 #NEED UPDATING
        self.base_weight_value = crop_float(
            self.REFLECTOR_M2_WEIGHT / self.number_of_tenzes_on_a_bench
            )
        # print(f"Целевой вес на один датчик = {self.base_weight_value}кг")
            #MAKE self.base_weight_value A PARAMETER FOR GUI

        self.is_tenz_enabled: bool = False
            #it must show whether Tenz in Tenzes or not
        self.is_tenz_nominal: bool = False

        self.device_number: int = device_number
        self.absolute_weight_value: float
            #parameter will be set in _set_initial_state() method

        self._dev_num_label = QtWidgets.QLabel()
        self._visibility_checkbox = QtWidgets.QCheckBox()
        self._abs_units_label = QtWidgets.QLabel()
        self._rel_units_label = QtWidgets.QLabel()

        # self.setMinimumHeight(10) не работает
        # self.setMaximumHeight(30) не работает

        self._dev_num_label.setFrameShape(QFrame.Panel)
        self._abs_units_label.setFrameShape(QFrame.Panel)
        self._rel_units_label.setFrameShape(QFrame.Panel)
        
        layout = QtWidgets.QHBoxLayout() 
        layout.setSpacing(0)

        layout.addWidget(self._dev_num_label)
        layout.addWidget(self._visibility_checkbox)
        layout.addWidget(self._abs_units_label)
        layout.addWidget(self._rel_units_label)

        self.setLayout(layout)
        self._set_initial_state()
        self.set_enabled(False)

    def _set_initial_state(self):
        self._dev_num_label.setText(str(self.device_number))
        self.update_and_show_units(tenz_abs_units = 0.)
        self._visibility_checkbox.setChecked(True)
        # print("Initial state of a TenzUnitsWidget was set")

    def _set_initial_style(self): #DEPRECATED
        raise NotImplementedError("Deprecated method")
        self._abs_units_label.setStyleSheet(
            'QLabel {background-color : lightblue; font : 15px}'
            )
        self._rel_units_label.setStyleSheet(
            'QLabel {background-color : #FFFFFF; font : 15px}'
            )

    def set_enabled(self, switch: bool):
        self.is_tenz_enabled = switch
        self.is_tenz_nominal = switch
        self._dev_num_label.setEnabled(switch)
        self._visibility_checkbox.setEnabled(switch)
        self._abs_units_label.setEnabled(switch)
        self._rel_units_label.setEnabled(switch)
        self._update_dev_num_label_color()

    def mark_tenz_as_not_nominal(self):
        #ЛИПКИЙ ПРАМЕТР. #СТОИТ ТЕНЗУ ТОЛЬКО РАЗ ПОКАЗАТЬ ЧТО-ТО СТРАННОЕ,
            #ОН ДО ОТКЛБЧЕНИЯ БУДЕТ ОКРАШЕН КРААСНЫМ 
        self.is_tenz_nominal = False
        self._update_dev_num_label_color()

    def _update_dev_num_label_color(self): #NEED TESTING
        if not self.is_tenz_enabled:
            hex_color_code = 'white'
            self._dev_num_label.setStyleSheet(
                'QLabel {background-color : ' + hex_color_code + '; font : 15px}'
            )
            return
        if self.is_tenz_nominal: hex_color_code = 'lightgreen'
        if not self.is_tenz_nominal: hex_color_code = 'red'
        self._dev_num_label.setStyleSheet(
            'QLabel {background-color : ' + hex_color_code + '; font : 15px}'
            )

    def _check_abs_units_and_update_abs_label_colors(
            self, abs_value: float = 0.):
        #NEED TESTING
        if not self.is_tenz_enabled: return
        base_value: float = self.base_weight_value #ALIAS
        #bright_blue_color_code is '#0000FF'
        #bright_red_color_code  is '#FF0000'
        brightness_of_red:   int = 255
        brightness_of_green: int = 255 
        brightness_of_blue:  int = 255
        rel_value: float = abs_value - base_value
        value_error_ratio: float = rel_value / base_value
        critical_value_ratio: float = 0.005
        '''
        base_value is about few kilos
        say then critical rel_value will be several tens of grams
        then value_error_ratio (rel_value / base_value) threeshold is 0.5%
        '''
        if abs(value_error_ratio) < critical_value_ratio:
            hex_color_code = '#FFFFFF'
            #аттрибут self.is_tenz_nominal обратно в True НЕ возвращаем
        if value_error_ratio >= critical_value_ratio: 
            #red indication (weight is too big)
            brightness_loss = \
                min(255, int(math.atan(value_error_ratio) * 5000))
            brightness_of_green -= brightness_loss
            brightness_of_blue  -= brightness_loss
            self.mark_tenz_as_not_nominal()

        if value_error_ratio <= -critical_value_ratio: #blue indication (weight is too small)
            brightness_loss = \
                min(255, int(math.atan(-value_error_ratio) * 5000))
            brightness_of_green -= brightness_loss
            brightness_of_red   -= brightness_loss
            self.mark_tenz_as_not_nominal()
        hex_color_code: str = ''.join([
            '#',
            f'{brightness_of_red:02X}',
            f'{brightness_of_green:02X}',
            f'{brightness_of_blue:02X}'
        ])
        # white_hex_color_code: str = '#FFFFFF'
        self._abs_units_label.setStyleSheet(
            'QLabel {background-color :' + hex_color_code + '}'
            )

    def update_and_show_units(self, tenz_abs_units: float = 0.):
        self.absolute_weight_value = tenz_abs_units
        # print("self.absolute_weight_value is a", self.absolute_weight_value)
        self._abs_units_label.setText(grow_string(
            str(crop_float(self.absolute_weight_value, decimals = 2)) + 'кг',
            new_string_length = 12
            ))
        self._check_abs_units_and_update_abs_label_colors(
            self.absolute_weight_value
            )
        self._rel_units_label.setText(grow_string(
            str(crop_float(self.absolute_weight_value - self.base_weight_value,  decimals = 2)) + 'кг',
            new_string_length = 12
            ))

    def setText(self, text): #PYQT требует метод SetText? Ну пусть получает его
        print("ДИКИЙ КОСТЫЛЬ:", f'PYQT хочет установить такой текст: {text}')

class UnitsWidget(QWidget):
    '''
    One big widget for all tenzes
    Weight data are always shown. User cannot turn it off in GUI
    Includes a data attributes (there ain't no many of them)
    '''

    def __init__(self, parent = None):
        super().__init__(parent)
        tu_widgets_number: int = 15
        self.tenz_units_widgets = [
            _TenzUnitsWidget(i + 1)
            for i in range(tu_widgets_number)
        ]
        # alternative variants (str to identifier):
            # setattr(self, f'tenz_units_widget_{i + 1}', _TenzUnitsWidget()) 
            # vars()[f'tenz_units_widget_{i + 1}'] = _TenzUnitsWidget(i + 1)

        layout = QtWidgets.QVBoxLayout()
        layout.setSpacing(0)
        for tu_widget in self.tenz_units_widgets:
            layout.addWidget(tu_widget)
            # tu_widget.setMaximumHeight(30)
            tu_widget.frameGeometry()
        self.setLayout(layout)

    def update_and_show_all_units(self, tenzes_absolute_units: Dict[int, float]):
        for tu_widget_number in tenzes_absolute_units.keys():
            self.tenz_units_widgets[tu_widget_number - 1].update_and_show_units( #cerefully with a decrement
                tenz_abs_units = tenzes_absolute_units[tu_widget_number]
                )

    def get_signals_of_clicked_visibility_checkboxes(self) -> List[callable]:
        return [
            tu_widget._visibility_checkbox.clicked
            for tu_widget in self.tenz_units_widgets
        ]

    def enable_unitswidgets_by_device_numbers(self, device_numbers: List[int]):
        for dev_num in device_numbers:
            self.tenz_units_widgets[dev_num - 1].set_enabled(True)
