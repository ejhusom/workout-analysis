#!/usr/bin/env python
# -*- coding: utf-8 -*-
#==========================================================================
# Program by Erik Johannes B. L. G. Husom on 2018-12-22 for Python 3.6.4
# Description: Class for analyzing workouts
#
# Accepted file formats:
# - .json
#
# Plot options:
# - Plot only GPS track with matplotlib or bokeh
# - Plot heart rate, speed, elevation and GPS in individual plots with
#   matplotlib or bokeh
# - Plot heart rate, speed and elevation (in same plot) and GPS with bokeh
#
# USAGE:
# $ python3 TrainingAnalyzer.py [filename]
# Currently no way of choosing plot without changing the function called at
# the bottom of this file manually.
#==========================================================================

# IMPORT STATEMENTS
import numpy as np
import sys, os, time, io, json, pprint, csv
import matplotlib.pyplot as plt
from matplotlib.gridspec import GridSpec
from bokeh.plotting import figure
from bokeh.io import output_file, show
from bokeh.models import HoverTool, Range1d, LinearAxis, BoxAnnotation, CustomJS, ColumnDataSource, Text, Circle, ColorBar
from bokeh.layouts import column, row
from bokeh.tile_providers import CARTODBPOSITRON
from bokeh.transform import linear_cmap
from bokeh.palettes import Spectral6
# import fitparse

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
            self.mercatorCoordinates = self.convert_to_mercator_coordinates(self.latitude, self.longitude)
