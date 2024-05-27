import sqlite3
import matplotlib.pyplot as plt
import seaborn as sns
import os
import pandas as pd
from mpl_toolkits.axes_grid1.inset_locator import zoomed_inset_axes
from mpl_toolkits.axes_grid1.inset_locator import mark_inset
from matplotlib.ticker import FixedFormatter, FixedLocator
import json
import seaborn as sns
import matplotlib
import numpy as np
matplotlib.use('Agg')

# Shareable parameters
number_of_LEOS_wanted = [5]
number_of_GS_wanted = []
number_of_HAGS_GS_wanted = [5]
number_of_repetitions = 20
# TTR = [5, 25]
# TTF = [0.1,0.2,0.5,1,2,5,10,15,20,25,30,35,40]
number_of_random_failures = 11
TTR = [[25,25,25,25,25] for i in range(number_of_random_failures)]
TTF = [[1.05,1.05,1.05,1.05,1.05], 
        [0.95,1.00,1.05,1.10,1.15],
        [0.85,0.95,1.05,1.15,1.25],
        [0.75,0.90,1.05,1.20,1.35],
        [0.65,0.85,1.05,1.25,1.45],
        [0.55,0.80,1.05,1.30,1.55],
        [0.45,0.75,1.05,1.35,1.65],
        [0.35,0.70,1.05,1.40,1.75],
        [0.25,0.65,1.05,1.45,1.85],
        [0.15,0.60,1.05,1.50,1.95],
        [0.05,0.55,1.05,1.55,2.05]
        ]

repetitions = list(range(0,number_of_repetitions))
count = []
INPUT_PATH = "dtnsim/simulations/HAPS_Analysis"
number_of_stations = len(number_of_GS_wanted) + len(number_of_HAGS_GS_wanted)

m0,m1 = "s","o"
mar0,mar1 = 7,7
medgewidth = 2

WIDTH = 8
HEIGHT = 5
LINEWIDTH = 0.4

num_dark_colors = 10
num_light_colors = 10
# Generate lighter/luminous color palette
light_palette = sns.color_palette("bright", n_colors=num_light_colors)
# Generate darker color palette
dark_palette = sns.color_palette("dark", n_colors=num_dark_colors)
# Combine the two palettes
clr = dark_palette + light_palette


# One line of value for each TTR
values= [0.1, 0.1, 0.1, 0.1, 0.1, 0.1, 0.1, 0.1, 0.1]


TTRinString, TTFinString = [], []
for i in range(number_of_random_failures):
    ttrInString,ttfInString = '',''
    for j in range(number_of_HAGS_GS_wanted[0]):
        ttrInString += str(TTR[i][j]) + '_'
        ttfInString += str(TTF[i][j]) + '_'

    TTRinString += [ttrInString[:-1] ]
    TTFinString += [ttfInString[:-1]]



li = []
resultsDR = []
resultsDD = []
x_values = [[0, 0.10, 0.20, 0.30, 0.40, 0.50, 0.60, 0.70, 0.80, 0.90, 1], [0, 0.10, 0.20, 0.30, 0.40, 0.50, 0.60, 0.70, 0.80, 0.90, 1]]
labels = ['5LEO_5HAP_5GS_weighted']
typeOfScenario = ['weighted']
avg_DR = []
avg_DD = []
std_DD = []
std_DR = []

