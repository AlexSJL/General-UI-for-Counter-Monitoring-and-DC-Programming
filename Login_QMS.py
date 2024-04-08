# Import Packages

import sys
sys.path.append('C:/Users/23053/Desktop/QMS Scanning with Isomer Detection/QMS Scanning')

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
from WorkMessage_Thread import Work_Thread
from DCThread import DCThread
from Configuration import Configurations as CF
from config_setting import Doppler, Zero, Detection
from AMU_PlotThread import AMUThread

import sys
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure
from PyQt5.QtGui import QIcon, QGuiApplication
from PyQt5.QtCore import Qt, QTimer, QThread, QMutex
from PyQt5.QtWidgets import *
from PyQt5 import QtCore, QtGui, QtWidgets
import pyqtgraph as pg

from cion.core.sequencer import *
from cion.core.data import *

from unittest import result
from cion.core.gates import *
#from cion.AD9910 import AD9910
import time
from cion.labbrick.labbrick import Labbrick
from cion.core.hardware.zwdc_dds import ZWDX_DDS_NETWORK
from time import strftime
from datetime import datetime

FPGA_Pin_Config = {
    'Strong'   : '10000000 00000000 00000000',    # 1 is close, 0 is open
    'Deep'     : '01000000 00000000 00000000',    # 1 is open, 0 is close
    'Doppler'  : '00100000 00000000 00000000',    # 1 is close, 0 is open
    'Detection': '00011000 00000000 00000000',    # the first 1 is switch box, the second is for close 14GHz EOM
    'Turn off 370'  : '00000001 00000000 00000000',    # 1 is turn off all the 370
    'Pumping'  : '00001110 00000000 00000000',    # first is turn off 14G EOM, second 1 is switch box, third is for open 2GHz EOM
    'Microwave': '00000000 10000000 00000000',    # 1 is open, 0 is close
    'Raman1': '00000000 01000000 00000000',     # 1 is open, 0 is close
    'Raman2': '00000000 00100000 00000000',     # 1 is open, 0 is close
    'EIT1':   '00000000 00010000 00000000',     # 1 is open, 0 is close
    'EIT2':   '00000000 00001000 00000000',     # 1 is open, 0 is close
                  }

Exp_chapter_dict = {
    'Doppler'         :'10000000 00000000 00000000', 
    'Doppler_Only'    :'00000000 00000000 00001111,[10000000 00000000 00000000, 1],[10000000 00000000 00010000,1]',
    'Doppler_OnlyFA'  :'10000000 00000000 00000001,[10000000 00000000 00000000, 1],[10000000 00000000 00000100,1]',
    'Doppler_OnlyMCP' :'10000000 00000000 00000010,[10000000 00000000 00000000, 1],[10000000 00000000 00001000,1]',
    'Pumping':  '10101110 00000000 00000000', 
    'Detection':'10111000 00000000 00000001,[10111000 00000000 00000000, 1],[10111000 00000000 00000100,1]', 
    'Microwave':  '10100001 10000000 00000000', 
    'Raman':  '10101001 01100000 00000000',
    'Raman1':  '10101001 01000000 00000000',
    'Raman2':  '10101001 00100000 00000000',
    'EIT1':  '10101000 00010000 00000000',
    'EIT2':  '10101000 00001000 00000000',
    'EIT':   '10101000 00011000 00000000',
    'Zero': '10101001 00000000 00000000', 
    'Strong': '00000000 00000000 00000000',
    'RedSideBand': '11001001 11111111 00000000',
    
    'Rx_Example' : '10000000 00000000 00000000'
              }

#carrier_chapter = ['Rx_0':  '11001001 10000000 00000000','Rx_1':  '11001001 01000000 00000000','Rx_2':  '11001001 00100000 00000000',...]
#carrier.on(1,3) -> '11001001 1010000'

################ DDS initi ####################

####################################################


class Doppler(BaseGate):
    hardware_amp, hardware_freq, hardware_phase = None, None, None
    def __init__(self, duration, latency = 0, awg_flag = None, amp = None, freq = None, phase = None, label = "Doppler"):
        super().__init__(duration, latency, awg_flag, 'Doppler', amp, freq, phase, label)
        #self.hardware = labbrick_doppler
    
    def update_hardware(self):
        #print("Update Doppler with ", "amp:", self.amp, "freq:", self.freq, "duration: ", self.duration,str(time()))
        labbrick_doppler.freq_update(self.freq)
        None
        
    def reset_hardware(self):
        labbrick_doppler.freq_update(180)
        None
        
