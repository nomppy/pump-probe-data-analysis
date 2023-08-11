# -*- coding: utf-8 -*-
"""
Created on Wed Jul 19 13:09:16 2023

@author: Kenneth Sun
"""

import glob
import numpy as np
import matplotlib.pyplot as plt

npy_files = glob.glob('data_1/*.npy') # change this to the directory where the data is stored
averages = len(npy_files)

# may need to change type casting
cum = np.load(npy_files[0]).astype(int, casting='safe')

for f in npy_files[1:averages-1]:
    cum = cum + np.load(f).astype(int, casting='safe')

avg = cum / averages
plt.plot(cum, '-o')

