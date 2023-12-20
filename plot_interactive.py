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
import plotly.graph_objs as go
from plotly.subplots import make_subplots

def plot_interactive(filepath):

    # Load your GPX file
    with open(filepath, 'r') as gpx_file:
        gpx = gpxpy.parse(gpx_file)

    # Initialize lists for data
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
                    if delta_time > 0:
                        distance = point.distance_2d(segment.points[-2])
                        speed = distance / delta_time * 3.6  # Convert m/s to km/h
                        speeds.append(speed)
                    else:
                        speeds.append(0)

    # Create a map trace
    map_trace = go.Scattermapbox(
        lat=latitudes,
        lon=longitudes,
        mode='lines+markers',
        name='Path',
        marker=dict(size=5, color='blue'),
        hoverinfo='text',
        text=[f'Time: {t}, Speed: {s:.2f} km/h' for t, s in zip(times[1:], speeds)]
    )

    # Create a speed trace
    speed_trace = go.Scatter(
        x=times[1:],
        y=speeds,
        mode='lines+markers',
        name='Speed',
        marker=dict(color='red'),
        hoverinfo='skip'  # Adjust as needed
    )

    # Create a subplot and add traces
    fig = make_subplots(rows=2, cols=1, subplot_titles=('Workout Path', 'Speed Over Time'),
                        specs=[[{"type": "scattermapbox"}], [{"type": "scatter"}]])

    fig.add_trace(map_trace, row=1, col=1)
    fig.add_trace(speed_trace, row=2, col=1)

    # Update layout
    fig.update_layout(
        mapbox_style="open-street-map",
        mapbox_zoom=10,
        mapbox_center={"lat": latitudes[0], "lon": longitudes[0]},
        height=800,
        showlegend=False
    )

    # Show the figure
    fig.show()



if __name__ == '__main__':
    filepath = sys.argv[1]

    plot_interactive(filepath)