class Doppler_OnlyFA(BaseGate):
    hardware_amp, hardware_freq, hardware_phase = None, None, None
    def __init__(self, duration, latency = 0, awg_flag = None, amp = None, freq = None, phase = None, label = "Doppler_OnlyFA"):
        super().__init__(duration, latency, awg_flag, 'Doppler_OnlyFA', amp, freq, phase, label)
        #self.hardware = labbrick_doppler
    
    def update_hardware(self):
        #print("Update Doppler with ", "amp:", self.amp, "freq:", self.freq, "duration: ", self.duration,str(time()))
        labbrick_doppler.freq_update(self.freq)
        None
        
    def reset_hardware(self):
        labbrick_doppler.freq_update(180)
        None
                
class Doppler_OnlyMCP(BaseGate):
    hardware_amp, hardware_freq, hardware_phase = None, None, None
    def __init__(self, duration, latency = 0, awg_flag = None, amp = None, freq = None, phase = None, label = "Doppler_OnlyMCP"):
        super().__init__(duration, latency, awg_flag, 'Doppler_OnlyMCP', amp, freq, phase, label)
        #self.hardware = labbrick_doppler
    
    def update_hardware(self):
        #print("Update Doppler with ", "amp:", self.amp, "freq:", self.freq, "duration: ", self.duration,str(time()))
        labbrick_370_lock_EOM.freq_update(self.freq)
        None
        
    def reset_hardware(self):
        #labbrick_doppler.freq_update(165)
        None
                      
class Doppler_Only(BaseGate):
    hardware_amp, hardware_freq, hardware_phase = None, None, None
    def __init__(self, duration, latency = 0, awg_flag = None, amp = None, freq = None, phase = None, label = "Doppler_Only"):
        super().__init__(duration, latency, awg_flag, 'Doppler_Only', amp, freq, phase, label)
        #self.hardware = labbrick_doppler
    
    def update_hardware(self):
        #print("Update Doppler with ", "amp:", self.amp, "freq:", self.freq, "duration: ", self.duration,str(time()))
        labbrick_370_lock_EOM.freq_update(self.freq)
        None
        
    def reset_hardware(self):
        #labbrick_doppler.freq_update(165)
        None
        
class Strong(BaseGate):
    hardware_amp, hardware_freq, hardware_phase = None, None, None
    def __init__(self, duration, latency = 0, awg_flag = None, amp = None, freq = None, phase = None, label = "Strong"):
        super().__init__(duration, latency, awg_flag, 'Strong', amp, freq, phase, label)
        self.hardware = None
    
    def update_hardware(self):
        print("Update Doppler with ", "amp:", self.amp, "freq:", self.freq, "duration: ", self.duration,str(time()))
        self.hardware.freq_update(self.freq)
        self.hardware.amp_update(self.amp)    
        
class Detection(BaseGate):
    hardware_amp, hardware_freq, hardware_phase = None, None, None
    def __init__(self, duration, latency = 0, awg_flag = None, amp = None, freq = None, phase = None, label = "Detection"):
        super().__init__(duration, latency, awg_flag, 'Detection', amp, freq, phase, label)

    def update_hardware(self):
        #print("Update Doppler with ", "amp:", self.amp, "freq:", self.freq, "duration: ", self.duration,str(time()))
        labbrick_detection.freq_update(self.freq)
        None
        
    def reset_hardware(self):
        labbrick_detection.freq_update(195)
        None

    
class Pumping(BaseGate):
    hardware_amp, hardware_freq, hardware_phase = None, None, None
    def __init__(self, duration, latency = 0, awg_flag = None, amp = None, freq = None, phase = None, label = "Pumping"):
        super().__init__(duration, latency, awg_flag, 'Pumping', amp, freq, phase, label)

    def direct_update_hardware(self):
        assert Optical_pumping.hardware_amp != None and Optical_pumping.hardware_freq != None and Optical_pumping.hardware_phase != None
        pass#return AD9910.WriteProf(1, 3, hardware_amp, hardware_freq, hardware_phase)
    
