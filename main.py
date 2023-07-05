import numpy as np
import pandas as pd

datafile = 'data.csv'
f = 80e6 # Hz
collection_time = 1000e-9 # seconds



# data = np.loadtxt(datafile, dtype=str, delimiter=',', skiprows=2)
# print(data)

# use pandas to read csv file, reading the 4th and 5th columns, skip the first 2 rows
data = pd.read_csv(datafile, usecols=[3, 4], skiprows=1)
num_pulses = int(f * collection_time)
group_length = len(data) // num_pulses

data['GroupNumber'] = np.repeat(range(num_pulses), group_length)
grouped = data.groupby('GroupNumber')
max_values = grouped['3 (VOLT)'].max()

print(max_values)