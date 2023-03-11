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
import datetime
import pandas as pd

try:
    from Thorlabs_MDT69XB_PythonSDK.MDT_COMMAND_LIB import *
except OSError as ex:
    print("Warning:",ex)

# ===================== START OF PIEZOCONTROLLER FUNCTIONS =====================

# Input: HDL of specific controller
# Returns: X Axis Voltage
def get_X_Axis(hdl):
    voltage = [0]
    result = mdtGetXAxisVoltage(hdl, voltage)
    if(result<0):
       print("mdtGetXAxisVoltage fail ", result)
    else:
       print("mdtGetXAxisVoltage ", voltage)
    return voltage [0]

# Input: HDL of specific controller
# Returns: Y Axis Voltage
def get_Y_Axis(hdl) -> int:
    voltage = [0]
    result = mdtGetYAxisVoltage(hdl, voltage)
    if(result<0):
       print("mdtGetYAxisVoltage fail ", result)
    else:
       print("mdtGetYAxisVoltage ", voltage)
    return voltage [0]
    
# Input: HDL of specific controller, value of voltage
# Returns: 1 if success, 0 if fail
def set_X_Axis(hdl, value):
    result = mdtSetXAxisVoltage(hdl, value)
    if(result<0):
       print("mdtSetXAxisVoltage fail ", result)
       return 0
    else:
       print("mdtSetXAxisVoltage ", value)
       return 1

# Input: HDL of specific controller, value of voltage
# Returns: 1 if success, 0 if fail       
def set_Y_Axis(hdl, value):
    result = mdtSetYAxisVoltage(hdl, value)
    if(result<0):
       print("mdtSetYAxisVoltage fail ", result)
       return 0
    else:
       print("mdtSetYAxisVoltage ", value)
       return 1

# Connects MDT Piezo Controllers from serial number input
# Returns: Controller HDL
def connect_controller(serialNumber):
   hdl = mdtOpen(serialNumber,115200,3)
   if(hdl < 0):
       print("Connect ",serialNumber, "fail" )
       return -1;
   else:
       print("Connect ",serialNumber, "successful")
   
   result = mdtIsOpen(serialNumber)
   id = []
   result = mdtGetId(hdl, id)
   if(result<0):
       print("mdtGetId fail ",result)
   else:
       print(id)
   return hdl

def MDT693BControl(serialNumber):
    hdl = connect_controller(serialNumber)
    if (hdl<0):
        return
        
    result = mdtClose(hdl)
    if(result == 0):
        print("mdtClose ", serialNumber)
    else:
        print("mdtClose fail", result)
    result = mdtIsOpen(serialNumber)
    print("mdtIsOpen ",result)

# ===================== END OF PIEZOCONTROLLER FUNCTIONS =====================

# ================================= POWER METER START =================================
def read_power_fiber():
    powerObj = ThorlabsPM100(inst=fiber_out)    
    return powerObj.read

def read_power_beam():
    powerObj = ThorlabsPM100(inst=beam_out)
    print(powerObj.read)
    return powerObj.read

def read_power_eff():
    # Returns the coupling efficiency
    print("beam", read_power_beam())
    return (read_power_fiber()/ read_power_beam()) * (0.286/0.31)

# ================================= POWER METER END =================================

# Global variables for the power meter's resource manager
#rm = visa.ResourceManager()
#fiber_out = rm.open_resource('USB0::4883::32888::P0025560::INSTR', timeout=0)
#beam_out = rm.open_resource('USB0::4883::32888::P0025003::INSTR', timeout=0)
  
time_arr = []
cur_power = []

def no_stabilization(file_name):
    #cur_time = round(time.time(), 3)
    cur_time = (datetime.datetime.fromtimestamp(time.time()).strftime('%c')[11:19])
    cur_power_reading = read_power_eff() * 100
    time_arr.append(cur_time)
    cur_power.append(cur_power_reading)
    write_file(cur_time, cur_power_reading, file_name)
    print(cur_power_reading)            

def stabilization(coarser_hdl, finer_hdl, threshold, file_name):
    #cur_time = round(time.time(), 3)
    cur_time = (datetime.datetime.fromtimestamp(time.time()).strftime('%c')[11:19])
    cur_power_reading = read_power_eff() * 100
    time_arr.append(cur_time)
    cur_power.append(cur_power_reading)
    write_file(cur_time, cur_power_reading, file_name)
    print(cur_power_reading)
    if (read_power_eff() * 100 < threshold):
        newtonsYAxis(coarser_hdl, finer_hdl)
        newtonsXAxis(coarser_hdl, finer_hdl)
        print("Algorithm Activated", read_power_eff() * 100) 

