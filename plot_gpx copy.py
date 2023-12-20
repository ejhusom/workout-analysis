#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import gpxo
import sys
import matplotlib as mpl
import matplotlib.pyplot as plt
import numpy as np
from fit_tool.fit_file import FitFile
from fit_tool.profile.messages.record_message import RecordMessage

def plot_gpxo(filepath):
    track = gpxo.Track(filepath)
    track.map(plot='scatter', c=track.elevation, cmap='plasma')
    track.map(plot='scatter', c=track.elevation, cmap='plasma')
    track.show()

def plot_fit_file(filepath):
    """ Analyze a FIT file
    """

    print(f'Loading activity file...')
    app_fit = FitFile.from_file(filepath)
    timestamp1 = []
    power1 = []
    distance1 = []
    speed1 = []
    cadence1 = []
    for record in app_fit.records:
        message = record.message
        if isinstance(message, RecordMessage):
            timestamp1.append(message.timestamp)
            distance1.append(message.distance)
            power1.append(message.power)
            speed1.append(message.speed)
            cadence1.append(message.cadence)

    start_timestamp = timestamp1[0]
    time1 = np.array(timestamp1)
    power1 = np.array(power1)
    speed1 = np.array(speed1)
    cadence1 = np.array(cadence1)
    time1 = (time1 - start_timestamp) / 1000.0  # seconds

    #
    # Plot the data
    #
    ax1 = plt.subplot(311)
    ax1.plot(time1, power1, '-o', label='app [W]')
    ax1.legend(loc="upper right")
    plt.xlabel('Time (s)')
    plt.ylabel('Power (W)')

    plt.subplot(312, sharex=ax1)
    plt.plot(time1, speed1, '-o', label='app [m/s]')
    plt.legend(loc="upper right")
    plt.xlabel('Time (s)')
    plt.ylabel('speed (m/s)')

    plt.subplot(313, sharex=ax1)
    plt.plot(time1, cadence1, '-o', label='app [rpm]')
    plt.legend(loc="upper right")
    plt.xlabel('Time (s)')
    plt.ylabel('cadence (rpm)')

    plt.show()


if __name__ == "__main__":
    filepath = sys.argv[1]
    plot_fit_file(filepath)

