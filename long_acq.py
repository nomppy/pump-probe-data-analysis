# -*- coding: utf-8 -*-
"""
Created on Tue Jul 18 13:57:03 2023

@author: Kenneth Sun
"""


import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import pyvisa # https://pyvisa.readthedocs.io/en/latest/
import time
from newportxps import NewportXPS

# connect to oscilloscope
# in most cases this will work without any changes
# if not, locate the correct resource name and replace line 20
# if the connection is successful, the console will print the scope's name
rm = pyvisa.ResourceManager()
scope = rm.open_resource(rm.list_resources()[-1])
# establish connection to XPS controller
xps = NewportXPS('192.168.254.254', username='Administrator', password='Administrator')
print(scope.query('*IDN?'))

class Stage:
    def __init__(self, group, axis):
        self.name= group+'.'+axis
        self.pos=xps.get_stage_position(self.name)
    
    def read(self):
        self.pos=xps.get_stage_position(self.name)
        return self.pos

        return [self.x,self.y,self.z] 
    
    def mov(self, pos):
        xps.move_stage(self.name, pos)
        self.pos=xps.get_stage_position(self.name)
        return self.pos

DelayEO=Stage('Delay','ASOSP')    

def acq_wav (chan=None, form=None, points=None, timeout=60000):
    """
    Acquires a waveform from the scope, using the specified channel, form, and point
    parameters, and returns the wavefrom as a numpy array. 

    Parameters
    ----------
    chan : int, optional
        The channel to acquire from. The default is None, which will use the 
        scope's current channel setting.
    form : str, optional
        The format of the waveform. The default is None, which will use the
        scope's current format setting.
        
        Refer to Keysight Programmer's guide, chapter 39, :waveform:format, for valid formats:
        https://www.keysight.com/us/en/assets/9018-07141/programming-guides/9018-07141.pdf
    points : int, optional
        The number of points to acquire. The default is None, which will use the
        scope's current point setting. Note that this does not change the time-resolution 
        of the acquisition, so a smaller number of points will simply result in a shorter waveform.
    timeout : int, optional
        The maximum amount of time to wait for an digitization to finish, in ms. The default is 60000.

    """
    if chan:
        scope.write('waveform:source chan' + str(chan))

    if form:
        scope.write('waveform:format ' + form)
        
    if points:
        scope.write('acquire:points ' + str(points))
        
    schan = scope.query('waveform:source?').rstrip()
    sform = scope.query('waveform:format?').rstrip()
    spoints = scope.query('acquire:points?').rstrip()
    
    print(f'Digitizing {schan}, {sform}')
    print('Attempting to collect ' + spoints + ' points...')
    
    try:
        _ = scope.timeout
        scope.timeout = timeout
        scope.query(f'dig {schan};*opc?')
        scope.timeout = _
        
        print('Acq done. Begin transfer')
        
        if sform == 'ASC':
            values = scope.query_ascii_values('waveform:data?', 
                                              container=np.array)[:-1]
        else:
            values = scope.query_binary_values('waveform:data?',
                                               datatype='h',
                                               container=np.array)
    
        print(f'Acquired {len(values)} points')
        return values
    except Exception:
        print(f'TIMEOUT: The acquisition took longer than {timeout}ms.')
        scope.clear()

scope.write('acquire:average 1') # enables average
scope.write('acquire:count 4096') # how many acquisitions to average
scope.write('acquire:complete 100') # this should be kept at 100 unless you have good reason to change it; see README
scope.write('acquire:mode ETIM') # equivalent time mode; see programmer's guide, chapter 11 /251
scope.write('waveform:source chan3')
scope.write('waveform:format asc') # see programmer's guide, chapter 39 / 1614


acqs = 100
for i in range(acqs):
    v = acq_wav()
    with open(f'data_blocked/trace_chan3_ASC_avg10000_{i}.npy', 'wb') as f:
        np.save(f, v)