class Zero(BaseGate):
    hardware_amp, hardware_freq, hardware_phase = None, None, None
    def __init__(self, duration, latency = 0, awg_flag = None, amp = None, freq = None, phase = None, label = "Zero"):
        super().__init__(duration, latency, awg_flag, 'Zero', amp, freq, phase, label)

class Microwave(BaseGate):
    hardware_amp, hardware_freq, hardware_phase = None, None, None
    def __init__(self, duration, latency = 0, awg_flag = None, amp = None, freq = None, phase = None, label = "Microwave"):
        super().__init__(duration, latency, awg_flag, 'Microwave', amp, freq, phase, label)

    def direct_update_hardware(self):
        pass
    
    def reset_hardware(self):
        pass
    
class EIT(BaseGate):
    hardware_amp, hardware_freq, hardware_phase = None, None, None
    def __init__(self, duration, latency = 0, awg_flag = None, amp = None, freq = None, phase = None, label = "EIT"):
        super().__init__(duration, latency, awg_flag, 'EIT', amp, freq, phase, label)

    def direct_update_hardware(self):
        pass
    
    def reset_hardware(self):
        pass
    
class EIT1(BaseGate):
    hardware_amp, hardware_freq, hardware_phase = None, None, None
    def __init__(self, duration, latency = 0, awg_flag = None, amp = None, freq = None, phase = None, label = "EIT1"):
        super().__init__(duration, latency, awg_flag, 'EIT1', amp, freq, phase, label)

    def direct_update_hardware(self):
        pass
    
    def reset_hardware(self):
        pass
    
class EIT2(BaseGate):
    hardware_amp, hardware_freq, hardware_phase = None, None, None
    def __init__(self, duration, latency = 0, awg_flag = None, amp = None, freq = None, phase = None, label = "EIT2"):
        super().__init__(duration, latency, awg_flag, 'EIT2', amp, freq, phase, label)

    def direct_update_hardware(self):
        pass
    
    def reset_hardware(self):
        pass

class Raman(BaseGate):
    hardware_amp, hardware_freq, hardware_phase = None, None, None
    def __init__(self, duration, latency = 0, awg_flag = None, amp = 1, freq = 258, phase = 0, label = "Raman"):
        super().__init__(duration, latency, awg_flag, 'Raman', amp, freq, phase, label)

    def update_hardware(self):
        dds_update(self.amp, self.freq, self.phase, dds_index=1)
    
    def reset_hardware(self):
        pass
        
class Raman_1(BaseGate):
    hardware_amp, hardware_freq, hardware_phase = None, None, None
    def __init__(self, duration, latency = 0, awg_flag = None, amp = 1, freq = 258, phase = 0, label = "Raman"):
        super().__init__(duration, latency, awg_flag, 'Raman1', amp, freq, phase, label)

    def update_hardware(self):
        dds_update(self.amp, self.freq, self.phase, dds_index=1)
    
    def reset_hardware(self):
        pass
    
class Raman_2(BaseGate):
    hardware_amp, hardware_freq, hardware_phase = None, None, None
    def __init__(self, duration, latency = 0, awg_flag = None, amp = 1, freq = 258, phase = 0, label = "Raman"):
        super().__init__(duration, latency, awg_flag, 'Raman2', amp, freq, phase, label)

    def update_hardware(self):
        dds_update(self.amp, self.freq, self.phase, dds_index=1)
    
    def reset_hardware(self):
        pass
        

class Rx(BaseGate):
    hardware_amp, hardware_freq, hardware_phase = None, None, None
    def __init__(self, duration, latency = 0, awg_flag = None, amp = None, freq = None, phase = None, label = "Raman"):
        super().__init__(duration, latency, awg_flag, 'Raman', amp, freq, phase, label)

    def direct_update_hardware(self):
        pass
    
    def reset_hardware(self):
        pass
    
class RedSideBand(AWGBaseGate):
    hardware_amp, hardware_freq, hardware_phase = None, None, None
    def __init__(self, duration, latency = 0, awg_flag = True, amp = None, freq = None, phase = None, label = "RSB"):
        super().__init__(duration, latency, awg_flag, 'RedSideBand', amp, freq, phase, label)
    def direct_update_hardware(self):
        pass
    
    def reset_hardware(self):
        pass


