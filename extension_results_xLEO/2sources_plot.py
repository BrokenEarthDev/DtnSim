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

#--------------------------------------- PARAMETERS ---------------------------------------#
# Shareable parameters
number_of_LEOS_wanted = [5]
number_of_GS_wanted = []
number_of_HAGS_GS_wanted = [5]
number_of_repetitions = 500
# TTR = [5, 25]
# TTF = [0.1,0.2,0.5,1,2,5,10,15,20,25,30,35,40]
number_of_random_failures = 11
TTR = [[25,25,25,25,25] for i in range(number_of_random_failures)]
TTF = [[1.05,1.05,1.05,1.05,1.05],
        [0.95,1.0,1.05,1.1,1.15],
        [0.85,0.95,1.05,1.15,1.25],
        [0.75,0.9,1.05,1.2,1.35],
        [0.65,0.85,1.05,1.25,1.45],
        [0.55,0.8,1.05,1.3,1.55],
        [0.45,0.75,1.05,1.35,1.65],
        [0.35,0.7,1.05,1.4,1.75],
        [0.25,0.65,1.05,1.45,1.85],
        [0.15,0.6,1.05,1.5,1.95],
        [0.05,0.55,1.05,1.55,2.05]
        ]
#SDR = [0,100,200,500]
#nbSDR = 4



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


# RunFinal
li = []
x_values = [[1, 1.2, 1.5, 1.8, 2.15, 2.5, 3.7, 5.1, 7.5, 13, 40],
            [1, 1.2, 1.5, 1.8, 2.15, 2.5, 3.7, 5.1, 7.5, 13, 40],
            [1, 1.2, 1.5, 1.8, 2.15, 2.5, 3.7, 5.1, 7.5, 13, 40]]
labels = ['5LEO_5HAP_5GS_opportunistic', '5LEO_5HAP_5GS_equal', '5LEO_5HAP_5GS_weighted']
typeOfScenario = ['Greedy, average TCC = 1.05h', 
                  'Equal, average TCC = 1.05h', 
                  'Weighted, average TCC = 1.05h',
                  ]
nameOfScenario = ['opportunistic', 'equal', 'weighted']
avg_DR = []
avg_DD = []
std_DD = []
std_DR = []
avg_avg_BO = []
std_avg_BO= []
avg_max_BO = []
std_max_BO = []

for type in nameOfScenario:

    li = []
    resultsDR = []
    resultsDD = []
    resultsBOAvg = []
    resultsBOMax = []
    for i in range(number_of_random_failures):
        li.append('source=44_%s_5LEO_5HAP_5GS_TTF_%s' % (type, TTFinString[i]))

    with open('./extension_results_xLEO/data_json/2sources_results.json', 'r') as json_file:
        data = json.load(json_file)
    
    for scenarios in li:
        resultsDR.append(data['delivery_ratio'][scenarios])
        resultsDD.append(data['delivery_delay'][scenarios])
        resultsBOAvg.append(data['buffer_occupancy_avg'][scenarios])
        resultsBOMax.append(data['buffer_occupancy_max'][scenarios])

        
    AVG_DR = []
    STD_DR = []
    AVG_DD = []
    STD_DD = []
    AVG_AVG_BO = []
    STD_AVG_BO = []
    AVG_MAX_BO = []
    STD_MAX_BO = []

    for j in range(len(resultsDR)):
        AVG_DR.append(np.mean(resultsDR[j]))
        STD_DR.append(1.96 * np.std(resultsDR[j]) / np.sqrt(len(resultsDR[j])))
        AVG_DD.append(np.mean(resultsDD[j]))
        STD_DD.append(1.96 * np.std(resultsDD[j]) / np.sqrt(len(resultsDD[j])))
    for k in range(len(resultsBOAvg)):
        AVG_AVG_BO.append(np.mean(resultsBOAvg[k]))
        STD_AVG_BO.append(1.96 * np.std(resultsBOAvg[k]) / np.sqrt(len(resultsBOAvg[k])))
        AVG_MAX_BO.append(np.mean(resultsBOMax[k]))
        STD_MAX_BO.append(1.96 * np.std(resultsBOMax[k]) / np.sqrt(len(resultsBOMax[k])))
        

    avg_DR.append(AVG_DR)
    std_DR.append(STD_DR)
    avg_DD.append(AVG_DD)
    std_DD.append(STD_DD)
    avg_avg_BO.append(AVG_AVG_BO)
    std_avg_BO.append(STD_AVG_BO)
    avg_max_BO.append(AVG_MAX_BO)
    std_max_BO.append(STD_MAX_BO)


# print(resultsDR[0])
# print("")
# print(resultsDD[1])
# print("")
# print(resultsDD[2])
alpha1 = 0.3
alpha2 = 0.4
alpha3 = 0.1
fontSize1 = 15
fontSize2 = 11

