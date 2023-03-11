# To fixing the Keyboard Interrupt error due to importing scipy
# Previously, when activate KeyboardInterrupt, would crash the program instead of going to the Keyboard Interrupt of the try/except statement
import os
os.environ['FOR_DISABLE_CONSOLE_CTRL_HANDLER'] = '1'

import pyvisa as visa
import time
from ThorlabsPM100 import ThorlabsPM100
import numpy as np
import matplotlib.pyplot as plt
import math
import sys
import csv
import pyvisa as visa
from ThorlabsPM100 import ThorlabsPM100
import matplotlib.pyplot as plt
import time
import math
from scipy.optimize import curve_fit

try:
    from Thorlabs_MDT69XB_PythonSDK.MDT_COMMAND_LIB import *
except OSError as ex:
    print("Warning:",ex)

# Reads the power from the power meter
# Returns: Current power measurement, array of total power
def read_power_fiber(fiberOut):
    
    powerObj = ThorlabsPM100(inst=fiberOut)
    total_power = []
    total_power.append(powerObj.read)
    return powerObj.read

def read_power_beam(beamOut):
    powerObj = ThorlabsPM100(inst=beamOut)
    total_power = []
    total_power.append(powerObj.read)
    return powerObj.read

def read_power_eff(fiberOut, beamOut):
    # Returns the coupling efficiency
    counter = 0
    while (True):
        
        time.sleep(1)
        power = []
        time_arr = []
        cur_power = (read_power_fiber(fiberOut)/ read_power_beam(beamOut)) * (0.282/0.311)
        print(cur_power)
        power.append(cur_power)

        print("==================================================================")
        
rm = visa.ResourceManager()
fiberOut = rm.open_resource('USB::0x1313::0x8078::P0026663::INSTR')
print("Finished creater resrouce manager 1")
beamOut = rm.open_resource('USB0::4883::32888::P0025560::INSTR')
print("Finished creater resrouce manager 2")

read_power_eff(fiberOut, beamOut)
# First try just calling read power eff, then include the main with the while loop (maybe it's the time on the sleep function)
# Seems to not work on Anaconda Powershell, but works on Anacondazc