# ДАННЫЙ МОДУЛЬ СЕЙЧАС ИМПОРТИРУЕТСЯ В МАЙННЕЯВНО
    # С ПОМОЩЬЮ МЕТОДА PROMOTE_WIDGET В QT_DESIGNER

from typing import List, Tuple, Dict, Optional

# from PyQt5 import QtCore, QtWidgets
from PyQt5.QtWidgets import QLabel


class UnitsWidget(QLabel): #encapsulate in a bigger class
    def __init__(self, parent=None):
        super().__init__(parent)
        self.tenz_number = 0 #не работает
        self.update(0) #не работает

    def assign_tenz_number(self, number: int):
        self.tenz_number = number

    def update(self, units: float):
        self.setText(f"тд{self.tenz_number}: {units}кг")

    

