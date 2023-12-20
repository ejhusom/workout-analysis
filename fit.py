#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""One-liner describing module.

Author:
    Erik Johannes Husom

Created:
    2021

"""
import sys
from fit2gpx import Converter

filepath = sys.argv[1]

conv = Converter()          # create standard converter object
gpx = conv.fit_to_gpx(f_in=filepath, f_out='new.gpx')
