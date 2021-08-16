# ДАННЫЙ МОДУЛЬ СЕЙЧАС ИМПОРТИРУЕТСЯ В МАЙННЕЯВНО
    # С ПОМОЩЬЮ МЕТОДА PROMOTE_WIDGET В QT_DESIGNER

import sys
import random
from typing import List, Tuple, Dict, Optional

import matplotlib
matplotlib.use('Qt5Agg')

from PyQt5 import QtCore, QtWidgets
from PyQt5.QtWidgets import (QDialog, QApplication, QPushButton,
    QVBoxLayout, QWidget)

import pyqtgraph as pg
from pyqtgraph import PlotWidget, plot
from dataclasses import WeightPoint, WeightTimeline

class GraphWidget(PlotWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
            # self.test_var: int = 422 is working
        self.number_of_tenzes: int = 15
        self.graphs_visibility: Dict[int, bool] = {
            i+1 : True
            for i in range(self.number_of_tenzes)
        }
            # visibility of all graphs defaults to True
        print("self.devices_visibility at initialization:", self.graphs_visibility)

    def plot_timelines(self, weight_timelines: List[WeightTimeline]):        
        for weight_timeline in weight_timelines:
            if self.graphs_visibility[weight_timeline.device_number] is True:
                lists_for_plotting: Tuple[List[float], List[float]] = \
                    weight_timeline.get_lists_for_plotting()
                self.plot(*lists_for_plotting) #NEED TESTING
    
    def _fake_weight_timeline( #DEPRECATED
            self, base_weight_timeline: WeightTimeline, shift_in_kilos: float
        ) -> WeightTimeline:
        base_times, base_weights = base_weight_timeline
        new_weights = [weight + shift_in_kilos for weight in base_weights]
        return base_times, new_weights

    def update_graphs_visibility(self, graph_visibility_for_each_device: Dict[int, bool]):
        self.graphs_visibility = graph_visibility_for_each_device


    '''def test_func(self):
        pass

    def test_method(self, s: str, n: int) -> int: #its working!
        print("another_test_method WORKED")
        print(f"That's how it worked: {s*n}")
        return n * 10

    def get_test_var(self):
        print("TEST VAR =", self.test_var)
        return self.test_var'''

    


#--------------------MATPLOTLIB OPTIONS-------------------------

'''# from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg
from matplotlib.figure import Figure
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg
from matplotlib.backends.backend_qt5agg import NavigationToolbar2QT
import matplotlib.pyplot as plt

class GraphWidget(QWidget):
    def __init__(self, parent=None):
        super(GraphWidget, self).__init__(parent)

        self.figure = plt.figure()
        self.canvas = FigureCanvasQTAgg(self.figure)
        self.toolbar = NavigationToolbar2QT(self.canvas, self)

        self.ax = self.figure.add_subplot(111)
        self.ax.plot([1]*10) #initial content to show
        self.canvas.draw()


        layout = QVBoxLayout()
        layout.addWidget(self.toolbar)
        layout.addWidget(self.canvas)
        self.setLayout(layout)
        

        # Just some button connected to `plot` method
        # self.button = QPushButton('Plot')
        # self.button.clicked.connect(self.update_plot)
        # layout.addWidget(self.button)

        print("init worked")

    def create_plot(self):
        self.ax = self.figure.add_subplot(111)
        self.ax.plot([1]*10) #initial content to show
        self.canvas.draw()
        print("create plot REALLY worked")

    def update_plot(self, data: List[Tuple[float, float]]):
        data = [random.random() for i in range(10)]
        self.figure.clear()
        self.ax.plot(data, '*-')
        self.canvas.draw()'''


'''class MplCanvas(FigureCanvasQTAgg):

    def __init__(self, parent, width=5, height=4, dpi=100):
        # fig = Figure(figsize=(width, height), dpi=dpi)
        fig = Figure()
        self.axes = fig.add_subplot(111)
        # super(MplCanvas, self).__init__(fig)'''

'''class MainWindow(QtWidgets.QMainWindow):

    def __init__(self, *args, **kwargs):
        super(MainWindow, self).__init__(*args, **kwargs)

        # Create the maptlotlib FigureCanvas object, 
        # which defines a single set of axes as self.axes.
        sc = MplCanvas(self, width=5, height=4, dpi=100)
        sc.axes.plot([0,1,2,3,4], [10,1,20,3,40])
        self.setCentralWidget(sc)

        self.show()


app = QtWidgets.QApplication(sys.argv)
w = MainWindow()
app.exec_()'''

#-----------------------------IN PLACE REDRAW-------------------------------

'''class MainWindow(QtWidgets.QMainWindow):

    def __init__(self, *args, **kwargs):
        super(MainWindow, self).__init__(*args, **kwargs)

        self.canvas = MplCanvas(self, width=5, height=4, dpi=100)
        self.setCentralWidget(self.canvas)

        n_data = 50
        self.xdata = list(range(n_data))
        self.ydata = [random.randint(0, 10) for i in range(n_data)]

        # We need to store a reference to the plotted line 
        # somewhere, so we can apply the new data to it.
        self._plot_ref = None
        self.update_plot()

        self.show()

        # Setup a timer to trigger the redraw by calling update_plot.
        self.timer = QtCore.QTimer()
        self.timer.setInterval(100)
        self.timer.timeout.connect(self.update_plot)
        self.timer.start()

    def update_plot(self):
        # Drop off the first y element, append a new one.
        self.ydata = self.ydata[1:] + [random.randint(0, 10)]

        # Note: we no longer need to clear the axis.       
        if self._plot_ref is None:
            # First time we have no plot reference, so do a normal plot.
            # .plot returns a list of line <reference>s, as we're
            # only getting one we can take the first element.
            plot_refs = self.canvas.axes.plot(self.xdata, self.ydata, 'r')
            self._plot_ref = plot_refs[0]
        else:
            # We have a reference, we can use it to update the data for that line.
            self._plot_ref.set_ydata(self.ydata)

        # Trigger the canvas to update and redraw.
        self.canvas.draw()'''




