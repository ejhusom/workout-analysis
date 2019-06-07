# Workout analysis

This repository contains scripts for visualizing and analyzing a workout file from a GPS-watch or similar device. The code is a work in progress, and the only operative functions are currently for basic plotting of the workout data. 

The script currently support the following file formats:

- .json

Planned support for:

- .tcx
- .fit
- .gpx

## Dependecies

- Python 3, with the following modules:
    - numpy
    - matplotlib
    - bokeh    

## TrainingVisualizer.py

The class contains five different plot options, but currently the wanted plot option has to be chosen by changing the function calls at the bottom of the script.