m =["s","o","x"]


fig, ax = plt.subplots(figsize=(WIDTH,HEIGHT))
for i in range(3):
    ax.plot(x_values[i], avg_DR[i], color=clr[i], marker=m[i], label=typeOfScenario[i])
    avg_DR_arr = np.array(avg_DR[i])
    std_DR_arr = np.array(std_DR[i])
    ax.fill_between(x_values[i], avg_DR_arr - std_DR_arr, avg_DR_arr + std_DR_arr, color=clr[i], alpha=alpha1)
 
ax.set_xlabel("Ratio between the more and the less cloudy area", fontsize=fontSize1)
ax.set_ylabel("Delivery Ratio [% of files generated]", fontsize=fontSize1)
plt.tight_layout()
plt.xscale('log')
# plt.ylim(35,100)
plt.grid(linewidth=LINEWIDTH, zorder=0)
ax.legend(loc='lower left', prop={'size': fontSize2},borderpad=0.2,labelspacing=0.40)
plt.savefig("extension_results_xLEO/plots/delivery_ratio_final2sources.pdf")
plt.cla()
plt.clf()


fig, ax = plt.subplots(figsize=(WIDTH,HEIGHT))
for i in range(3):
    ax.plot(x_values[i][:-2], avg_DD[i][:-2], color=clr[i], marker=m[i], label=typeOfScenario[i])
    ax.plot(x_values[i][-3:], avg_DD[i][-3:], color='gray', marker=m0, label=None)
    avg_DD_arr = np.array(avg_DD[i])
    std_DD_arr = np.array(std_DD[i])
    ax.fill_between(x_values[i][:-2], avg_DD_arr[:-2] - std_DD_arr[:-2], avg_DD_arr[:-2] + std_DD_arr[:-2], color=clr[i], alpha=alpha1)
    ax.fill_between(x_values[i][-3:], np.array(avg_DD[i][-3:]) - np.array(std_DD[i][-3:]), np.array(avg_DD[i][-3:]) + np.array(std_DD[i][-3:]), color='gray', alpha=alpha1)


ax.set_xlabel("Ratio between the more and the less cloudy area", fontsize=fontSize1)
ax.set_ylabel("Delivery Delay [hours]", fontsize=fontSize1)
plt.tight_layout()
plt.xscale('log')
# plt.ylim(44,76)
plt.grid(linewidth=LINEWIDTH, zorder=0)
ax.legend(loc='best', prop={'size': fontSize2},borderpad=0.2,labelspacing=0.40)
plt.savefig("extension_results_xLEO/plots/2sources_DD_final.pdf")
plt.cla()
plt.clf()

fig, ax = plt.subplots(figsize=(WIDTH,HEIGHT))
for i in range(3):
    ax.plot(x_values[i], avg_avg_BO[i], color=clr[i], marker=m[i], label=typeOfScenario[i])
    avg_avg_BO_arr = np.array(avg_avg_BO[i])
    std_avg_BO_arr = np.array(std_avg_BO[i])
    ax.fill_between(x_values[i], avg_avg_BO_arr - std_avg_BO_arr, avg_avg_BO_arr + std_avg_BO_arr, color=clr[i], alpha=alpha1)

ax.set_xlabel("Ratio between the more and the less cloudy area", fontsize=fontSize1)
ax.set_ylabel("Average Time in all HAGS Buffer [hours]", fontsize=fontSize1)
plt.tight_layout()
plt.xscale('log')
# plt.ylim(39,156)
plt.grid(linewidth=LINEWIDTH, zorder=0)
ax.legend(loc='upper left', prop={'size': fontSize2},borderpad=0.2,labelspacing=0.40)
plt.savefig("extension_results_xLEO/plots/2sources_BufferOccupency_final.pdf")
plt.cla()
plt.clf()


fig, ax = plt.subplots(figsize=(WIDTH,HEIGHT))
for i in range(3):
    ax.plot(x_values[i], avg_max_BO[i], color=clr[i], marker=m0, label=typeOfScenario[i])
    avg_BO_arr = np.array(avg_max_BO[i])
    std_BO_arr = np.array(std_max_BO[i])
    ax.fill_between(x_values[i], avg_BO_arr - std_BO_arr, avg_BO_arr + std_BO_arr, color=clr[i], alpha=alpha1)

ax.set_xlabel("Ratio between the more and the less cloudy area", fontsize=15)
ax.set_ylabel("Buffer Max Occupancy", fontsize=15)
plt.tight_layout()
plt.xscale('log')
# plt.ylim(119,187)
plt.grid(linewidth=LINEWIDTH, zorder=0)
ax.legend(loc='lower left', prop={'size': fontSize2},borderpad=0.2,labelspacing=0.40)
plt.savefig("extension_results_xLEO/plots/MaxBufferOccupency_final2sources.pdf")
plt.cla()
plt.clf()