for type in typeOfScenario:
    li = []
    resultsDR = []
    resultsDD = []
    for i in range(number_of_random_failures):
        li.append("5LEO_5HAP_5GS_TTR_%s_TTF_%s_%s" % (TTRinString[i], TTFinString[i], type))

    with open('./extension_results_xLEO/data_json/V2_results_LEO=5_TTR=[25, 25, 25, 25, 25].json', 'r') as json_file:
        data = json.load(json_file)
    
    for scenario in li:
        resultsDR.append(data['delivery_ratio'][scenario])
        resultsDD.append(data['delivery_delay'][scenario])


    AVG_DR = []
    STD_DR = []
    AVG_DD = []
    STD_DD = []
    for j in range(len(resultsDR)):
        AVG_DR.append(np.mean(resultsDR[j]))
        STD_DR.append(1.96 * np.std(resultsDR[j]) / np.sqrt(len(resultsDR[j])))
        AVG_DD.append(np.mean(resultsDD[j]))
        STD_DD.append(1.96 * np.std(resultsDD[j]) / np.sqrt(len(resultsDD[j])))

    avg_DR.append(AVG_DR)
    std_DR.append(STD_DR)
    avg_DD.append(AVG_DD)
    std_DD.append(STD_DD)
    resultsDR = []
    resultsDD = []

    with open('./extension_results_xLEO/data_json/V3_results_LEO=5_TTR=[25, 25, 25, 25, 25].json', 'r') as json_file:
        data = json.load(json_file)
    
    for scenario in li:
        resultsDR.append(data['delivery_ratio'][scenario])
        resultsDD.append(data['delivery_delay'][scenario])


    AVG_DR = []
    STD_DR = []
    AVG_DD = []
    STD_DD = []
    for j in range(len(resultsDR)):
        AVG_DR.append(np.mean(resultsDR[j]))
        STD_DR.append(1.96 * np.std(resultsDR[j]) / np.sqrt(len(resultsDR[j])))
        AVG_DD.append(np.mean(resultsDD[j]))
        STD_DD.append(1.96 * np.std(resultsDD[j]) / np.sqrt(len(resultsDD[j])))

    avg_DR.append(AVG_DR)
    std_DR.append(STD_DR)
    avg_DD.append(AVG_DD)
    std_DD.append(STD_DD)



# print(resultsDR[0])
# print("")
# print(resultsDD[1])
# print("")
# print(resultsDD[2])


fig, ax = plt.subplots(figsize=(WIDTH,HEIGHT))

avg_DR_values = [np.mean(avg) for avg in avg_DR]
avg_DD_values = [np.mean(avg) for avg in avg_DD]

for i in range(2):
    avg_DR_values[i] = [avg_DR_values[i]]*11
    avg_DD_values[i] = [avg_DD_values[i]]*11

nameOfAverage = ["Average weightedBatch", "Average weightedDistributed"]
nameOfCurves = ["weightedBatch", "weightedDistributed"]

for i in range(2):
    plt.plot(x_values[i], avg_DR_values[i], color=clr[i], marker=m0, label=nameOfAverage[i])

for i in range(2):
    ax.plot(x_values[i], avg_DR[i], color=clr[i], marker=m0, label=nameOfCurves[i])
    avg_DR_arr = np.array(avg_DR[i])
    std_DR_arr = np.array(std_DR[i])
    ax.fill_between(x_values[i], avg_DR_arr - std_DR_arr, avg_DR_arr + std_DR_arr, color=clr[i], alpha=0.3)
 

ax.set_xlabel("Standard deviation", fontsize=13)
ax.set_ylabel("Delivery delay", fontsize=13)
plt.tight_layout()
plt.grid(linewidth=LINEWIDTH, zorder=0)
ax.legend(loc='lower right', prop={'size': 10})
plt.savefig("extension_results_xLEO/plots/delivery_ratio_V2_V3_Compared.pdf")
plt.cla()
plt.clf()



fig, ax = plt.subplots(figsize=(WIDTH,HEIGHT))
for i in range(2):
    plt.plot(x_values[i], avg_DD_values[i], color=clr[i], marker=m0, label=nameOfAverage[i])

for i in range(2):
    ax.plot(x_values[i], avg_DD[i], color=clr[i], marker=m0, label=nameOfCurves[i])
    avg_DD_arr = np.array(avg_DD[i])
    std_DD_arr = np.array(std_DD[i])
    ax.fill_between(x_values[i], avg_DD_arr - std_DD_arr, avg_DD_arr + std_DD_arr, color=clr[i], alpha=0.3)
 

ax.set_xlabel("Standard deviation", fontsize=13)
ax.set_ylabel("Delivery delay", fontsize=13)
plt.tight_layout()
plt.grid(linewidth=LINEWIDTH, zorder=0)
ax.legend(loc='lower right', prop={'size': 10})
plt.savefig("extension_results_xLEO/plots/delivery_delay_V2_V3_Compared.pdf")
plt.cla()
plt.clf()
