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
from Configuration import Configurations as CF
from config_setting import Doppler, Zero, Detection

import sys
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure
from PyQt5.QtGui import QIcon
from PyQt5.QtCore import Qt, QTimer, QThread, QMutex
from PyQt5.QtWidgets import *
from PyQt5 import QtCore, QtGui, QtWidgets
import pyqtgraph as pg

from cion.core.sequencer import *
from cion.core.data import *


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
        self.plot_thread=None
        self.control_thread=None
        self.CF=None
        self.message=[]
        self.setWindowIcon(QIcon('serialscope.ico'))
        self.sendbutton.setToolTip('Click to Open the port')
        self.sendbutton.clicked.connect(self.open_com)
        self.sendcom.activated['QString'].connect(self.port_changed)
        self.sendbot.activated['QString'].connect(self.baud_changed)
        self.pushButton_3.clicked.connect(self.play)
        self.pushButton_4.clicked.connect(self.clear)
        self.pushButton_4.setEnabled(False)
        self.message_display_timer=QTimer()
        self.message_display_timer.timeout.connect(self.message_display)
        self.counter_port ="COM5"
        self.message_display_timer.start(100)

        #print(self.exp.data.path_prefix) # Indicate the path to store data

    def play(self):
        global ser, serialPort, DC, myWin
        if self.pushButton_3.text() == "Play": # Start Configurations
            if self.sendbutton.text() != 'Disconnect':
                self.show_dialog(str="Device Not Connected",title="No Connection")
                return
            if self.check_input_validity() is False:
                self.clear()
                return
            self.message.append("Configuration Start")
            self.disable_parameter()
            self.pushButton_3.setText("Pause")
            #self.CF = CF(ser=ser, 
            #             RF_chan=self.comboBox_5.currentText(), 
            #             DC_chan_pos=self.comboBox_3.currentText(), 
            #             DC_chan_neg=self.comboBox_4.currentText(), 
            #             RF_freq = float(self.lineEdit.text()), 
            #             In_radius = float(self.lineEdit_2.text()),
            #             ion_mass = float(self.lineEdit_3.text()), 
            #             ion_charge = float(self.lineEdit_4.text()))
            #self.CF.config()

            # Monitoring Plot
            self.plot_thread=PlotThread(self.A_vs_Q, DC, myWin)
            #self.control_thread=DCThread(DC, self.thread)
            self.plot_thread.start()
            #self.control_thread.start()
            
            # Default Setting for Counter
            Global_Setting.set_debug_mode(False)
            execfile('config_setting.py')
            ion_number = 1
            self.exp = Experiment(ion_number=ion_number, chapter_dict=Exp_chapter_dict, port="COM5") # Check the port first
            self.seq = self.exp.last_sequence

            # Activate Detection
            detection_time = 1000000
            self.detection = self.exp.new_sequence()
            self.detection.set_sequence(
                #Zero(100).on(all),
                Doppler(1000, label='Doppler').on(all),
                Zero(2000, label='Zero').on(all),
                Detection(detection_time, label='Detection').on(all))
            self.exp.repeat=1
            self.exp.state_flag=True
            
            # Counter Data Input
            self.exp.sweep(sequence=self.detection, myWin=myWin)
            
        elif self.pushButton_3.text() == "Pause": # Current Status: Running -> Pause
            self.enable_parameter()
            self.pushButton_3.setText("Resume")
            self.plot_thread.pause()
            #self.control_thread.stop()
            #self.message_display_timer.stop()
        elif self.pushButton_3.text() == "Resume": # Current Status: Pause, click to run
            if self.sendbutton.text() != 'Connect': # If connection disconnect, show warning
                self.show_dialog(str="Device Not Connected",title="No Connection")
                return
            if self.check_input_validity() is False:
                self.clear()
                return
            self.message_display_timer.start(100)
            self.disable_parameter()
            self.pushButton_3.setText("Pause")                                                                      
            self.CF = CF(ser=ser, 
                         RF_chan=self.comboBox_5.currentText(), 
                         DC_chan_pos=self.comboBox_3.currentText(), 
                         DC_chan_neg=self.comboBox_4.currentText(), 
                         RF_freq = float(self.lineEdit.text()), 
                         In_radius = float(self.lineEdit_2.text()), 
                         ion_mass = float(self.lineEdit_3.text()), 
                         ion_charge = float(self.lineEdit_4.text()))
            #self.CF.config()
            self.plot_thread.play()
            #self.control_thread=DCThread(DC, self.thread)
            #self.control_thread.start()
            
    def clear(self):
        # When there is no data, Clear button would not work
        if self.pushButton_3.text() == "Play":
            return
        # There is data and thread are still running, then stop all threads
        if self.pushButton_3.text() == "Pause":
            self.plot_thread.stop()
            #self.control_thread.stop()
            self.message_display_timer.stop()
            self.pushButton_3.setText("Play")
        self.enable_parameter()
        #self.CF.clear()
        self.pushButton_3.setText("Play")
        self.A_vs_Q.clear()
        self.Counter_Histogram.clear()
        self.Count_vs_t.clear()
        self.Q_vs_t.clear()
        
    
    #################################################### Following are Basic Functions of UI ################################################
    #def data_save(self):       

    def Counter_port(self, port: int = 3):
        self.counter_port = "COM" + str(port)
    
    def check_input_validity(self):
        if self.lineEdit.text() == '':
            self.show_dialog(str="No RF Frequency Input",title="Invalid Input Parameter")
            return False
        if self.lineEdit_2.text() == '':
            self.show_dialog(str="No Inscribed Radius Input",title="Invalid Input Parameter")
            return False
        if self.lineEdit_3.text() == '':
            self.show_dialog(str="No Ion Mass Input",title="Invalid Input Parameter")
            return False
        if self.lineEdit_4.text() == '':
            self.show_dialog(str="No Ion Charge Input",title="Invalid Input Parameter")
            return False
        return True
        
    def open_com(self):
        global ser, serialPort, baudRate, com_list
        com_list = get_com_list() # Get available Ports
        self.message_display_timer.start(100)
        self.message.append("Checking Connection...")
        if com_list != []:  
            if serialPort != None and self.sendcom.currentText() != "":# Port is not None and Connect button is clicked
                ser.port = serialPort
                ser.baudrate = baudRate
                if self.sendbutton.text() == 'Connect':
                    ser.open() # Cannot open an open port
                    #self.timer.start(timer_value) #Start Timer for message display
                    self.message.append("Checking Connection Complete")
                    self.sendcom.setEnabled(False)
                    self.sendbot.setEnabled(False)
                    self.sendbutton.setText("Disconnect")
                    self.sendbutton.setToolTip('Click to Close Port')
                    print('Port Connect')
                else:
                    ser.close()  # Close the port
                    self.sendcom.setEnabled(True)
                    self.sendbot.setEnabled(True)
                    self.sendbutton.setText("Connect")
                    self.sendbutton.setToolTip('Click to Open Port')
                    print('Port Disconnect')
            elif serialPort != None and self.sendcom.currentText() == "":
                self.show_dialog(str='Please Choose a Port', title='Warning：No Port Chosen')
            else:  # Fixing
                self.port_combo.clear()
                for i in range(len(com_list)):  # Add available Ports to combo box
                    self.sendcom.addItem(com_list[i])
                serialPort = com_list[0]  # Setting the first available port by default
        else:  # Show warning dialog
            serialPort = None
            self.sendcom.clear()
            self.show_dialog(str='No Port Detected', title='Warning：Port Unfound')
        self.message_display_timer.stop()

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
ser=serial.Serial(timeout=1)
DC = DC_Scan(ser)
app = QApplication(sys.argv)
myWin = MyWindow()
myWin.Counter_port(3)
myWin.show()
#myWin.Port_send()
baudRate = 9600  # baudrate
timer_value=1
#################################################
com_list=get_com_list() #obtain port list

if com_list!=[]:
    for i in range(len(com_list)):
        myWin.sendcom.addItem(com_list[i])
    serialPort = com_list[0]
else:
    serialPort = None
    myWin.show_dialog(str='Please Open the Port')

sys.exit(app.exec_())