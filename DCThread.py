import sys
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure
from PyQt5.QtGui import QIcon
from PyQt5.QtCore import Qt, QTimer, QThread, QMutex, pyqtSignal
from PyQt5.QtWidgets import *
from PyQt5 import QtCore, QtGui, QtWidgets
import pyqtgraph as pg

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

# This thread for visiting devices for monitoring values
class DCThread(QThread):
    stop_signal = pyqtSignal()
    def __init__(self, DC, plotthread):
        super().__init__()
        self.DC=DC    
        self.mutex = QMutex()
        self.thread=plotthread
        self.running = True
        self.state=None
        self.Hmon = None
        
    def run(self):
        while self.running:            
            timer = QTimer()
            timer.timeout.connect(self.monitor)
            timer.start(10)
            QApplication.processEvents()
            self.exec_()
    
    def monitor(self):
        if self.state=="play":
            self.mutex.lock()
            Hm = self.DC.DC.get_single_channel_parameter("VMON", self.DC.Hchannel[-1])
            RF_val=float(self.DC.RF.read_dc_v())
            try:
                self.Hmon=float(Hm)
                self.thread.update_data2(RF_val, self.Hmon)
            except:
                pass
            self.mutex.unlock()
    
    def pause(self):
        self.state = "pause"

    def play(self):
        self.state = "play"
    
    def stop(self):
        #self.mutex.lock()
        #try:
        #    self.DC.RF.reset()
        #    self.DC.RF_channel
        #    self.DC.DC.query(CMD="SET", PAR="VSET", CH=self.DC.Hchannel[-1], VAL=0)
        #    self.DC.DC.query(CMD="SET", PAR="ISET", CH=self.DC.Hchannel[-1], VAL=0)
        #    self.DC.DC.query(CMD="SET", PAR="OFF", CH=self.DC.Hchannel[-1])
        #except Exception as e:
        #    print(f"Error in stopping thread: {e}")
        self.running = False
        #self.mutex.unlock()
        
        