def main():
    try:
        devs = mdtListDevices()
        print(devs)
        if(len(devs)<=0):
           print('There are no devices connected')
           exit()
        coarserSerialNum = devs[0][0]
        finerSerialNum = devs[1][0]
    except Exception as ex:
        print("Warning:", ex)

    
    coarser_hdl = connect_controller(coarserSerialNum)
    finer_hdl = connect_controller(finerSerialNum)

    file_name = '1_26_data.txt'
    

    try:
        while True:
            time.sleep(1.5) # originally 0.5
            current_time = (datetime.datetime.fromtimestamp(time.time()).strftime('%c')[11:19])
            no_stabilization (file_name)
            #stabilization(coarser_hdl, finer_hdl, 71.5, file_name)
            
    except KeyboardInterrupt:
        plt.rcParams['font.size'] = 16
        plt.xlabel("Time")
        plt.ylabel("Coupling %")
        plt.xticks(rotation = 45) # Rotates X-Axis Ticks by 45-degrees
        
        time_arr_new = pd.to_datetime(time_arr)
        plt.title("Coupling percentage vs Time")
        plt.plot(time_arr_new,cur_power ,marker='o',color='blue', linestyle = '--')
        
        plt.show()
        print("mean and std", np.mean(cur_power), np.std(cur_power))
        
    plt.rcParams['font.size'] = 16
    plt.xlabel("Time")
    plt.ylabel("Coupling %")
    plt.xticks(rotation = 45) # Rotates X-Axis Ticks by 45-degrees
    time_arr_new = pd.to_datetime(time_arr)
    plt.title("Coupling percentage vs Time")
    plt.plot(time_arr_new,cur_power ,marker='o',color='blue', linestyle = '--', )
    plt.show()
    

def newtonsYAxis(coarser, finer):
    # Get starting voltage
    startingVoltageFiner = get_Y_Axis(finer)
    startingVoltageCoarser = get_Y_Axis(coarser)

    # Getting starting power
    mid_eff = read_power_eff()
    # Step size
    res = 4

    # Effiency of starting + step
    end_eff = 0
    if (startingVoltageCoarser + res < 149):
        set_Y_Axis (coarser, int(startingVoltageCoarser + res))
        end_eff = read_power_eff()

    # Efficiency of starting - step
    start_eff = 0
    if (startingVoltageCoarser - res > 1):
        set_Y_Axis(coarser, int(startingVoltageCoarser - res))
        start_eff = read_power_eff()

    set_Y_Axis(coarser, startingVoltageCoarser)
    print("Starting eff: ", start_eff, "Middle eff", mid_eff, "Ending eff", end_eff)
    
    movement_amt = res/2 * (end_eff-start_eff)/(end_eff+start_eff-2*mid_eff) # based off of Newtons
    print("Calculated Movement Amount", movement_amt) # For the finer mirror
    if (movement_amt >= 0): # if it's positive value
        movement_amt = min((movement_amt), 1.5 * res)
    else: # if it's negative value
        movement_amt = max(movement_amt, -1.5 * res)

    print("Movement Amount ", movement_amt)

    set_Y_Axis(finer, startingVoltageFiner + movement_amt)

    mid_eff = read_power_eff()
    end_eff = 0
    if (startingVoltageCoarser + res < 149):
        set_Y_Axis (coarser, int(startingVoltageCoarser + res))
        end_eff = read_power_eff()
    start_eff = 0
    if (startingVoltageCoarser - res > 1):
        set_Y_Axis(coarser, int(startingVoltageCoarser - res))
        start_eff = read_power_eff()

    if (max(start_eff, mid_eff, end_eff) == start_eff):
        set_Y_Axis(coarser, int(startingVoltageCoarser - res))
    elif (max(start_eff, mid_eff, end_eff) == mid_eff):
        set_Y_Axis(coarser, startingVoltageCoarser)
    else: # At the end_eff
        set_Y_Axis(coarser, int(startingVoltageCoarser + res))

    ending_power = read_power_eff()
    if (ending_power < mid_eff):
        # Reset back to the current value
        print("Reset to original values")
        set_Y_Axis(coarser, startingVoltageCoarser)
        set_Y_Axis(finer, startingVoltageFiner)

    final_power = read_power_eff()
    print("Initial Eff: ", mid_eff, "Ending Eff", final_power )
    
