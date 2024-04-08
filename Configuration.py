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
from QMS_mainwindow import Ui_MainWindow
from PlotThread import PlotThread
from DCThread import DCThread
from First_Stability_Diagram import Stability_Diagram as SD
from Amp_DC_converter import Amp_DC_converter

import sys
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure
from PyQt5.QtGui import QIcon
from PyQt5.QtCore import Qt, QTimer, QThread, QMutex
from PyQt5.QtWidgets import *
from PyQt5 import QtCore, QtGui, QtWidgets
import pyqtgraph as pg

class Configurations():
    def __init__(self, ser, RF_chan, DC_chan_pos, DC_chan_neg, RF_freq, In_radius, ion_mass, ion_charge):
        self.DC = DC_Scan(ser,Achannel=RF_chan,Hchannel=DC_chan_pos, Hchannel1=DC_chan_neg)
        self.RF_freq=float(RF_freq) * 10**3.
        self.In_radius=float(In_radius) * 10**(-3.)
        self.ion_mass=float(ion_mass) * 1.6605402E-27
        self.ion_charge=float(ion_charge) * 1.6 * 10**(-19)
        self.DC_chan_pos = DC_chan_pos
        self.DC_chan_neg = DC_chan_neg
        self.SD=SD()
        self.x0=self.SD.x0
        self.y0=self.SD.func0(self.x0)
        self.u_con = self.y0 * self.ion_mass * self.In_radius**2.* self.RF_freq**2. /(4. * self.ion_charge)
        self.v_con = self.x0 * self.ion_mass * self.In_radius**2.* self.RF_freq**2. /(2. * self.ion_charge)
        self.u_ref = Amp_DC_converter("amplitude_data.csv", 4)
        self.v_ref = Amp_DC_converter("DC_data.csv", 4)
        self.v_set = self.v_ref.converter(self.v_con)
        self.u_set = self.u_ref.converter(self.u_con)
        self.timer = QTimer()
        self.timer.timeout.connect(self.Timer)
        self.count = 0
    
    def config(self, update_time = None, u=None, v= None):
        if update_time:
            update_time = update_time
        else:
            update_time = 10
        self.DC.RF_channel(state="ON")
        self.DC.DC_channel(self.DC_chan_pos, state="ON")
        self.DC.DC_channel(self.DC_chan_neg, state="ON")
        
        if u and v:
            # First set the amplitude of RF
            self.DC.RF_set(u)
            
            # Wait 1 seconds for RF configuration
            self.timer.start(100)
            while self.count < update_time:
                QApplication.processEvents()
            self.timer.stop()
            self.count = 0
        
            # Then set the DC offset
            self.DC.DC_set(v,self.DC_chan_pos)
            self.DC.DC_set(v,self.DC_chan_neg)
        else:
            # First set the amplitude of RF
            self.DC.RF_set(self.v_set)    
            
            # Wait 1 seconds for RF configuration
            self.timer.start(100)
            while self.count < update_time:
                QApplication.processEvents()
            self.timer.stop()
            self.count = 0
        
            # Then set the DC offset
            self.DC.DC_set(self.u_set,self.DC_chan_pos)
            self.DC.DC_set(self.u_set,self.DC_chan_neg)

    def cancel_config(self):
        self.DC.RF_set(0)
        self.DC.DC_set(0,self.DC_chan_pos)
        self.DC.DC_set(0,self.DC_chan_neg)

        # clear prior settings
        self.DC.RF_set(0)
        self.DC.DC_set(0,self.DC_chan_pos)
        self.DC.DC_set(0,self.DC_chan_neg)

        # Wait At least 30 seconds to complete
        self.DC.RF_channel(state="OFF")
        self.DC.DC_channel(self.DC_chan_pos, state="OFF")
        self.DC.DC_channel(self.DC_chan_neg, state="OFF")
        self.timer.start(1000)
        while self.count < 30:
            QApplication.processEvents()
        self.timer.stop()
        self.count = 0

    def Timer(self):
        self.count += 1