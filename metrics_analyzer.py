#!/usr/bin/env python3
# ==================================================================
# File:     metrics_analyzer.py
# Author:   Erik Johannes Husom
# Created:  2019-07-14
# ------------------------------------------------------------------
# Description:
# Analyzing metrics.
# ==================================================================
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

metrics = pd.read_csv('metrics.csv', parse_dates=['Timestamp'])
metrics.set_index('Timestamp',inplace=True)
metrics.head()

# Print all types of values
types = metrics.Type.unique()
print(*types, sep='\n')

notes_idx = np.argwhere(types=='notes')
types = np.delete(types, notes_idx)

scale_types = np.argwhere(types=='sleep quality')

plt.figure(figsize=(15, 4))

for type in types:
    values = metrics.loc[metrics['Type'] == type]

    plt.plot(values['Value'], 'x', label=type)

plt.legend()
plt.show()