class Rx_Example(AdvanceGate):
    def __init__(self, latency=0, para_table = {}, awg_flag = True):
        super().__init__(latency=latency, para_table=para_table, awg_flag=awg_flag)
        self.pulse_type = 'Rx_Example'




# an example of RSB paratable for sideband cooling

RSB_paratable = {
    'ion_number' : 4,
    'pumping_time' : 30,
    'data_per_ion' : {
        #第一个离子的参数表
        0 : {
            'baseTime' : 20,
            'amp': 0.45, 
            'freq': 4,
            'eta' : 0.1,
            },
        #第二个离子的参数表
        1 : {
            'baseTime' : 20,
            'amp': 0.45,
            'freq': 5,
            'eta': 0.1,
            },
        #第三个离子的参数表
        2 : {
            'baseTime' : 30,
            'amp': 0.45,
            'freq': 5,
            'eta': 0.1,
        },
        #第四个离子的参数表
        3 : {
            'baseTime' : 35,
            'amp': 0.45,
            'freq': 5,
            'eta': 0.05,
        }
    }
}

#RSB_paratable['ion_number'] = 5
#RSB_paratable['data_per_ion']['1']['baseTime'] = 25

# Laguerre polynomial with s=1
def Laguerre(n,x):
    sum = 0
    for k in range(n+1):
        sum += (-1)**k*combinatorial_number(n+1,n-k)*(x**k / math.factorial(k))
    return sum

def sideBandCooling(pumping_time, cycles, para_table):
    result_seq = [sync(all)]
    ion_number = para_table['ion_number']
    pump_time = para_table['pumping_time']
    for n in range(cycles,0,-1):       
        for k in range(0,ion_number):
            eta = para_table['data_per_ion'][k]['eta']
            current_time = para_table['data_per_ion'][k]['baseTime'] / (n**0.5  * Laguerre(n, eta*eta))
            current_time = round(current_time,4)
            amp, freq = para_table['data_per_ion'][k]['amp'], para_table['data_per_ion'][k]['freq']
            temp_RSB = RedSideBand(duration = current_time, amp = amp, freq=freq, phase = 0).on(k)
            result_seq.append(temp_RSB)
        result_seq.append(sync(all))
        result_seq.append(Pumping(pumping_time).on(empty) )
    
    result_seq.append(sync(all))
    return result_seq


def get_com_list():
    Com_List = []
    plist = list(serial.tools.list_ports.comports())
    if len(plist) > 0:
        for i in range(len(plist)):
            Com_List.append(list(plist[i])[0])
    return Com_List

