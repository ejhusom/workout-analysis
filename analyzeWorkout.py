#!/usr/bin/env python
# -*- coding: utf-8 -*-
#==========================================================================
# Program by Erik Johannes B. L. G. Husom on 2018-12-17 for Python 3.6.4
# Description: Script for analyzing one or several workout files
# USAGE:
#==========================================================================
# IMPORT STATEMENTS
import sys, os, time, io
import numpy as np
import pandas as pd
import json
import codecs
from pprint import pprint
import matplotlib.pyplot as plt

import TrainingAnalyzer

# SET PLOT STYLE
plt.style.use('ggplot')
plt.rcParams.update({'font.size': 8})
plt.rc("text", usetex=True)
plt.rc('font', family='serif')
w = 5; h = 2.5

start = time.time()



def readAllWorkouts():
    totalDuration = 0
    SkippedCount = 0
    workoutCount = 0

    for file in os.listdir("/Downloads/"):
        filename = os.fsdecode(file)
        workoutCount += 1



        try:
            # data = json.load(io.open("/Downloads/" + filename, 'r', encoding='utf-8-sig'))
            data = json.load(codecs.open("/Downloads/" + filename, "r", "utf-8-sig"))
            # totalDuration += data["RIDE"]["SAMPLES"][-1]["SECS"]
        except:
            SkippedCount += 1
            print(filename)

    print("Total duration: " + str(totalDuration/60/60))
    print("Number skipped: " + str(SkippedCount))


def readSingleWorkout():
    # Read workout filename from command line
    try:
        workoutFile = sys.argv[1]
    except:
        print("Provide filename of workout file as command line argument!")

    # Read data from workoutfile
    data = json.load(io.open(workoutFile, 'r', encoding='utf-8-sig'))
    # data = json.load(codecs.open(workoutFile, "r", "utf-8-sig"))

    numberOfSamples = len(data["RIDE"]["SAMPLES"])
    seconds = []
    heartrate = []
    kph = []
    elevation = []

    for i in range(numberOfSamples):
        seconds.append(data["RIDE"]["SAMPLES"][i]["SECS"])
        heartrate.append(data["RIDE"]["SAMPLES"][i]["HR"])
        kph.append(data["RIDE"]["SAMPLES"][i]["KPH"])
        elevation.append(data["RIDE"]["SAMPLES"][i]["ALT"])

    minutes = np.array(seconds)/60
    heartrate = np.array(heartrate)
    kph = np.array(kph)

if __name__ == '__main__':
