from port_ctrl1 import Rigol_DCPort
from CAENDesktopHighVoltagePowerSupply1 import CAENDesktopHighVoltagePowerSupply, OneCAENChannel
import pyvisa as visa
import time
import numpy as np
from bisect import bisect
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

q = 0.70625231

class AMUThread(QThread):
    def __init__(self, myWin):
        super().__init__()
        self.myWin = myWin
        self.canvas = myWin.Count_vs_AMU
        self.mutex = QMutex() 
        self.U = myWin.U
        self.V = myWin.V
        self.Uo = self.U
        self.Vo = self.V
        self.AMU = []
        self.count = []
        self.ind = 0
        self.running = True
        self.state = 'play'

    def qm(self):
        r0 = int(self.myWin.lineEdit_2.text()) * 10**(-3)
        omega = int(self.myWin.lineEdit.text()) * 1000 * 2 * np.pi
        qm = 2 * self.V * (1.6E-19/1.6605402E-27)/(q * r0**2. * omega**2.)
        return qm

    def update_data(self, count):
        if len(self.count) == 0:
            self.count.append(count)
            self.AMU.append(self.qm())
        elif self.U != self.Uo or self.V != self.Vo:
            self.count.apppend(count)
            self.AMU.append(self.qm())
        else:
            self.ind = bisect(self.AMU, self.qm(), lo=self.ind)
            self.count[-self.ind] += count
    
    def clear(self):
        self.AMU.clear()
        self.count.clear()
        
    def run(self):
        while self.running:            
            timer1 = QTimer()
            timer1.timeout.connect(self.update_plot)
            timer1.start(230)
            self.exec_()

    def update_plot(self):
        # Call Assistant Plot
        self.mutex.lock()
        self.canvas.clear()
        # Monitoring Plot
        if self.state == 'play':
            try:
            #import ipdb; ipdb.set_trace()
                self.canvas.getPlotItem().plot(
                    self.AMU,
                    self.count,
                    #name="Monitor Values",
                    pen=pg.mkPen(color='r', width=2))
                    #symbol='+',
                    #symbolSize=20)
            except:
                pass
        self.mutex.unlock()


    def stop(self):
        self.running = False