#        elif (fileExtension=='.fit'):
#            ################################################
#            # TODO: Add support for .fit
#            fitfile = fitparse.FitFile(workoutFile, data_processor=fitparse.StandardUnitsDataProcessor())
#            for record in fitfile.get_messages('record'):
#
#                # Go through all the data entries in this record
#                for record_data in record:
#
#                    # Print the records name and value (and units if it has any)
#                    if record_data.units:
#                        print(" * %s: %s %s" % (
#                            record_data.name, record_data.value, record_data.units,
#                        ))
#                    else:
#                        print(" * %s: %s" % (record_data.name, record_data.value))
#                print()
#
#            #################################################

        else:
            print("Wring file format. Only .json supported")
            sys.exit(1)

    def map_plot_mpl(self):
        """Plots GPS track with matplotlib."""
        # TODO: Add background map layer for GPS plot.

        fig = plt.figure(figsize=(12,12))
        ax = fig.add_subplot(111)
        ax.set_aspect(1.8)
        plt.axis('off')
        fig.patch.set_facecolor('black')

        # Plotting GPS track with elevation as colorbar:
        plt.scatter(self.longitude,self.latitude,c=self.elevation)

        plt.show()

    def map_plot_bokeh(self):
        """Plots GPS track with bokeh, generating a html-file."""

        output_file("gps_track.html", title="GPS track visualization")
        source = ColumnDataSource({'seconds' : self.seconds, 'minutes' : self.minutes, 'heartrate' : self.heartrate, 'speed' : self.kph, 'elevation' : self.elevation, 'xCoordinates' : self.mercatorCoordinates[0], 'yCoordinates' : self.mercatorCoordinates[1]})


        # mapper = linear_cmap(field_name='heartrate', palette=Spectral6, low=0, high=1000)#, low=min(self.elevation), high=max(self.elevation))


        # Adding map plot
        mapPlot = figure(x_range=(np.min(self.mercatorCoordinates[0])-600, np.max(self.mercatorCoordinates[0])+600), y_range=(np.min(self.mercatorCoordinates[1])-600, np.max(self.mercatorCoordinates[1])+600), x_axis_type="mercator", y_axis_type="mercator")
        mapPlot.add_tile(CARTODBPOSITRON)
        mapLine = mapPlot.line(x = 'xCoordinates', y = 'yCoordinates', source=source)#, line_color=mapper, color=mapper)
        mapPlot.axis.visible = False

        show(mapPlot)

    def workout_plot_mpl(self):
        """Plot heart rate, speed, elevation and GPS track with matplotlib."""
        # FIXME: GPS plot has wrong axes ratio.
        # TODO: Add background map layer for GPS plot.

        plt.style.use('seaborn')
        plt.rcParams.update({'font.size': 15})
        plt.rc('xtick', labelsize=15)
        plt.rc('ytick', labelsize=15)

        plt.figure(figsize=(25,15))

        gs1 = GridSpec(3,2)

        ax1 = plt.subplot(gs1[0,0])
        plt.plot(self.minutes,self.heartrate, 'r-')
        plt.ylabel('bpm')

        plt.subplot(gs1[1,0], sharex=ax1)
        plt.plot(self.minutes,self.kph, 'b-')
        plt.ylabel('kph')

        plt.subplot(gs1[2,0], sharex=ax1)
        plt.plot(self.minutes,self.elevation, 'g-')
        plt.ylabel('elevation [m]')

        plt.subplot(gs1[:,1])
        plt.plot(self.longitude, self.latitude)
        plt.axis('equal')

        plt.show()

    def workout_singleplot_bokeh(self):

        output_file("workoutData.html")
        plotwidth = 800
        plotheight = 400
        hover = HoverTool(tooltips=[("", "@y")], mode="vline", point_policy="snap_to_data")

        plotHR = figure(title="heartrate", x_axis_label='time [minutes]', y_axis_label='heart rate [bpm]', plot_width=plotwidth, plot_height=plotheight, toolbar_location="below")
        plotHR.add_tools(hover)
        plotHR.line(self.minutes, self.heartrate, color="red")

        plotSpeed = figure(title="speed", x_axis_label='time [minutes]', y_axis_label='speed [kph]', plot_width=plotwidth, plot_height=plotheight, x_range=plotHR.x_range, toolbar_location="below")
        plotSpeed.add_tools(hover)
        plotSpeed.line(self.minutes, self.kph, color='blue')

        plotElevation = figure(title="elevation", x_axis_label='time [minutes]', y_axis_label='elevation [m]', plot_width=plotwidth, plot_height=plotheight, x_range=plotHR.x_range, toolbar_location="below")
        plotElevation.add_tools(hover)
        plotElevation.line(self.minutes, self.elevation, color='green')

        plotMap = figure(x_range=(np.min(self.mercatorCoordinates[0])-600, np.max(self.mercatorCoordinates[0])+600), y_range=(np.min(self.mercatorCoordinates[1])-600, np.max(self.mercatorCoordinates[1])+600), x_axis_type="mercator", y_axis_type="mercator")
        plotMap.add_tile(CARTODBPOSITRON)
        plotMap.line(x = self.mercatorCoordinates[0], y = self.mercatorCoordinates[1])

        show(column(plotHR, plotSpeed, plotElevation, plotMap))

    def workout_multiplot_bokeh(self):


        output_file("workoutData.html")
        plotheight = 400
        plotwidth = 900
        source = ColumnDataSource({'seconds' : self.seconds, 'minutes' : self.minutes, 'heartrate' : self.heartrate, 'speed' : self.kph, 'elevation' : self.elevation, 'xCoordinates' : self.mercatorCoordinates[0], 'yCoordinates' : self.mercatorCoordinates[1]})
        multiplot = figure(title="Workout", x_axis_label='time [minutes]', plot_width=plotwidth, plot_height=plotheight, toolbar_location="below")

        source1 = ColumnDataSource({'hiddenX' : [], 'hiddenY' : []})

        # Adding hover tool
        multihover = HoverTool(tooltips=[("", "@y")], mode="vline", point_policy="snap_to_data")

        # Adding shades of HR zones in plot
        HRzoneLimits = [133,152,161,171]
        HRzone1 = BoxAnnotation(top=HRzoneLimits[0], fill_alpha=0.1, fill_color='darkgreen')
        HRzone2 = BoxAnnotation(bottom=HRzoneLimits[0], top=HRzoneLimits[1], fill_alpha=0.1, fill_color='lawngreen')
        HRzone3 = BoxAnnotation(bottom=HRzoneLimits[1], top=HRzoneLimits[2], fill_alpha=0.1, fill_color='yellow')
        HRzone4 = BoxAnnotation(bottom=HRzoneLimits[2], top=HRzoneLimits[3], fill_alpha=0.1, fill_color='orange')
        HRzone5 = BoxAnnotation(bottom=HRzoneLimits[3], fill_alpha=0.1, fill_color='red')
        multiplot.add_layout(HRzone1)
        multiplot.add_layout(HRzone2)
        multiplot.add_layout(HRzone3)
        multiplot.add_layout(HRzone4)
        multiplot.add_layout(HRzone5)

        # Adding lines
        multiplot.yaxis.axis_label = 'Heartrate [bpm]'
        multiplot.y_range = Range1d(start=np.min(self.heartrate)-10, end=np.max(self.heartrate)+10)
        multiplot.extra_y_ranges['kph'] = Range1d(start=0, end=np.max(self.kph)+2)
        multiplot.add_layout(LinearAxis(y_range_name='kph', axis_label='Speed [kph]'), 'left')
        multiplot.extra_y_ranges['elevation'] = Range1d(start=np.min(self.elevation)-10, end=np.max(self.elevation)+10)
        multiplot.add_layout(LinearAxis(y_range_name='elevation', axis_label='Elevation [m]'), 'right')
        multiplot.add_tools(multihover)
        multiplot.line(self.minutes, self.heartrate, legend="HR", color="red")
        multiplot.line(self.minutes, self.kph, legend="Speed", y_range_name="kph", color="blue")
        multiplot.line(self.minutes, self.elevation, legend="Elevation", y_range_name="elevation", color="green")
        # multiplot.line(x='minutes', y='heartrate', source=source, legend="Heartrate", color="red")
        # multiplot.line('minutes', 'speed', source=source, legend="Speed", y_range_name="kph", color="blue")
        # multiplot.line('minutes', 'elevation', source=source, legend="Elevation", y_range_name="elevation", color="green")
        multiplot.legend.click_policy="hide"

        # Adding map plot
        mapPlot = figure(x_range=(np.min(self.mercatorCoordinates[0])-600, np.max(self.mercatorCoordinates[0])+600), y_range=(np.min(self.mercatorCoordinates[1])-600, np.max(self.mercatorCoordinates[1])+600), x_axis_type="mercator", y_axis_type="mercator")
        mapPlot.add_tile(CARTODBPOSITRON)
        mapLine = mapPlot.line(x = 'xCoordinates', y = 'yCoordinates', source=source)
        # mapCircles = mapPlot.circle('hiddenX', 'hiddenY', size=5, source=source1)
        #
        # code = """
        # var data = {'hiddenX' : [], 'hiddenY' : []};
        # var ldata = line.data;
        # var indeces = cb_data.index['1d'].indeces;
        #
        # for (var i = 0; i < indices.length; i++) {
        #     var ind0 = indices[i]
        #     data['hiddenX'].push(ldata.x[ind0]);
        #     data['hiddenY'].push(ldata.y[ind0]);
        # }
        #
        # circle.data = data;
        # """
        # callback = CustomJS(args={'line': mapLine.data_source, 'circle': mapCircles.data_source}, code=code)
        # mapHover = HoverTool(tooltips=[("time", "@minutes")], callback=callback, renderers=[mapCircles])
        # multihover = HoverTool(tooltips=[("", "@y")], mode="vline", point_policy="snap_to_data", callback=callback)
        # mapPlot.add_tools(mapHover)
        # multiplot.add_tools(multihover)


        show(row(multiplot, mapPlot))

    def convert_to_mercator_coordinates(self, lat, lon):
        """Converts coordinates to Mercator projection."""

        r_major = 6378137.000
        x = r_major * np.radians(lon)
        scale = x/lon
        y = 180.0/np.pi * np.log(np.tan(np.pi/4.0 + lat * (np.pi/180.0)/2.0)) * scale
        return (x, y)


if __name__ == '__main__':
    try:
        workoutFile = sys.argv[1]
    except IndexError:
        print('Give name of workout file as command line argument.')
        sys.exit(1)

    workout = TrainingAnalyzer(workoutFile)

    # TODO: Make it possible to choose plot from command line.
    #workout.map_plot_mpl()
    #workout.map_plot_bokeh()
    #workout.workout_plot_mpl()
    #workout.workout_singleplot_bokeh()
    workout.workout_multiplot_bokeh()
