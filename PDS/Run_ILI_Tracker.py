#!/usr/bin/env python3
import os

from Data import Data
from Misc import *
from datetime import date
from ILI_Tracker import ili_tracker
import matplotlib.pyplot as plt
import argparse
import numpy as np


# Default
data_file = './data/Sample_Data.csv'
output_png_file = './data/ILI_Tracker_Output.png'
diseases = ['INFLUENZA','RSV','HMPV','PARAINFLUENZA','OTHER']

ll_fields = [disease+'_loglikelihood_T' for disease in diseases]
priors = normalize([(0.1/(len(diseases)-1)) if dx!='OTHER' else 0.9 for dx in diseases],1.0)
admission_date_field, delimiter, file_missing_value, data_missing_value, base = 'Admit_date_time', ',', 'M', 'M', 10.0
equivalent_sample_size, moving_average_window = 10, 7

# ------------------------------------------------------------------------
# Command Line Arguments
# ------------------------------------------------------------------------
parser = argparse.ArgumentParser(description='ILI Tracker')
parser.add_argument('--input_file', type=str, default=data_file, help='Input file')
parser.add_argument('--output_file', type=str, default=output_png_file, help='Output png file')
parser.add_argument('--diseases', type=str, default='INFLUENZA,RSV,HMPV,PARAINFLUENZA,OTHER', help='List of diseases')

args = parser.parse_args()
if args.diseases:
    diseases = args.diseases.split(',')
if args.input_file:
    data_file = args.input_file
if args.output_file:
    output_png_file = args.output_file

# ------------------------------------------------------------------------

data = Data(admission_date_field, delimiter, file_missing_value, data_missing_value, data_file)
ili_tracker_results = ili_tracker(diseases, priors, ll_fields, equivalent_sample_size, base, data)
daily_log_probability = ili_tracker_results['daily_log_probability']
window_size, min_window_size = 28, 28
daily_empirical_p = empirical_p(window_size, min_window_size, daily_log_probability)

print(data)
print(ili_tracker_results)
print("Daily Log Probability: ", daily_log_probability)
print("Daily Empirical P-Value: ", daily_empirical_p)


# ----------------------------------------------------------------------

dates = data.dates()
xticks = [dates.index(date) for date in dates if date.day==1]
xticklabels = [str(dates[d].month)+'/'+str(dates[d].year) for d in xticks]

# ----------------------------------------------------------------------

fig, axes = plt.subplots(len(diseases) + 1)
fig.tight_layout(pad=2.0)
fig.set_size_inches(16,10)

for i in range(len(diseases)):
    axes[i].set_title(diseases[i])
    axes[i].plot(moving_average(moving_average_window,ili_tracker_results[diseases[i]]), color='blue')
    axes[i].set_ylabel('ILI Tracker', color='blue')
    axes[i].set_xticks(xticks)
    axes[i].set_xticklabels(xticklabels)
    axes[i].secondary_xaxis("top")
axes[len(diseases)].set_title('P-Value of Novel Disease')
axes[len(diseases)].plot(moving_average(moving_average_window, daily_empirical_p), color='red')
axes[len(diseases)].set_ylabel('P-Value', color='red')
axes[len(diseases)].set_xticks(xticks)
axes[len(diseases)].set_xticklabels(xticklabels)
axes[len(diseases)].secondary_xaxis("top")
axes[len(diseases)].set_xlabel('Date')

plt.savefig(output_png_file)

print("The Output of ILI Tracker saved to: ", output_png_file)

# ------------------------------------------------------------------------

quit()

# ------------------------------------------------------------------------

