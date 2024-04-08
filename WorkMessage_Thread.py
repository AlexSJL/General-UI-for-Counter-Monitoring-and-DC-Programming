# Import Packages
import time
import numpy as np
from matplotlib import pyplot as plt
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

# This play for displaying working message in message window
class Work_Thread(QThread):
    def __init__(self, myWin=None):
        super().__init__()
        self.myWin=myWin
        self.running=True
        self.state=None
        self.mutex = QMutex()

    def run(self):
        while self.running:           
            timer1 = QTimer()
            timer1.timeout.connect(self.message_update)
            timer1.start(550)
            QApplication.processEvents()
            self.exec_()

    def message_update(self):
        if self.myWin.message==[]:
            pass
        else:
            self.mutex.lock()
            for m in self.myWin.message:
                self.myWin.messagewindow.append(m)
            self.myWin.message = []
            self.mutex.unlock()
            
    def stop(self):
        self.running = False