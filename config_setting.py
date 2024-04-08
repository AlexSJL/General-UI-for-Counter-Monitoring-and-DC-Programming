### 在此文件中具体实现各种类型的pulse，同时进一步明确每种pulse所对应的硬件接口
from unittest import result
from cion.core.gates import *
#from cion.AD9910 import AD9910
import time
from cion.labbrick.labbrick import Labbrick
from cion.core.hardware.zwdc_dds import ZWDX_DDS_NETWORK

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