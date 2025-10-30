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
data_directory = './data'
data_file = 'Sample_Data.csv'
diseases = ['INFLUENZA','RSV','HMPV','PARAINFLUENZA','OTHER']

ll_fields = [disease+'_loglikelihood_T' for disease in diseases]
priors = normalize([(0.1/(len(diseases)-1)) if dx!='OTHER' else 0.9 for dx in diseases],1.0)
admission_date_field, delimiter, file_missing_value, data_missing_value, base = 'Admit_date_time', ',', 'M', 'M', 10.0
equivalent_sample_size, moving_average_window = 10, 7

# ------------------------------------------------------------------------
# Command Line Arguments
# ------------------------------------------------------------------------
parser = argparse.ArgumentParser(description='ILI Tracker')
parser.add_argument('--data_directory', type=str, default='./data', help='Directory containing the data file')
parser.add_argument('--data_file', type=str, default='Sample_Data.csv', help='Data file')
parser.add_argument('--diseases', type=str, default='INFLUENZA,RSV,HMPV,PARAINFLUENZA,OTHER', help='List of diseases')

args = parser.parse_args()
if args.diseases:
    diseases = args.diseases.split(',')
if args.data_directory:
    data_directory = args.data_directory
if args.data_file:
    data_file = args.data_file

# ------------------------------------------------------------------------

data = Data(admission_date_field, delimiter, file_missing_value, data_missing_value, data_directory + os.sep + data_file)
ili_tracker_results = ili_tracker(diseases, priors, ll_fields, equivalent_sample_size, base, data)
daily_log_probability = ili_tracker_results['daily_log_probability']

print(data)
print(ili_tracker_results)
print("Daily Log Probability: ", daily_log_probability)


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
axes[len(diseases)].set_title('Daily Log Probability')
axes[len(diseases)].plot(moving_average(moving_average_window, daily_log_probability), color='red')
axes[len(diseases)].set_ylabel('Log Probability', color='red')
axes[len(diseases)].set_xticks(xticks)
axes[len(diseases)].set_xticklabels(xticklabels)
axes[len(diseases)].secondary_xaxis("top")
axes[len(diseases)].set_xlabel('Date')

output_png_file = data_directory + os.sep + data_file + '.png'
plt.savefig(output_png_file)

print("The Output of ILI Tracker saved to: ", output_png_file)

# ------------------------------------------------------------------------

quit()

# ------------------------------------------------------------------------

