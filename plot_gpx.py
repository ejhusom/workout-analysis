#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""One-liner describing module.

Author:
    Erik Johannes Husom

Created:
    2021

"""
import sys

import gpxpy
import matplotlib.pyplot as plt
import mplleaflet
import pandas as pd

def plot_gpx(filepath):
    # Load your GPX file
    with open(filepath, 'r') as gpx_file:
        gpx = gpxpy.parse(gpx_file)

    # Initialize lists to store data
    latitudes = []
    longitudes = []
    times = []
    speeds = []

    # Extract data from GPX file
    for track in gpx.tracks:
        for segment in track.segments:
            for point in segment.points:
                latitudes.append(point.latitude)
                longitudes.append(point.longitude)
                times.append(point.time)

                if len(times) > 1:
                    # Calculate speed
                    delta_time = (times[-1] - times[-2]).total_seconds()
                    distance = point.distance_2d(segment.points[-2])
                    speed = distance / delta_time * 3.6  # Convert m/s to km/h
                    speeds.append(speed)

    # Plotting the map
    plt.figure(figsize=(10, 6))
    plt.plot(longitudes, latitudes, 'b-', alpha=0.7)
    mplleaflet.show()

    # Create a Pandas DataFrame for speed over time
    df = pd.DataFrame({'Time': times[1:], 'Speed': speeds})
    df.set_index('Time', inplace=True)
    # df.index = df.index.dt.tz_localize(None)


    print(df)
    print(df.info())

    # Plotting the speed over time
    plt.figure(figsize=(10, 6))
    plt.plot(df.index, df['Speed'], 'r-')
    plt.xlabel('Time')
    plt.ylabel('Speed (km/h)')
    plt.title('Speed Over Time')
    plt.show()



if __name__ == '__main__':
    filepath = sys.argv[1]

    plot_gpx(filepath)
