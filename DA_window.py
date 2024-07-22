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
from PyQt5.QtGui import QIcon
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

from DA_ui import Ui_MainWindow
from data_analysis import DataAnalysis

class DA_Window(QMainWindow,Ui_MainWindow):
    def __init__(self, parent = None, datapath = None, Year = None, Month = None, Day = None, Hour = None):
        super(DA_Window, self).__init__(parent)
        self.setupUi(self)
        self.datapath = datapath
        self.Year = Year
        self.Month = Month
        self.Day = Day
        self.Hour = Hour

        self.DA = DataAnalysis(datapath=self.datapath, Year=self.Year, Month=self.Month, Day=self.Day, Hour=self.Hour)
        for i in range(32):
            self.DA.hist_sort(i + 1)
        self.DA.line_check()
        self.DA.hist_check()
        self.add_marker()

        self.comboBox.currentIndexChanged.connect(self.mode_change)
        self.comboBox_2.currentIndexChanged.connect(self.bin_change)
        self.comboBox_3.currentIndexChanged.connect(self.marker_change)

    def add_marker(self):
        _translate = QtCore.QCoreApplication.translate
        if self.DA.flag is False:
            self.comboBox_3.addItem("")
            self.comboBox_3.setItemText(1, _translate("MainWindow", "Head {} data".format(self.DA.win)))
        else:
            for i in range(len(self.DA.dic)):
                self.comboBox_3.addItem("")
                self.comboBox_3.setItemText(i + 1, _translate("MainWindow", "Marker {}".format(str(i + 1))))

    def mode_change(self):
        if self.comboBox.currentText() == '':
            self.comboBox_2.setEnabled(False)
            self.comboBox_3.setEnabled(False)
            self.pltWidget.clear()
            return
        elif self.comboBox.currentText() == 'Histograms':
            self.pltWidget.clear()
            self.comboBox_2.setEnabled(True)
            self.comboBox_3.setEnabled(False)
        else:
            self.comboBox_2.setEnabled(False)
            self.comboBox_3.setEnabled(True)
            self.pltWidget.clear()

    def bin_change(self):
        if self.comboBox_2.currentText() == '':
            self.pltWidget.clear()
            self.label_4.setText('')
            return
        else:
            self.pltWidget.clear()
            bin = int(self.comboBox_2.currentText()) - 1
            self.pltWidget.getPlotItem().plot(list(range(1, len(self.DA.hist[bin].iloc[1:,0]) + 1)), self.DA.hist[bin].iloc[1:, 1].tolist(), pen = pg.mkPen(color=(0, 114, 189), width=3))
            self.label_4.setText('Evolution of bin {}'.format(str(bin + 1)))

    def marker_change(self):
        if self.comboBox_3.currentText() == '':
            self.pltWidget.clear()
            self.label_4.setText('')
            return
        elif self.comboBox_3.currentText() == "Head {} data".format(self.DA.win):
            self.pltWidget.clear()
            self.pltWidget.getPlotItem().plot(list(range(1, len(self.DA.dic.iloc[:, 0]) + 1)), self.DA.dic.iloc[:, 1].tolist(), pen = pg.mkPen(color=(0, 114, 189), width=3))
            self.label_4.setText('')
        else:
            self.pltWidget.clear()
            ind = int(self.comboBox_3.currentText()[-1]) - 1
            self.pltWidget.getPlotItem().plot(list(range(1, len(self.DA.dic[ind].iloc[:,0]) + 1)), self.DA.dic[ind].iloc[:, 1].tolist(), pen = pg.mkPen(color=(0, 114, 189), width=3))
            self.label_4.setText('Marker {}: '.format(str(ind + 1)) + self.DA.dic[ind].iloc[0,3])


if __name__ == '__main__':
    year = '2024'
    Month = '04'
    day = '15'    
    Hour = '15'
    datapath = 'D:/Data/'+ year + '/' + year + Month
    #DA = DataAnalysis(datapath=datapath, Year=year, Month=Month, Day=day, Hour=Hour)
    app = QApplication(sys.argv)
    mywin = DA_Window(datapath=datapath, Year=year, Month=Month, Day=day, Hour=Hour)
    mywin.show()
    QApplication.processEvents()
    sys.exit(app.exec_())