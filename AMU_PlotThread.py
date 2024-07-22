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
qmax = 0.9091038686429043

class AMUThread(QThread):
    def __init__(self, myWin):
        super().__init__()
        self.myWin = myWin
        self.canvas = myWin.Count_vs_AMU
        self.mutex = QMutex() 
        self.Uo = myWin.U
        self.Vo = myWin.V
        self.SD = SD()
        self.plotx = []
        self.ploty = []
        #self.config_pair = []
        self.qm_lst = None
        self.a_list = None
        self.q_list = None
        self.ind = 0
        self.win = 150
        self.running = True
        self.state = 'play'
        self.myWin.pushButton_4.clicked.connect(self.clear)
        self.r0 = int(self.myWin.lineEdit_2.text()) * 10**(-3)
        self.omega = int(self.myWin.lineEdit.text()) * 1000 * 2 * np.pi
        if self.myWin.spectrum_debug == True:
            self.VM = 200
            self.Vm = 150
            self.UM = self.VM * 0.2
            self.Um = self.Vm * 0.2
            self.temp0 = list(np.linspace(self.Vm, self.VM, 200))
            self.temp1 = list(np.linspace(self.Um, self.UM, 200))
            #self.temp1 = [int(temp) for temp in self.temp1]
            qmmin = self.qm(min(self.temp0))
            qmmax = max(300, self.qm(max(self.temp0)))
            self.qm_lst = list(np.linspace(qmmin, qmmax, 1000)) # mass over charge ratio list
            '''
            self.q_list = [[self.compute_q(V, qm) for qm in self.qm_lst] for V in self.temp0] # q parameter list for each qm value under different V voltages
            self.a_list = [[self.compute_a(U, qm) for qm in self.qm_lst] for U in self.temp1] # a parameter list for each qm value under different U voltages
            self.stable = [[self.SD.func(q) for q in qlst] for qlst in self.q_list] # edge of stable region for each qm value
            self.stable = [[q if q else -1 for q in qlst] for qlst in self.q_list]
            for i in self.stable:
                for j in i:
                    if j == -1:
                        print('yes')
                        break
            self.a_list = np.array(self.a_list)
            self.stable = np.array(self.stable)
            self.count = self.stable > self.a_list
            self.temp1 = np.array(self.temp1)
            '''

    def compute_a(self, U, qm):
         return U * (1.6E-19/1.6605402E-27)/(qm * self.r0**2. * self.omega**2.)

    def compute_q(self, V, qm):
        return  2 * V * (1.6E-19/1.6605402E-27)/(qm * self.r0**2. * self.omega**2.)

    def qm(self, V):
        return 2 * V * (1.6E-19/1.6605402E-27)/(q * self.r0**2. * self.omega**2.)
        
    def play(self):
        self.state = 'play'

    def pause(self):
        self.state = 'pause'

    def update_data(self, count):
        if len(self.plotx) == 0:
            #self.count.append(count)
            #self.AMU.append(self.qm(self.Vo))
            self.plotx = self.qm_lst
            self.ploty = list(np.zeros(len(self.plotx))) 
            #self.plot = [[self.qm(self.Vo), count]]
            #self.config_pair.append((self.myWin.V, self.myWin.U))
        #elif self.myWin.U != self.Uo or self.myWin.V != self.Vo: # Configuration Changed
        else:    
            #self.Uo = self.myWin.U
            #self.Vo = self.myWin.V
            if self.myWin.spectrum_debug:
                self.Vo = self.myWin.V[0]
            else:
                self.Vo = self.myWin.V
            #if (self.Vo, self.Uo) in self.config_pair:# Configuration exists before
                #ind = self.config_pair.index((self.Vo, self.Uo))
            '''
            try:
                idx = self.temp1.index(self.Uo)
            except:
                idx = np.abs(self.Uo - self.temp1).argmin()
            rng = self.count[idx][:]
            avg = (np.ones(len(rng)) * count / sum(rng)) * rng
            self.ploty += avg
            '''
            qm = self.qm(self.Vo)
            try:
                idx = self.qm_lst(qm)
            except:
                idx = np.abs(qm - self.qm_lst).argmin()
                
            self.ploty[idx] += count
            #self.plot[ind][1] += count
            #else:# Configuration Does not Exist
            #    self.config_pair.append((self.Vo, self.Uo))
                #self.count.append(count)
                #self.AMU.append(self.qm(self.Vo))
            #    self.plot.append([self.qm(self.Vo), count])
        #else:# Configuration has not changed
        #    ind = self.config_pair.index((self.Vo, self.Uo))
        #    self.plot[ind][1] += count
    
    def clear(self):
        #self.AMU.clear()
        #self.count.clear()
        #self.plot.clear()
        #self.config_pair.clear()
        self.plotx.clear()
        self.ploty.clear()
        
    def run(self):
        while self.running:            
            timer1 = QTimer()
            timer1.timeout.connect(self.update_plot)
            timer1.start(230)
            self.exec_()

    def update_plot(self):
        # Call Assistant Plot
        '''
        if len(self.AMU) > self.win:
            self.x = [qm[0] for qm in self.plot][-self.win:]
            self.y = [qm[1] for qm in self.plot][-self.win:]
        else:
        '''
        #self.x = [qm[0] for qm in self.plot]
        #self.y = [qm[1] for qm in self.plot]

        self.mutex.lock()
        # Monitoring Plot
        if self.myWin.spectrum_debug:
            self.myWin.spectrometer_debug()
        if self.state == 'play':
            self.canvas.clear()
            try:
                self.canvas.getPlotItem().plot(
                    self.plotx,
                    self.ploty,
                    name="Monitor Values",
                    #pen=pg.mkPen(color='r', width=2),
                    pen = None,
                    symbol='o',
                    symbolBrush = pg.mkBrush(color=(0, 114, 189)),
                    symbolSize=5)
                '''
                    self.canvas.getPlotItem().plot(
                        [self.x[-1]],
                        [self.y[-1]],
                        name="Latest Monitor Values",
                        #pen=pg.mkPen(color='r', width=2),
                        pen = None,
                        symbol='o',
                        symbolBrush = 'r',
                        symbolSize=5)
                    '''
            except:
                pass
        else:
            self.canvas.clear()
            #self.spectro = sorted(self.plot, key = lambda x:x[0])
            #self.x = [qm[0] for qm in self.spectro]
            #self.y = [qm[1] for qm in self.spectro]
            self.canvas.getPlotItem().plot(
                    self.plotx,
                    self.ploty,
                    name="Monitor Values",
                    pen=pg.mkPen(color='r', width=2))
                    #symbolBrush = pg.mkBrush(color=(0, 114, 189)),
                    #symbol='o',
                    #symbolSize=5)
        self.mutex.unlock()
        
    def stop(self):
        self.running = False