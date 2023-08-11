# -*- coding: utf-8 -*-
"""
Created on Mon Jul 10 12:10:55 2023

@author: Kenneth Sun
"""

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import pyvisa # https://pyvisa.readthedocs.io/en/latest/
import time

# connect to oscilloscope
# in most cases this will work without any changes
# if not, locate the correct resource name and replace line 8
# if the connection is successful, the oscilloscope will respond with its ID

rm = pyvisa.ResourceManager()
print(rm.list_resources())
scope.query('acquire:mode?')
scope = rm.open_resource(rm.list_resources()[-1])
print(scope.query('*IDN?'))

def acq_wav (chan=None, form=None, points=None):

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
        scope.query(f'dig {schan};*opc?')
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
        print(f'TIMEOUT: The acquisition took longer than {scope.timeout}ms.')
        scope.clear()
#%%
blist = []
for i in range(20):
    blist.append(acq_wav(chan=3, form='WORD'))
    
def smooth_array(array, window_size):
    window = np.ones(window_size) / window_size
    smoothed = np.convolve(array, window, mode='same')
    return smoothed

scope.write('*RST')
scope.write('acquire:points 20000')
scope.write('acquire:mode HRESolution')
scope.write('acquire:complete 100')
scope.write('acquire:count 10000')
scope.write('acquire:average 1')
scope.write('acquire:bandwidth 1e9')
scope.write('acq:bandwidth auto')
scope.timeout = 600000

plt.plot(smooth_array(acq_wav(chan=3), 1), '-o')
plt.plot(acq_wav(chan=3, form='ASC'), '-o')

scope.write('dig chan3')

plt.plot(values[:4000],'-o')

scope.write('single')

scope.write('waveform:source chan3')
scope.query('waveform:points?')

scope.write('waveform:format word')
pyvisa.log_to_screen()
bvalues = scope.query_binary_values('waveform:data?',
                                   datatype='h',
                                   container=np.ndarray)
values = scope.read_raw()

values = scope.query_ascii_values('waveform:data?', container=np.array)[:-1]

scope.write('waveform:format ascii')
v = np.asarray([ float(i) for i in scope.query('waveform:data?').split(',')[:-1]])
plt.plot(values)

df = pd.DataFrame(values)
print(df.describe())

scope.write('run')
scope.write('stop')

scope.write('blank chan1')
scope.write('view chan3')
scope.write('acquire:average 0')
scope.write('acquire:points auto')

scope.query('acquire:points?')
scope.query('acquire:mode?')
scope.write('acquire:mode etim')
scope.query('waveform:source?')
scope.query('waveform:format?')
scope.query('waveform:type?')
scope.query('waveform:points?')
scope.query('waveform:count?')
scope.query('waveform:view?')

scope.query('measure:vmax?')
scope.query('measure:vmin?')
scope.query('measure:freq?')