class MyWindow(QMainWindow,Ui_MainWindow):
    def __init__(self, parent=None):
        super(MyWindow, self).__init__(parent)
        self.setupUi(self)  
        self.CF=None
        self.message=[]
        self.setWindowIcon(QIcon('serialscope.ico'))
        self.sendbutton.setToolTip('Click to Open the port')
        self.sendbutton.clicked.connect(self.open_com)
        self.sendcom.activated['QString'].connect(self.port_changed)
        self.sendbot.activated['QString'].connect(self.baud_changed)
        self.pushButton_3.clicked.connect(self.play)
        #self.pushButton_4.clicked.connect(self.clear)
        self.pushButton_4.setEnabled(False)
        self.mkd_save.clicked.connect(self.mkd_sav)
        self.mkd_note = []
        self.marker = False
        self.V = 200
        self.U = 200
        self.counter_port ="COM5"

        #print(self.exp.data.path_prefix) # Indicate the path to store data

    def play(self):
        global ser, serialPort, DC, myWin, plot_thread, exp, detection, AMU_thread #, control_thread
        if self.pushButton_3.text() == "Play": # Start Configurations
            
            #if self.sendbutton.text() != 'Disconnect':
            #    self.show_dialog(str="Device Not Connected",title="No Connection")
            #    return
            
            self.message.append("Configuration Start")
            if self.scanning.isChecked():
                if self.sendbutton.text() == 'Connect':
                    self.show_dialog(str="Device Not Connected",title="No Connection")
                    return
                self.message.append("Working in Scanning Mode")
                if self.auto.isChecked() is False and self.custom.isChecked() is False:
                    self.show_dialog(str="Scanning Mode Not Specified",title="Working Mode needed")
                    self.message.append("Scanning Mode Not Specified")
                    return
                elif self.check_input_validity() is False:
                    self.message.append("Parameters Invalid")
                    return
            elif self.selecting.isChecked():
                if self.sendbutton.text() == 'Connect':
                    self.show_dialog(str="Device Not Connected",title="No Connection")
                    return
                self.message.append("Working in Selecting Mode")
                if self.check_input_validity() is False:
                    self.message.append("Parameters Invalid")
                    return
            else:
                self.message.append("Working in Monitor Mode")
            self.disable_parameter()
            self.pushButton_2.setEnabled(False)
            self.pushButton_4.setEnabled(True)
            self.pushButton_3.setText("Pause")
            
            #self.CF = CF(ser=ser, 
            #             RF_chan=self.comboBox_5.currentText(), 
            #             DC_chan_pos=self.comboBox_3.currentText(), 
            #             DC_chan_neg=self.comboBox_4.currentText(), 
            #             RF_freq = float(self.lineEdit.text()), 
            #             In_radius = float(self.lineEdit_2.text()),
            #             ion_mass = float(self.lineEdit_3.text()), 
            #             ion_charge = float(self.lineEdit_4.text()))
            # Monitoring Plot
            plot_thread.start()
            #control_thread.start()
            #self.Conf()
            # Counter Data Input
            exp.sweep(sequence=detection, myWin=myWin, AMU_thread = AMU_thread)

        elif self.pushButton_3.text() == "Pause": # Current Status: Running -> Pause
            self.enable_parameter()
            self.pushButton_2.setEnabled(True)
            self.message.append("Configuration Pause")
            self.pushButton_3.setText("Resume")
            #control_thread.stop()
        elif self.pushButton_3.text() == "Resume": # Current Status: Pause, click to run
            #if self.sendbutton.text() == 'Connect': # If connection disconnect, show warning
            #    self.show_dialog(str="Device Not Connected",title="No Connection")
            #    return
            if self.scanning.isChecked() or self.selecting.isChecked():
                if self.sendbutton.text() == 'Connect':
                    self.show_dialog(str="Device Not Connected",title="No Connection")
                    return
                if self.check_input_validity() is False:
                    self.message.append("Parameters Invalid")
                    return
            self.disable_parameter()
            self.pushButton_2.setEnabled(False)
            #self.pushButton_4.setEnabled(True)
            self.message.append("Configuration Resume")
            self.pushButton_3.setText("Pause")                                                                      
            #self.CF = CF(ser=ser, 
            #             RF_chan=self.comboBox_5.currentText(), 
            #             DC_chan_pos=self.comboBox_3.currentText(), 
            #             DC_chan_neg=self.comboBox_4.currentText(), 
            #             RF_freq = float(self.lineEdit.text()), 
            #             In_radius = float(self.lineEdit_2.text()), 
            #             ion_mass = float(self.lineEdit_3.text()), 
            #             ion_charge = float(self.lineEdit_4.text()))
            #self.Conf()

    #################################################### Following are Basic Functions of UI ################################################
    def data_analysis(self):
        # Data Analysis only Available 
        if self.pushButton_3.text() == "Pause":
            return
        
        


    def Conf(self):
        if self.selecting.isChecked(): # Generate U and V that only ions specified on "Parameter Settings" can go through
            self.CF.config()
        elif self.scanning.isChecked():
            if self.auto.isChecked():
                Duration = None
                u_set = np.linspace(float(self.Aminputdata), float(self.AMinputdata) , int(self.Sample))
                v_set = np.linspace(float(self.Qminputdata), float(self.QMinputdata) , int(self.Sample))
                if self.Duration.text() != '': # in auto mode, all step have the same duration
                    try:
                        Duration = float(self.Duration.split(',')[0])
                    except:
                        Duration = float(self.Duration)
                for i in range(int(self.Sample)):
                    self.CF.config(u_set[i], v_set[i], update_time = Duration)
            elif self.custom.isChecked():
                Duration = None
                u_set = [float(self.Aminputdata)]
                v_set = [float(self.Qminputdata)]
                Astep = self.Astep.split(',')
                Hstep = self.Hstep.split(',')
                for i in range(len(Astep)):
                    u_set.append(float(Astep[i]))
                    v_set.append(float(Hstep[i]))
                u_set.append(float(self.AMinputdata))
                v_set.append(float(self.QMinputdata))
                if self.Duration.text() != '':
                    try:
                        Duration = self.Duration.split(',')
                        Duration = [float(d) for d in Duration]
                    except:
                        pass
                if Duration:
                    for i in range(len(u_set)):
                        if i >= len(Duration):
                            self.CF.config(u_set[i], v_set[i], update_time = Duration[-1])
                        else:
                            self.CF.config(u_set[i], v_set[i], update_time = Duration[i])
                else:
                    self.CF.config(u_set[i], v_set[i], update_time = Duration)

    def mkd_sav(self):
        if self.mkdwindow.toPlainText() == "":
            self.mkd_note.insert(0, "Plain Marker")
        else:
            self.mkd_note.insert(0, self.mkdwindow.toPlainText())
            self.marker = True
            message = strftime("%Y.%m.%d.%H:%M:%S", time.localtime()) + " wrote: " + self.mkdwindow.toPlainText()
            self.message.append(message)
            self.mkdwindow.clear()

    def Counter_port(self, port: int = 5):
        self.counter_port = "COM" + str(port)
    
    def check_input_validity(self):
        if self.scanning.isChecked() is False and self.selecting.isChecked() is False:
            return True

        if self.lineEdit.text() == '':
            self.show_dialog(str="No RF Frequency Input",title="Invalid Input Parameter")
            return False
        if self.lineEdit_2.text() == '':
            self.show_dialog(str="No Inscribed Radius Input",title="Invalid Input Parameter")
            return False
        if self.selecting.isChecked():
            if self.lineEdit_3.text() == '':
                self.show_dialog(str="No Ion Mass Input",title="Invalid Input Parameter")
                return False
            if self.lineEdit_4.text() == '':
                self.show_dialog(str="No Ion Charge Input",title="Invalid Input Parameter")
                return False
        elif self.scanning.isChecked():
            if self.AMinputdata.text() == '' or self.Aminputdata.text() == '' or self.QMinputdata.text() == '' or self.Qminputdata.text() == '':
                self.show_dialog(str = "Scanning Parameters Invalid", title = "Invalid Input Parameter")
                return False
            if self.auto.isChecked() and self.Sample.text() == '':
                self.show_dialog(str = "Number of Samples not Specified", title = "Invalid Input Parameter")
                return False
            
            if self.custom.isChecked() and (self.Astep.text() == '' or self.Hstep.text() == ''):
                self.show_dialog(str = "Step not Specified", title = "Invalid Input Parameter")
                return False
            
            Astep = self.Astep.split(',')
            Hstep = self.Hstep.split(',')
            if self.custom.isChecked() and len(Astep) != len(Hstep):
                self.show_dialog(str = "Number of Step is different", title = "Invalid Input Parameter")
                return False 
        return True
        
    def open_com(self):
        global ser, serialPort, baudRate, com_list, myWin, Work_message_Thread
        com_list = get_com_list() # Get available Ports
        Work_message_Thread.start()
        self.message.append("Checking Connection...")
        if com_list != []:  
            if serialPort != None and self.sendcom.currentText() != "":# Port is not None and Connect button is clicked
                ser.port = serialPort
                ser.baudrate = baudRate
                if self.sendbutton.text() == 'Connect':
                    ser.open() # Cannot open an open port
                    self.message.append("Checking Connection Complete")
                    #self.messagewindow.append(DC.working_message)
                    self.sendcom.setEnabled(False)
                    self.sendbot.setEnabled(False)
                    self.sendbutton.setText("Disconnect")
                    self.sendbutton.setToolTip('Click to Close Port')
                    print('Port Connect')
                else:
                    ser.close()  # Close the port
                    try:
                        self.CF.cancel_config()
                    except:
                        pass
                    self.sendcom.setEnabled(True)
                    self.sendbot.setEnabled(True)
                    self.sendbutton.setText("Connect")
                    self.sendbutton.setToolTip('Click to Open Port')
                    print('Port Disconnect')
            elif serialPort != None and self.sendcom.currentText() == "":
                myWin.show_dialog(str='Please Choose a Port', title='Warning：No Port Chosen')
                #Work_message_Thread.stop()
            else:  # Fixing
                myWin.port_combo.clear()
                for i in range(len(com_list)):  # Add available Ports to combo box
                    myWin.sendcom.addItem(com_list[i])
                serialPort = com_list[0]  # Setting the first available port by default
        else:  # Show warning dialog
            serialPort = None
            myWin.sendcom.clear()
            myWin.show_dialog(str='No Port Detected', title='Warning：Port Unfound')
            #Work_message_Thread.stop()

    def show_dialog(self,str,title=""):
        # Create QDialog object
        dialog = QDialog()
        layout = QVBoxLayout(dialog)
        label_layout = QHBoxLayout()
        button_layout = QHBoxLayout()
        
        # Create QLabel and QPushButton in the dialog
        lb = QLabel(str, dialog)
        btn = QPushButton('ok', dialog)
        
        lb.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        btn.setSizePolicy(QSizePolicy.Fixed, QSizePolicy.Fixed)
        
        label_layout.addWidget(lb)
        button_layout.addWidget(btn)
        label_layout.setAlignment(Qt.AlignCenter)
        
        layout.addLayout(label_layout)
        layout.addLayout(button_layout)
        btn.clicked.connect(dialog.accept)
    
        # Set dialog title
        dialog.setWindowTitle(title)
        
        # Set the window modality and adjust the size to fit the contents
        dialog.setWindowModality(Qt.NonModal)
        dialog.adjustSize()
        
        # Show the dialog
        dialog.exec_()

    def Timer(self):
        self.count+=1

    def message_display(self):
        if self.message==[]:
            pass
        else:
            for m in self.message:
                self.messagewindow.append(m)
            self.message = []
        
    def port_changed(self, text):
        global ser, serialPort
        serialPort = text
        print('Port：' + serialPort)
        ser.port = serialPort
        
    def baud_changed(self, text):
        global ser, baudRate
        baudRate = int(text)
        print(baudRate)
        ser.baudrate=baudRate
