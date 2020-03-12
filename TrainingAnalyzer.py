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
from bokeh.models import HoverTool, Range1d, LinearAxis, BoxAnnotation, CustomJS, ColumnDataSource, Text, Circle, ColorBar, Slider
from bokeh.layouts import column, row
from bokeh.embed import components
from bokeh.tile_providers import get_provider, Vendors
from bokeh.transform import linear_cmap
from bokeh.palettes import Spectral6
from xml.dom import minidom
# import mplleaflet
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
            self.kph = np.array(kph)
            self.heartrate = np.array(heartrate, dtype=int)
            # self.heartrate = self.heartrate.astype(int)

        elif (fileExtension == ".gpx"):
            # data = open(workoutFile)
            with open(workoutFile, "r") as f:
                data = f
                xmldoc = minidom.parse(data)

            track = xmldoc.getElementsByTagName('trkpt')
            elevation_xml = xmldoc.getElementsByTagName('ele')
            datetime_xml = xmldoc.getElementsByTagName('time')
            sample_count = len(track)

            longitude = []
            latitude = []
            elevation = []
            seconds = []
            for s in range(sample_count):
                lon, lat = track[s].attributes['lon'].value,track[s].attributes['lat'].value
                elev = elevation_xml[s].firstChild.nodeValue
                longitude.append(float(lon))
                latitude.append(float(lat))
                elevation.append(float(elev))
                # PARSING TIME ELEMENT
                dt = datetime_xml[s].firstChild.nodeValue
                time_split = dt.split('T')
                hms_split = time_split[1].split(':')
                time_hour = int(hms_split[0])
                time_minute = int(hms_split[1])
                time_second = int(hms_split[2].split('Z')[0])
                total_second = time_hour*3600+time_minute*60+time_second
                seconds.append(total_second)

            self.heartrate = None
            self.kph = None
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


        self.seconds = np.array(seconds)
        self.minutes = np.array(seconds)/60
        self.elevation = np.array(elevation)
        self.latitude = np.array(latitude)
        self.longitude = np.array(longitude)
        self.mercatorCoordinates = self.convert_to_mercator_coordinates(self.latitude, self.longitude)

    def plot_map_mpl(self):
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
        # plotMap.add_tile(CARTODBPOSITRON)
        plotMap.add_tile(get_provider(Vendors.CARTODBPOSITRON))
        plotMap.line(x = self.mercatorCoordinates[0], y = self.mercatorCoordinates[1])

        show(column(plotHR, plotSpeed, plotElevation, plotMap))


    def create_plot(self, backend="bokeh"):

        output_file("workout_plot.html")
        self.plotheight = 400
        self.plotwidth = 600
        self.source = ColumnDataSource({
            'seconds' : self.seconds, 
            'minutes' : self.minutes, 
            'elevation' : self.elevation, 
            'xCoordinates' : self.mercatorCoordinates[0], 
            'yCoordinates' : self.mercatorCoordinates[1]
        })

        if self.kph is not None:
            self.source.add(self.kph, 'kph')
        if self.heartrate is not None:
            self.source.add(self.heartrate, 'heartrate')

        self.workout_plot = figure(
                title="Workout", 
                x_axis_label='time [minutes]',
                plot_width=self.plotwidth, 
                plot_height=self.plotheight, 
                # toolbar_location="below"
        )

        self.workout_plot.yaxis.visible = False


        if self.heartrate is not None:
            self.plot_heartrate()
        if self.kph is not None:
            self.plot_speed()
        self.plot_elevation()
        self.plot_map_bokeh()

        multihover = HoverTool(tooltips=[("", "@y")], mode="vline", point_policy="snap_to_data")
        self.workout_plot.add_tools(multihover)
        self.workout_plot.legend.click_policy="hide"

        workout_script, workout_div = components(self.workout_plot)
        map_script, map_div = components(self.mapPlot)
        with open("map_components.txt", "w") as f:
            f.write(map_div)
            f.write(map_script)

        # show(column(self.workout_plot, self.mapPlot))


    def add_heartrate_zones(self):

        hr_zones = [
                [0, "darkgreen", None],
                [133, "lawngreen", None],
                [152, "yellow", None],
                [161, "orange", None],
                [171, "red", None],
                [220, "white", None],
        ]

        self.workout_plot.yaxis.axis_label = 'Heartrate [bpm]'
        self.workout_plot.y_range = Range1d(
                start=np.min(self.heartrate)-10,
                end=np.max(self.heartrate)+10
        )

        for i in range(len(hr_zones)-1):
            layout = BoxAnnotation(
                    bottom = hr_zones[i][0], 
                    top = hr_zones[i+1][0], 
                    fill_alpha = 0.1, 
                    fill_color = hr_zones[i][1]
            )
            self.workout_plot.add_layout(layout)

    
    def plot_heartrate(self):

        self.add_heartrate_zones()
        # multiplot.yaxis.axis_label = 'Heartrate [bpm]'
        # self.workout_plot.y_range = Range1d(start=np.min(self.heartrate)-10,
        #         end=np.max(self.heartrate)+10)
        self.workout_plot.extra_y_ranges['heartrate'] = Range1d(
                start=np.min(self.heartrate)-10, end=np.max(self.heartrate)+10)
        self.workout_plot.add_layout(LinearAxis(y_range_name='heartrate',
            axis_label='Heart rate [bpm]'), 'left')
        self.workout_plot.line(self.minutes, self.heartrate, legend_label="HR",
                y_range_name="heartrate", color="red")

    def plot_speed(self):

        self.workout_plot.extra_y_ranges['kph'] = Range1d(start=0, end=np.max(self.kph)+2)
        self.workout_plot.add_layout(LinearAxis(y_range_name='kph', axis_label='Speed [kph]'), 'left')
        self.workout_plot.line(self.minutes, self.kph, legend_label="Speed", y_range_name="kph", color="blue")

    def plot_elevation(self):

        self.workout_plot.extra_y_ranges['elevation'] = Range1d(
                start=np.min(self.elevation)-10, 
                end=np.max(self.elevation)+10
        )
        self.workout_plot.add_layout(LinearAxis(
            y_range_name='elevation', axis_label='Elevation [m]'), 'right'
        )
        self.workout_plot.line(self.minutes, self.elevation, 
                legend_label="Elevation", y_range_name="elevation", color="green"
        )


    def plot_map_bokeh(self, map_style="terrain"):
        # Adding map plot
        self.mapPlot = figure(
                x_range=(np.min(self.mercatorCoordinates[0])-600, 
                    np.max(self.mercatorCoordinates[0])+600), 
                y_range=(np.min(self.mercatorCoordinates[1])-600, 
                    np.max(self.mercatorCoordinates[1])+600), 
                x_axis_type="mercator", 
                y_axis_type="mercator",
                plot_width=self.plotwidth, 
                plot_height=self.plotheight, 
        )

        if map_style == "terrain":
            self.mapPlot.add_tile(get_provider(Vendors.STAMEN_TERRAIN))
        elif map_style == "normal":
            self.mapPlot.add_tile(get_provider(Vendors.CARTODBPOSITRON))
        else:
            print("map_style must be either 'terrain' or 'normal'.")

        mapLine = self.mapPlot.line(
                x = 'xCoordinates', 
                y = 'yCoordinates', 
                source=self.source
        )

        # source1 = ColumnDataSource({'hiddenX' : [], 'hiddenY' : []})
        # mapCircles = self.mapPlot.circle('hiddenX', 'hiddenY', size=5, source=source1)
        
        # code = """
        # var data = {'hiddenX' : [], 'hiddenY' : []};
        # var ldata = line.data;
        # var indeces = cb_data.index['1d'].indeces;
        
        # for (var i = 0; i < indices.length; i++) {
        #     var ind0 = indices[i]
        #     data['hiddenX'].push(ldata.x[ind0]);
        #     data['hiddenY'].push(ldata.y[ind0]);
        # }
        
        # circle.data = data;
        # """
        # callback = CustomJS(args={'line': mapLine.data_source, 'circle': mapCircles.data_source}, code=code)
        # mapHover = HoverTool(tooltips=[("time", "@minutes")], callback=callback, renderers=[mapCircles])
        mapHover = HoverTool(tooltips=[("time", "@minutes")],
            point_policy="snap_to_data")
        # multihover = HoverTool(tooltips=[("", "@y")], mode="vline", point_policy="snap_to_data", callback=callback)
        self.mapPlot.add_tools(mapHover)
        # self.workout_plot.add_tools(multihover)

        return self.mapPlot



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
    # workout.plot_map_mpl()
    # workout.workout_plot_mpl()
    # workout.workout_singleplot_bokeh()
    # workout.workout_multiplot_bokeh()
    workout.create_plot()
