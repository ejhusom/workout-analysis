#!/usr/bin/env python
# -*- coding: utf-8 -*-
#==========================================================================
# Program by Erik Johannes B. L. G. Husom on 2018-01-14 for Python 3.6.4
# Description: Calculating elevation gain on a treadmill
# USAGE:
#==========================================================================
# IMPORT STATEMENTS
import sys
import numpy as np

def elevationGain(incline, distance):
    """Calculates elevation gain on a treadmill"""
    incline = incline/100
    elevationGain = distance*np.cos(np.arctan(incline))*incline
    return elevationGain*1000

def elevationGainRiseOverRun(incline, distance):
    incline = incline/100
    elevationGain = distance*incline
    print(elevationGain*1000)

def elevationGainTime(incline, speed, time_in_min):
    time_in_h = time_in_min / 60.0
    distance = speed*time_in_h

incline = float(input("Incline (percentage)="))
distance = float(input("Distance (km)="))
#speed = float(input("Speed (km/h)="))
time = float(input("Time (min)="))

gain = elevationGain(incline, distance)
#time = distance/speed
time /= 60
speed = distance/time
print("Elevation gain: ", gain)
print("Speed: ", speed)
print("Vertical speed (m/min): ", gain/(time*60))
print("Vertical speed (m/hr): ", gain/time)