def newtonsXAxis(coarser, finer):
    # Get starting voltage
    startingVoltageFiner = get_X_Axis(finer)
    startingVoltageCoarser = get_X_Axis(coarser)

    # Getting starting power
    mid_eff = read_power_eff()
    # Step size
    res = 4

    # Effiency of starting + step
    end_eff = 0
    if (startingVoltageCoarser + res < 149):
        set_X_Axis (coarser, int(startingVoltageCoarser + res))
        end_eff = read_power_eff()

    # Efficiency of starting - step
    start_eff = 0
    if (startingVoltageCoarser - res > 1):
        set_X_Axis(coarser, int(startingVoltageCoarser - res))
        start_eff = read_power_eff()

    set_X_Axis(coarser, startingVoltageCoarser)
    print("Starting eff: ", start_eff, "Middle eff", mid_eff, "Ending eff", end_eff)
    
    movement_amt = res/2 * (end_eff-start_eff)/(end_eff+start_eff-2*mid_eff) # based off of Newtons
    print("Calculated Movement Amount", movement_amt) # For the finer mirror
    if (movement_amt >= 0): # if it's positive value
        movement_amt = min((movement_amt), 1.5 * res)
    else: # if it's negative value
        movement_amt = max(movement_amt, -1.5 * res)

    print("Movement Amount ", movement_amt)

    set_X_Axis(finer, startingVoltageFiner + movement_amt)

    mid_eff = read_power_eff()
    end_eff = 0
    if (startingVoltageCoarser + res < 149):
        set_X_Axis (coarser, int(startingVoltageCoarser + res))
        end_eff = read_power_eff()
    start_eff = 0
    if (startingVoltageCoarser - res > 1):
        set_X_Axis(coarser, int(startingVoltageCoarser - res))
        start_eff = read_power_eff()

    if (max(start_eff, mid_eff, end_eff) == start_eff):
        set_X_Axis(coarser, int(startingVoltageCoarser - res))
    elif (max(start_eff, mid_eff, end_eff) == mid_eff):
        set_X_Axis(coarser, startingVoltageCoarser)
    else: # At the end_eff
        set_X_Axis(coarser, int(startingVoltageCoarser + res))

    ending_power = read_power_eff()
    if (ending_power < mid_eff):
        # Reset back to the current value
        print("Reset to original values")
        set_X_Axis(coarser, startingVoltageCoarser)
        set_X_Axis(finer, startingVoltageFiner)

    final_power = read_power_eff()
    print("Initial Eff: ", mid_eff, "Ending Eff", final_power )
    
def plot_hysteresis(coarser, finer):
    voltage_levels_increase = []
    voltage_levels_decrease = []
    coarser_x_increase = []
    coarser_y_decrease = []

    set_Y_Axis(coarser, 75)
    set_X_Axis(finer, 45)
    set_Y_Axis(finer, 75)
    for i in range (0, 151, 5):
        voltage_levels_increase.append(i)
    for i in range (150, -1, -5):
        voltage_levels_decrease.append(i)

    for voltage in voltage_levels_increase:
        set_X_Axis(coarser, voltage)
        power = read_power_fiber()
        coarser_x_increase.append(power)
    
    for voltage in voltage_levels_decrease:
        set_X_Axis(coarser, voltage)
        power = read_power_fiber()
        coarser_y_decrease.append(power)

    plt.plot(voltage_levels_increase, coarser_x_increase, '-ok',color="orange")
    plt.plot(voltage_levels_decrease, coarser_y_decrease, '-ok', color="blue")

    plt.yticks(np.arange(0.00015, 0.0003, 0.00005))

    plt.xlabel("Voltage [V]")
    plt.ylabel("Power [W]")

    set_Y_Axis(coarser, 74.11)
    set_Y_Axis(finer, 64.08)
    set_X_Axis(coarser, 23.09)
    set_X_Axis(finer, 100.61)


    plt.show()

def write_file(time, power, file_name):
    file_object = open(file_name, 'a')
    file_object.write("time:" + str(time))
    file_object.write('\n')
    file_object.write("power:" + str(power))
    file_object.write('\n')

    # Close the file
    file_object.close()
    
        
def read_file():
    power_readings = []
    time_readings = []
    
    with open('1_27_data.txt') as f:
        for line in f.readlines():
            #print("time", (line[5:18]), "power", (line[25:35]))
            if "time" in line:
                time_readings.append((line[5:]))
            if "power" in line: 
                power_readings.append(float(line[6:]))
    
    print("time readings", time_readings)
    print("power readings", power_readings)
    print("Mean and Std", np.mean(power_readings), np.std(power_readings))
    plt.plot(time_readings,power_readings ,color='blue', marker='o', linestyle = '--')

    plt.xlabel("Time")
    plt.ylabel("Coupling Efficiency (Percentage)")
    plt.show()

#main()

#write_file('1_5_2_data.txt')
read_file()
#serialNumber = 150903175407


#mdtGetYAxisVoltage  [74.11]
#mdtGetYAxisVoltage  [64.08]
#mdtGetXAxisVoltage  [23.09]
#mdtGetXAxisVoltage  [100.61]