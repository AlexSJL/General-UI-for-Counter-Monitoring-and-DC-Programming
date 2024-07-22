# Import Packages
from port_ctrl1 import Rigol_DCPort
from CAENDesktopHighVoltagePowerSupply1 import CAENDesktopHighVoltagePowerSupply, OneCAENChannel
import pyvisa as visa
import time
import numpy as np
import serial
import serial.tools.list_ports 
from matplotlib import pyplot as plt
from DC_Scan_class import *
from random import randint
from UI_Main_Window_Object import Ui_MainWindow
from First_Stability_Diagram import Stability_Diagram as SD

import sys
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure
from PyQt5.QtGui import QIcon
from PyQt5.QtCore import Qt, QTimer, QThread, QMutex, pyqtSignal
from PyQt5.QtWidgets import *
from PyQt5 import QtCore, QtGui, QtWidgets
import pyqtgraph as pg

# This thread for plotting in stability diagram
class PlotThread(QThread):
    #stop_signal = pyqtSignal()
    def __init__(self, plot_widget, DC, myWin):
        super().__init__()
        self.plot_widget = plot_widget
        self.x_data = []
        self.y_data = []
        self.i_data = []
        self.j_data = []
        self.win = 150
        self.mutex = QMutex() 
        self.pen1 = pg.mkPen(color=(255, 0, 0), width=3)
        self.pen2 = pg.mkPen(color=(0, 0, 255), width=3)
        self.pen3 = pg.mkPen(color=(255, 255, 255), width=3)
        self.running = True
        self.DC=DC
        self.myWin = myWin
        self.pen1 = pg.mkPen(color=(255, 0, 0), width=3)
        self.pen2 = pg.mkPen(color=(0, 0, 255), width=3)
        self.pen3 = pg.mkPen(color='k', width=3)
        self.pen4 = pg.mkPen(color='g', width=3)
        self.omega = 800
        self.inscribed_radius = 12
        self.t = None      
        self.state = None
        self.myWin.pushButton_4.clicked.connect(self.clear)

    #def update_data1(self, new_x, new_y):
    #    self.mutex.lock()
    #    self.x_data = np.append(self.x_data, new_x)
    #    self.y_data = np.append(self.y_data, new_y)
    #    self.mutex.unlock()

    def update_data2(self, new_x, new_y):
        if self.state == 'play':
            self.mutex.lock()
            self.i_data.append(new_x)
            self.j_data.append(new_y)
            if self.myWin.spectrum_debug == False:
                self.myWin.U = new_y
                self.myWin.V = new_x
            self.mutex.unlock()
    
    def run(self):
        while self.running:            
            timer1 = QTimer()
            timer1.timeout.connect(self.update_plot)
            timer1.start(230)
            self.exec_()

    def play(self):
        self.state = 'play'

    def pause(self):
        self.state = 'pause'

    def clear(self):
        self.x_data.clear()
        self.y_data.clear()
    
    def Assistant_plot(self):
        # Only update the data when input is valid
        if self.myWin.lineEdit.text() != '' and float(self.myWin.lineEdit.text()) > 0 :
            self.omega = float(self.myWin.lineEdit.text())
        if self.myWin.lineEdit_2.text() != '' and float(self.myWin.lineEdit_2.text()) > 0:
            self.inscribed_radius = float(self.myWin.lineEdit_2.text())
        self.t = SD()
        self.tx0, self.ty0 = self.t.diagram_data_uv(omega=self.omega, m=229, e=1, r = self.inscribed_radius)
        self.tx1, self.ty1 = self.t.diagram_data_uv(omega=self.omega, m=229, e=3, r = self.inscribed_radius)
        self.tx2, self.ty2 = self.t.diagram_data_uv(omega=self.omega, m=228, e=3, r = self.inscribed_radius)
        self.tx3, self.ty3 = self.t.diagram_data_uv(omega=self.omega, m=233, e=1, r = self.inscribed_radius)
        
        ion_1 = pg.PlotCurveItem(self.tx0,self.ty0,name=r'Th-229(I)',pen=self.pen1)
        ion_2 = pg.PlotCurveItem(self.tx1,self.ty1,name=r'Th-229(III)',pen=self.pen2)
        ion_3 = pg.PlotCurveItem(self.tx2,self.ty2,name=r'Th-228(III)',pen=self.pen3)
        ion_4 = pg.PlotCurveItem(self.tx3,self.ty3,name=r'U-233(I)',pen=self.pen4)
        
        self.plot_widget.addItem(ion_1)
        self.plot_widget.addItem(ion_2)
        self.plot_widget.addItem(ion_3)
        self.plot_widget.addItem(ion_4)
        '''
        self.plot_widget.getPlotItem().plot(
            self.tx0,
            self.ty0,
            name=r'Th-229(I)',
            pen=self.pen1)
        self.plot_widget.getPlotItem().plot(
            self.tx1,
            self.ty1,
            name=r'Th-229(III)',
            pen=self.pen2)
        self.plot_widget.getPlotItem().plot(
            self.tx2,
            self.ty2,
            name=r'Th-228(III)',
            pen=self.pen3)
        self.plot_widget.getPlotItem().plot(
            self.tx3,
            self.ty3,
            name=r'U-233(I)',
            pen=self.pen4)
        '''
    
    def update_plot(self):
        # Call Assistant Plot
        self.mutex.lock()
        # Monitoring Plot
        if self.state == 'play':
            self.plot_widget.clear()
            self.Assistant_plot()
            #import ipdb; ipdb.set_trace()
            try:
                if len(self.i_data) > self.win:
                    self.x_data = self.i_data[-self.win:]
                    self.y_data = self.j_data[-self.win:]
                    self.i_data = self.i_data[-self.win:]
                    self.j_data = self.j_data[-self.win:]
                else:
                    self.x_data = self.i_data
                    self.y_data = self.j_data

                if len(self.x_data) > 1:
                    self.plot_widget.getPlotItem().plot(
                        self.x_data[:-1],
                        self.y_data[:-1],
                        name="Monitor Values",
                        pen=None, #pg.mkPen(color=(0, 114, 189), width=3),
                        symbol='o',
                        symbolBrush = pg.mkBrush(color=(0, 114, 189)),
                        symbolSize=5)
                    
                    self.plot_widget.getPlotItem().plot(
                        [self.x_data[-1]],[self.y_data[-1]],
                        name="Latest Monitor Values",
                        pen= None, #pg.mkPen(color=(0, 114, 189), width=3),
                        symbol='o',
                        symbolBrush = 'r',
                        symbolSize=10)

                elif len(self.x_data) == 1:
                    self.plot_widget.getPlotItem().plot(
                        [self.x_data[-1]],[self.y_data[-1]],
                        name="Latest Monitor Values",
                        pen=None, #pg.mkPen(color=(0, 114, 189), width=3),
                        symbol='o',
                        symbolBrush = 'r',
                        symbolSize=10)
            except:
                pass
            #print(len(self.i_data))
            #self.plot_widget.show()
        else:
            self.plot_widget.clear()
            self.Assistant_plot()
            self.plot_widget.getPlotItem().plot(
                    self.i_data,
                    self.j_data,
                    name="Monitor Values",
                    pen= None, #pg.mkPen(color=(0, 114, 189), width=3),
                    symbol='o',
                    symbolSize=5)
            '''
            self.plot_widget.getPlotItem().plot(
                    self.i_data,
                    self.j_data,
                    name="Monitor Values",
                    pen= None, #pg.mkPen(color=(0, 114, 189), width=3),
                    symbol='o',
                    symbolSize=5)
            '''
        self.mutex.unlock()

    def stop(self):
        self.running = False

