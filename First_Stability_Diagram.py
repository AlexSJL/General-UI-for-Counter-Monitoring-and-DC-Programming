#!/usr/bin/env python
# coding: utf-8

# In[1]:


#from sympy import *
import numpy as np
from matplotlib import pyplot as plt


# In[2]:


class Stability_Diagram():
    def __init__(self):
        self.x0 = 0.70625231 #0.70600
        self.x1=0.9091038686429043
        self.x_list1=np.linspace(self.x0, self.x1, 50)
        self.x_list0=np.linspace(0, self.x0, int(np.ceil(self.x0/(self.x_list1[1]-self.x_list1[0]))))
        
    def func0(self, x):
        return 1 - x - x**2./8 + x**3./64 + x**4./1536 + 11*x**5./36864 + 49*x**6./589824 - 55*x**7./9437184 - 265*x**8./113246208

    def func1(self, x):
        return x**2./2 - 7*x**4./128 + 29*x**6./2304 - 68687*x**8./18874368
    
    def func(self, x):
        if x <= self.x0:
            return self.func1(x)
        elif x > self.x0 and x <= self.x1:
            return self.func0(x)
        else:
            return None
    
    def diagram_data_aq(self):
        self.y_list0 = self.func1(self.x_list0)
        self.y_list1 = self.func0(self.x_list1)
        self.x_list=list(np.concatenate((self.x_list0, self.x_list1)))
        self.y_list=list(np.concatenate((self.y_list0, self.y_list1)))
        return [self.x_list, self.y_list], [self.x_list, list(np.zeros(len(self.x_list)))]
    
    # To derive a U-V relation rather than A-Q, some conversion is needed
    def diagram_data_uv(self, omega, e, m, r=6):
        '''
        omega: frequency of RF signal, unit kHz
        e: charge of ion, unit e, electron charge
        m: mass of ion, unit a.u., atomic unit
        r: inscribed radius, unit mm
        '''
        a, _ = self.diagram_data_aq()
        x, y = a
        x_new = []
        y_new = []
        e0 = e * 1.6 * 10**(-19)
        r0 = r * 10**(-3.)
        mass = m * 1.6605402E-27
        omega0 = omega * np.pi * 2. * 10**3.
        
        for val in x:
            temp = (val * mass * r0**2.* omega0**2.) /(2. * e0)
            x_new.append(temp)
        
        for val in y:
            temp = (val * mass * r0**2.* omega0**2.) /(4. * e0)
            y_new.append(temp)
            
        return x_new, y_new




