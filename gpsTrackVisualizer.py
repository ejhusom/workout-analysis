#!/usr/bin/env python
# -*- coding: utf-8 -*-
#==========================================================================
# Program by Erik Johannes B. L. G. Husom on 2018-02-09 for Python 3.6.4
# Description: Class for beautiful visualization of GPS tracks.
# USAGE:
#==========================================================================
# IMPORT STATEMENTS
import numpy as np
import sys, os, time, io, json, fitparse, pprint, csv
import matplotlib.pyplot as plt
from matplotlib.gridspec import GridSpec
from bokeh.plotting import figure
from bokeh.io import output_file, show
from bokeh.models import HoverTool, Range1d, LinearAxis, BoxAnnotation, CustomJS, ColumnDataSource, Text, Circle, ColorBar
from bokeh.layouts import column, row
from bokeh.tile_providers import CARTODBPOSITRON
from bokeh.transform import linear_cmap
from bokeh.palettes import Spectral6

class TrainingAnalyzer(object):
    def __init__(self, workoutFile):
        self.workoutFile = workoutFile
        filename, fileExtension = os.path.splitext(self.workoutFile)
        # Read json-file
        if (fileExtension=='.json'):
            data = json.load(io.open(workoutFile, 'r', encoding='utf-8-sig'))
            # Read data samples
            numberOfSamples = len(data["RIDE"]["SAMPLES"])
            seconds = []
            heartrate = []
            kph = []
            elevation = []
            latitude = []
            longitude = []
            for i in range(numberOfSamples):
                seconds.append(data["RIDE"]["SAMPLES"][i]["SECS"])
                heartrate.append(data["RIDE"]["SAMPLES"][i]["HR"])
                kph.append(data["RIDE"]["SAMPLES"][i]["KPH"])
                elevation.append(data["RIDE"]["SAMPLES"][i]["ALT"])
                latitude.append(data["RIDE"]["SAMPLES"][i]["LAT"])
                longitude.append(data["RIDE"]["SAMPLES"][i]["LON"])
            # Converting to arrays
            self.seconds = np.array(seconds)
            self.minutes = np.array(seconds)/60
            self.heartrate = np.array(heartrate)
            self.heartrate = self.heartrate.astype(int)
            self.kph = np.array(kph)
            self.elevation = np.array(elevation)
            self.latitude = np.array(latitude)
            self.longitude = np.array(longitude)
            self.mercatorCoordinates = self.getMercatorCoordinates(self.latitude, self.longitude)
        else:
            print("Wrong file format")


    def plotWithMPL(self):
#        plt.style.use('seaborn')
#        plt.rcParams.update({'font.size': 15})
#        plt.rc('xtick', labelsize=15)
#        plt.rc('ytick', labelsize=15)

        # PLOT APPEARANCE
#        fig = plt.figure(figsize=(12,14)) # has to be manually set for now
        fig = plt.figure(figsize=(12,12))
        ax = fig.add_subplot(111)
        ax.set_aspect(1.8)
#        plt.axis('equal')
        plt.axis('off')             # removing everything except plot line
#        fig.patch.set_facecolor('black')
#        plt.plot(self.longitude,self.latitude)
        plt.scatter(self.longitude,self.latitude,c=self.elevation)
        

        plt.show()

    def multiplotWithBokeh(self):


        output_file("gpsVisualization.html", title="GPS track visualization")
        source = ColumnDataSource({'seconds' : self.seconds, 'minutes' : self.minutes, 'heartrate' : self.heartrate, 'speed' : self.kph, 'elevation' : self.elevation, 'xCoordinates' : self.mercatorCoordinates[0], 'yCoordinates' : self.mercatorCoordinates[1]})


#        mapper = linear_cmap(field_name='heartrate', palette=Spectral6, low=0, high=1000)#, low=min(self.elevation), high=max(self.elevation))


        # Adding map plot
        mapPlot = figure(x_range=(np.min(self.mercatorCoordinates[0])-600, np.max(self.mercatorCoordinates[0])+600), y_range=(np.min(self.mercatorCoordinates[1])-600, np.max(self.mercatorCoordinates[1])+600), x_axis_type="mercator", y_axis_type="mercator")
        mapPlot.add_tile(CARTODBPOSITRON)
        mapLine = mapPlot.line(x = 'xCoordinates', y = 'yCoordinates', source=source)#, line_color=mapper, color=mapper)
    

        mapPlot.axis.visible = False

        show(mapPlot)


    def getMercatorCoordinates(self, lat, lon):
        r_major = 6378137.000
        x = r_major * np.radians(lon)
        scale = x/lon
        y = 180.0/np.pi * np.log(np.tan(np.pi/4.0 + lat * (np.pi/180.0)/2.0)) * scale
        return (x, y)


if __name__ == '__main__':
    workoutFile = sys.argv[1]

    workout = TrainingAnalyzer(workoutFile)
    #workout.plotWithMPL()
    workout.multiplotWithBokeh()
