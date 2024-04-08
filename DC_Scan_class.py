#!/usr/bin/env python
# coding: utf-8

# In[1]:


from port_ctrl1 import Rigol_DCPort
from CAENDesktopHighVoltagePowerSupply1 import CAENDesktopHighVoltagePowerSupply, OneCAENChannel
import pyvisa as visa
import time
import numpy as np
import serial
import serial.tools.list_ports 
from matplotlib import pyplot as plt


# Constrain RF data in the range between 0-6 V
class DC_Scan:
    def __init__(self,ser,Rigol_address="USB0::0x1AB1::0x0E11::DP8B242401816::INSTR",Hrange=None,Arange=None,Achannel=None,Hchannel=None, Hchannel1=None, sampling=None, Astep=None, Hstep=None, intv=None, mode=None):
        self.RF = Rigol_DCPort(Rigol_address)
        self.DC = CAENDesktopHighVoltagePowerSupply(ser)
        self.Hrange=Hrange
        self.Arange=Arange
        self.Achannel=Achannel
        self.Hchannel=Hchannel
        self.Hchannel1= Hchannel1
        self.sampling=sampling
        self.Astep=Astep
        self.Hstep=Hstep
        self.intv=intv
        self.interval=None
        self.working_message = None
        self.error_message = None
        self.error = False
        self.mode=mode
        
    def RF_validity(self):
        if self.Arange is None:
            self.error_message = "No RF Input"
            return False
        for vol in range(len(self.Arange)):
            if self.Arange[vol] < 0 or self.Arange[vol] > 6:
                self.error_message = "Invalid RF Amplitude Range"
                return False
            else:
                self.Arange[vol] = float(self.Arange[vol])
        return True

    def DC_validity(self):
        if self.Hrange is None:
            self.error_message = "No DC Input"
            return False
        for vol in range(len(self.Hrange)):
            if vol < 0 or vol > 3000:
                self.error_message = "Invalid DC Voltage Range"
                return False
            else:
                self.Hrange[vol] = float(self.Hrange[vol])
        return True
    
    def sampling_validity(self):
        if self.Hrange[0] != self.Hrange[1] and self.Arange[0] != self.Arange[1]:
            self.curr_q = np.linspace(self.Hrange[0], self.Hrange[1], self.sampling)
            if np.abs(self.curr_q[1] - self.curr_q[0]) > 40:
                self.sampling = int(np.ceil(np.abs(self.Hrange[1] - self.Hrange[0]) / 40))
            self.curr_q = np.linspace(self.Hrange[0], self.Hrange[1], self.sampling)
            self.curr_a = np.linspace(self.Arange[0], self.Arange[1], self.sampling)
        elif self.Hrange[0] == self.Hrange[1] and self.Arange[0] != self.Arange[1]:
            self.curr_q = self.Hrange[0] * np.ones(self.sampling)
            self.curr_a = np.linspace(self.Arange[0], self.Arange[1], self.sampling)
        elif self.Arange[0] == self.Arange[1] and self.Hrange[0] != self.Hrange[1]:
            self.curr_q = np.linspace(self.Hrange[0], self.Hrange[1], self.sampling)
            if np.abs(self.curr_q[1] - self.curr_q[0]) > 40:
                self.sampling = int(np.ceil(np.abs(self.Hrange[1] - self.Hrange[0]) / 40))
            self.curr_q = np.linspace(self.Hrange[0], self.Hrange[1], self.sampling)
            self.curr_a = self.Arange[0] * np.ones(self.sampling)
        else:
            self.curr_q = self.Hrange[0] * np.ones(self.sampling)
            self.curr_a = self.Arange[0] * np.ones(self.sampling)
            
        
    def step_validity(self):
        self.curr_q_0 = [Hrange[0]] + Hstep + [Hrange[1]]
        self.curr_a_0 = [Arange[0]] + Astep + [Arange[1]]
        self.curr_q = []
        self.curr_a = []
        self.ind=[0]
        for i in range(len(self.curr_q_0) - 1):
            if np.abs(self.curr_q_0[i] - self.curr_q_0[i+1]) > 40:
                temp_samp = int(np.ceil(np.abs(self.curr_q[i+1] - self.curr_q_0[i]) / 40))
                temp_q = np.linspace(self.curr_q_0[i], self.curr_q_0[i+1],temp_samp)
                temp_a = np.linspace(self.curr_a_0[i], self.curr_a_0[i+1],temp_samp)
                self.curr_q += temp_q[1:]# first element have been attached to the list
                self.curr_a += temp_a[1:]# first element have been attached to the list
                self.ind.append(len(self.curr_q)-1)
            else:
                self.curr_q.append(self.curr_q_0[i+1])
                self.curr_a.append(self.curr_a_0[i+1])
                self.ind.append(len(self.curr_q)-1)
            
    def duration_check(self):
        if self.mode == 0:
            if self.intv is None or (type(self.intv) is int and self.intv <= 3):
                self.interval = 3 * np.ones(self.sampling)
            elif type(self.intv) is int and self.intv > 3:
                self.interval = self.intv * np.ones(self.sampling)
            elif type(self.intv) is list and len(self.intv) != len(self.curr_a):
                self.error_message = 'Number of data in duration does not meet the number of data to be scanned.'
                return False
            elif type(self.intv) is list and len(self.intv) == len(self.curr_a):
                for i in range(len(self.intv)):
                    if self.intv[i] < 3:
                        self.intv[i] = 3
                self.interval = self.intv
        elif self.mode == 1:
            if self.intv is None or (type(self.intv) is int and self.intv < 30):
                self.interval = 30 * np.ones(self.sampling)
            elif type(self.intv) is list and len(self.intv) != len(self.curr_a):
                raise ValueError(f'Number of data in duration does not meet the number of data to be scanned.')
                return False
            elif type(self.intv) is list and len(self.intv) == len(self.curr_a):
                for i in range(len(self.intv)):
                    if self.intv[i] < 30:
                        self.intv[i] = 30
                self.interval = self.intv
        return True
    
    def cancel_configuration(self):
        self.RF.reset()
        self.RF.ChannelOff(self.Achannel)
        self.DC.query(CMD="SET", PAR="VSET", CH=self.DC.Hchannel[-1], VAL=0)
        self.DC.query(CMD="SET", PAR="ISET", CH=self.DC.Hchannel[-1], VAL=0)
        self.DC.query(CMD="SET", PAR="OFF", CH=self.DC.Hchannel[-1])
        
    def RF_set(self, VAL):
        self.RF.set_dc_fix_value(voltage = VAL, current=1, channel=self.Achannel)
        
    def DC_set(self, VAL, Hchannel):
        self.DC.query(CMD="SET", PAR="VSET", CH=Hchannel[-1], VAL=VAL)
        self.DC.query(CMD="SET", PAR="ISET", CH=Hchannel[-1], VAL=VAL/9)
    
    def RF_channel(self, state="OFF"):
        if state == "ON":
            self.RF.ChannelOn(self.Achannel)
        else:
            self.RF.ChannelOff(self.Achannel)
    
    def DC_channel(self, Channel, state="OFF"):
        if state == "ON":
            self.DC.query(CMD="SET", PAR="ON", CH=Channel[-1])
        else:
            self.DC.query(CMD="SET", PAR="OFF", CH=Channel[-1])
            
    def RF_vol_monitor(self):
        return self.RF.read_dc_v(channel = self.Achannel)
    
    '''
    def DC_scan(self, Arange: list, Hrange: list, Astep=None, Hstep=None, intv=None, samp=None, Achannel:str = None, Hchannel:str = None):
    
    
            #Input
            #Arange    param: Org and Dest of RF, a list
            #Hrange    param: Org and Dest for H, a list
            #Astep     param: a list of specified value (Not include org and dest, order insensitive) or just a constant
            #Hstep     param: a list of specified value (Not include org and dest, order insensitive) or just a constant
            #intv      param: time constant, integer or list of integers
            #samp      param: # of data points, when step of each one is specified,
            #Achannel  param: device channel
            #Hchannel  param: device channel
            
            
            # Check Valid Input Working Mode
            self.working_message = "Working Mode Checking..."
            
            self.working_message = "Working Mode Configuration Complete."
            time.sleep(0.1)
            
            self.working_message = "Working Mode Configuration Complete."
            
            # Check Input Channel
            if Achannel is None or Hchannel is None:
                self.error = True
                raise ValueError(f'Please specify the output channel of both power supply.')
                
            curr_v = [] # monitored value of RF amplitude
            curr_u = [] # monitored valur of DC voltage
            
            # Turn on the output port for supply
            self.DC.query(CMD="SET", PAR="ON", CH=Hchannel[-1])
            time.sleep(5)
            self.DC.query(CMD="SET", PAR="ISET", CH=Hchannel[-1], VAL=300)
            self.DC.query(CMD="SET", PAR="VSET", CH=Hchannel[-1], VAL=curr_q[0])
            if curr_q[0] <= 3000:
                time.sleep(30) # Waiting for CAEN to be set to the starting value
            else:
                time.sleep(60)
            self.RF.ChannelOn(channel=Achannel)
            #plt.ion()
            
            for i in range(sampling):
                self.RF.set_dc_fix_value(curr_a[i], 2, channel=Achannel)
                self.DC.query(CMD="SET", PAR="VSET", CH=Hchannel[-1], VAL=curr_q[i])
                #H.send_command(CMD="SET", PAR="ON", CH=Hchannel[-1])
                #time.sleep(30)
                
                for _ in range(int(interval[i])):
                    # Do not try to measure output with Power supply
                    Hmon = H.get_single_channel_parameter("VMON", Hchannel[-1])
                    if type(Hmon) != float:
                        continue
                        
                    curr_v.append(RF.read_dc_v(channel = Achannel))    
                    time.sleep(1)
                    
            # After the entire process, close the output of both device
            self.DC.query(CMD="SET", PAR="VSET", CH=0, VAL=0)
            self.DC.query(CMD="SET", PAR="ISET", CH=0, VAL=0)
            time.sleep(0.5)
            self.DC.query(CMD="SET", PAR="OFF", CH=Hchannel[-1])
            self.RF.ChannelOff(channel=Achannel)
            self.RF.reset()
            self.complete = True
     '''