####################################################

#Gloabal Variables and Initialization

if __name__=='__main__':
    app = QApplication(sys.argv)
    ser=serial.Serial(timeout=1)
    DC = DC_Scan(ser)
    myWin = MyWindow()
    #myWin.Counter_port(3)
    #myWin.show()
    plot_thread=PlotThread(myWin.A_vs_Q, DC, myWin)
    Work_message_Thread=Work_Thread(myWin=myWin)
    AMU_thread = AMUThread(myWin=myWin)
    #control_thread = DCThread(DC, plot_thread)
    #myWin.Port_send()
    baudRate = 9600  # baudrate
    timer_value=1
#################################################
    Global_Setting.set_debug_mode(False)
            # import ipdb; ipdb.set_trace()
            # execfile('C:/Users/23053/Desktop/QMS Scanning ver 1.1/QMS Scanning/config_setting.py')
    ion_number = 1
    exp = Experiment(ion_number=ion_number, chapter_dict=Exp_chapter_dict, port="COM5", myWin=myWin) # Check the port first
    seq = exp.last_sequence

    # Activate Detection
    detection_time = 1000000 # 1 second
    detection = exp.new_sequence()
    detection.set_sequence(
                #Zero(100).on(all),
                Doppler(1000, label='Doppler').on(all),
                Zero(2000, label='Zero').on(all),
                Detection(detection_time, label='Detection').on(all))
    exp.repeat=1
    exp.state_flag=True

#################################################
    com_list=get_com_list() #obtain port list

    if com_list!=[]:
        for i in range(len(com_list)):
            myWin.sendcom.addItem(com_list[i])
        serialPort = com_list[0]
    else:
        serialPort = None
        myWin.show_dialog(str='Please Open the Port')
    
    myWin.show()
    QApplication.setHighDpiScaleFactorRoundingPolicy(Qt.HighDpiScaleFactorRoundingPolicy.PassThrough)
    QApplication.processEvents()
    sys.exit(app.exec_())