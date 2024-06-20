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


#--------------------------------------- PLOT DR ---------------------------------------#

def plot_DR_RunTest1_5(resultsDR, liHAGS, clr, ttf_values, TTF, WIDTH, HEIGHT, LINEWIDTH, m0, mar0, medgewidth, m1, mar1, number_of_GS_wanted, number_of_HAGS_GS_wanted, leos, ttr, dest):
    fig, ax = plt.subplots(figsize=(WIDTH,HEIGHT))
    for i in range(3):
        sns.lineplot(x=ttf_values, y=resultsDR[i], color=clr[i], marker=m0, label=liHAGS[i], markersize=mar0, markeredgecolor=clr[i], markerfacecolor='none', markeredgewidth=medgewidth, ax=ax)

    ax.set_xlabel("TCC [hours]", fontsize=13)
    ax.set_ylabel("Delivery ratio [% of files generated]", fontsize=13)
    plt.tight_layout()

    plt.grid(linewidth=LINEWIDTH, zorder=0)
    ax.legend(loc='lower right', prop={'size': 10})
    plt.xscale('log')
    plt.xticks(TTF, [str(val) for val in TTF])
    plt.savefig("extension_results_xLEO/plots/delivery_ratio_DEST=%s_TCS=%s.pdf" % (str(dest), str(ttr)))
    plt.cla()
    plt.clf()


def plot_DR_RunTest6(resultsDR, liHAGS, clr, ttf_values, TTF, WIDTH, HEIGHT, LINEWIDTH, m0, mar0, medgewidth, m1, mar1, nbCurves, name, leos, ttr, dest):
    fig, ax = plt.subplots(figsize=(WIDTH,HEIGHT))
    for i in range(nbCurves):
        sns.lineplot(x=ttf_values, y=resultsDR[i], color=clr[i], marker=m0, label=liHAGS[i], markersize=mar0, markeredgecolor=clr[i], markerfacecolor='none', markeredgewidth=medgewidth, ax=ax)

    
    ax.set_xlabel("TCC [hours]", fontsize=13)
    ax.set_ylabel("Delivery ratio [% of files generated]", fontsize=13)
    plt.tight_layout()

    plt.grid(linewidth=LINEWIDTH, zorder=0)
    ax.legend(loc='lower right', prop={'size': 10})
    plt.xscale('log')
    plt.xticks(TTF, [str(val) for val in TTF])
    plt.savefig("extension_results_xLEO/plots/delivery_ratio_DEST=%s_TCS=%s_%s.pdf" % (str(dest), str(ttr), name))
    plt.cla()
    plt.clf()

#--------------------------------------- PLOT DD ---------------------------------------#
def plot_DD_RunTest1_5(resultsDD, count, liHAGS, clr, ttf_values, TTF, WIDTH, HEIGHT, LINEWIDTH, m0, mar0, medgewidth, m1, mar1, number_of_GS_wanted, number_of_HAGS_GS_wanted, leos, ttr, dest):
    fig, ax = plt.subplots(figsize=(WIDTH,HEIGHT))

    cte = len(repetitions)
    grey_color = "#CCCCCC"

    print("test")

    for i in range(len(number_of_GS_wanted)):
        sns.lineplot(x=ttf_values[:count[i]+cte], y=resultsDD[i][:count[i]+cte], color=grey_color, marker=m0, markersize=mar0, markeredgecolor=grey_color, markerfacecolor='none', markeredgewidth=medgewidth, ax=ax)
        sns.lineplot(x=ttf_values[count[i]:], y=resultsDD[i][count[i]:], color=clr[i], marker=m0, label=liHAGS[i], markersize=mar0, markeredgecolor=clr[i], markerfacecolor='none', markeredgewidth=medgewidth, ax=ax)

    for j in range(len(number_of_GS_wanted), len(number_of_GS_wanted) + len(number_of_HAGS_GS_wanted)):
        sns.lineplot(x=ttf_values[:count[j]+cte], y=resultsDD[j][:count[j]+cte], color=grey_color, marker=m1, markersize=mar1, markeredgecolor=grey_color, ax=ax)
        sns.lineplot(x=ttf_values[count[j]:], y=resultsDD[j][count[j]:], color=clr[j], marker=m1, label=liHAGS[j], markersize=mar1, markeredgecolor=clr[j], ax=ax)

    ax.set_xlabel("TCC [hours]", fontsize=13)
    ax.set_ylabel("Delivery delay [hours]", fontsize=13)
    plt.tight_layout()
    plt.grid(linewidth=LINEWIDTH, zorder=0)
    ax.legend(loc='upper right',  prop={'size': 10})
    plt.xscale('log')
    plt.xticks(TTF, [str(val) for val in TTF])
    plt.ylim(0,100)
    plt.savefig("extension_results_xLEO/plots/delivery_delay_DEST=%s_TCS=%s.pdf" % (str(dest), str(ttr)))
    plt.cla()
    plt.clf()

def plot_DD_RunTest6(resultsDD, count, liHAGS, clr, ttf_values, TTF, WIDTH, HEIGHT, LINEWIDTH, m0, mar0, medgewidth, m1, mar1, nbCurves, name, leos, ttr, dest):
    fig, ax = plt.subplots(figsize=(WIDTH,HEIGHT))

    cte = len(repetitions)
    grey_color = "#CCCCCC"

    for i in range(nbCurves):
        sns.lineplot(x=ttf_values[:count[i]+cte], y=resultsDD[i][:count[i]+cte], color=grey_color, marker=m0, markersize=mar0, markeredgecolor=grey_color, markerfacecolor='none', markeredgewidth=medgewidth, ax=ax)
        sns.lineplot(x=ttf_values[count[i]:], y=resultsDD[i][count[i]:], color=clr[i], marker=m0, label=liHAGS[i], markersize=mar0, markeredgecolor=clr[i], markerfacecolor='none', markeredgewidth=medgewidth, ax=ax)

    ax.set_xlabel("TCC [hours]", fontsize=13)
    ax.set_ylabel("Delivery delay [hours]", fontsize=13)
    plt.tight_layout()
    plt.grid(linewidth=LINEWIDTH, zorder=0)
    ax.legend(loc='upper right',  prop={'size': 10})
    plt.xscale('log')
    plt.xticks(TTF, [str(val) for val in TTF])
    plt.ylim(0,100)
    plt.savefig("extension_results_xLEO/plots/delivery_delay_DEST=%s_TCS=%s_%s.pdf" % (str(dest), str(ttr), name))
    plt.cla()
    plt.clf()


#--------------------------------------- PLOT SDR ---------------------------------------#

def plot_SDR_RunTest5(liHAGS, clr, ttf_values, TTF, WIDTH, HEIGHT, LINEWIDTH, m0, mar0, medgewidth, m1, mar1, number_of_GS_wanted, number_of_HAGS_GS_wanted, leos, ttr, dest):
    fig, ax = plt.subplots(figsize=(WIDTH,HEIGHT))
    for i in range(len(number_of_GS_wanted)):
            sns.lineplot(x=ttf_values, y=resultsDR[i], color=clr[i], marker=m0, label=liHAGS[i], markersize=mar0, markeredgecolor=clr[i], markerfacecolor='none', markeredgewidth=medgewidth, ax=ax)

    for j in range(4):
        sns.lineplot(x=ttf_values, y=resultsDR[j], color=clr[j], marker=m1, label=liHAGS[j], markersize=mar1, markeredgecolor=clr[j], ax=ax)

    ax.set_xlabel("TCC [hours]", fontsize=13)
    ax.set_ylabel("Delivery ratio [% of files generated]", fontsize=13)
    plt.tight_layout()

    plt.grid(linewidth=LINEWIDTH, zorder=0)
    ax.legend(loc='lower right', prop={'size': 10})
    plt.xscale('log')
    plt.xticks(TTF, [str(val) for val in TTF])
    plt.savefig("extension_results_xLEO/plots/delivery_ratio_LEO=%s_TTR=%HAGS=%s.pdf" % (str(leos), str(ttr), str(number_of_HAGS_GS_wanted[i])))
    plt.cla()
    plt.clf()



#--------------------------------------- PROCESSING ---------------------------------------#
# Iterate over each TTR
# for ttr in TTR:
#     for hags in number_of_HAGS_GS_wanted:
#         liHAGS = []
#         resultsDR = []
#         resultsDD = []
#         for leos in number_of_LEOS_wanted:

#             li = []
#             li.append("%sLEO_%sHAP_%sGS" % (leos, hags, hags))

#             liHAGS.append(li.copy())
           
#             with open('extension_results_xLEO/data_json/results_LEO=%s_TTR=%s.json' % (leos, ttr), 'r') as json_file:
#                 data = json.load(json_file)

#             ttf_values = data['ttf_values']
#             for scenario in li:
#                 resultsDR.append(data['delivery_ratio'][scenario])
#                 resultsDD.append(data['delivery_delay'][scenario])

#             for stations in range(number_of_stations):
#                 count.append(len([value for value in ttf_values  if value < values[stations]]))

#         for leos in number_of_LEOS_wanted:
#             li = []
#             li.append("%sLEO_%sHAP_%sGS_EQ" % (leos, hags, hags))
#             print(li)

#             liHAGS.append(li.copy())
           
#             with open('extension_results_xLEO/data_json/results_LEO=%s_TTR=%s.json' % (leos, ttr), 'r') as json_file:
#                 data = json.load(json_file)

#             ttf_values = data['ttf_values']
#             for scenario in li:
#                 resultsDR.append(data['delivery_ratio'][scenario])
#                 resultsDD.append(data['delivery_delay'][scenario])

#             for stations in range(number_of_stations):
#                 count.append(len([value for value in ttf_values  if value < values[stations]]))


#         plot_DR_RunTest6(resultsDR, liHAGS, clr, ttf_values, TTF, WIDTH, HEIGHT, LINEWIDTH, m0, mar0, medgewidth, m1, mar1, len(number_of_LEOS_wanted)*2,"hags", leos, ttr, hags)
#         plot_DD_RunTest6(resultsDD, count, liHAGS, clr, ttf_values, TTF, WIDTH, HEIGHT, LINEWIDTH, m0, mar0, medgewidth, m1, mar1, len(number_of_LEOS_wanted)*2, "hags", leos, ttr, hags)



# Iterate over each TTR
# for ttr in TTR:
#     for gs in number_of_GS_wanted:
#         liHAGS = []
#         resultsDR = []
#         resultsDD = []
#         for leos in number_of_LEOS_wanted:
#             li = []
#             li.append("%sLEO_%sGS" % (leos, gs))

#             liHAGS.append(li.copy())

#             with open('extension_results_xLEO/data_json/results_LEO=%s_TTR=%s.json' % (leos, ttr), 'r') as json_file:
#                 data = json.load(json_file)
            
#             ttf_values = data['ttf_values']
#             for scenario in li:
#                 resultsDR.append(data['delivery_ratio'][scenario])
#                 resultsDD.append(data['delivery_delay'][scenario])

#             for stations in range(number_of_stations):
#                 count.append(len([value for value in ttf_values  if value < values[stations]]))
                    

#         plot_DR_RunTest6(resultsDR, liHAGS, clr, ttf_values, TTF, WIDTH, HEIGHT, LINEWIDTH, m0, mar0, medgewidth, m1, mar1, len(number_of_LEOS_wanted), "gs", leos, ttr, hags)
#         plot_DD_RunTest6(resultsDD, count, liHAGS, clr, ttf_values, TTF, WIDTH, HEIGHT, LINEWIDTH, m0, mar0, medgewidth, m1, mar1, len(number_of_LEOS_wanted), "gs", leos, ttr, hags)
# print("Plots for %s LEOS and TTR=%s are done" % (leos, ttr))

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
x_values = [[0, 0.10, 0.20, 0.30, 0.40, 0.50, 0.60, 0.70, 0.80, 0.90, 1],
            [0, 0.10, 0.20, 0.30, 0.40, 0.50, 0.60, 0.70, 0.80, 0.90, 1],
            [0, 0.10, 0.20, 0.30, 0.40, 0.50, 0.60, 0.70, 0.80, 0.90, 1]]
labels = ['5LEO_5HAP_5GS_opportunistic', '5LEO_5HAP_5GS_equal', '5LEO_5HAP_5GS_weighted']
typeOfScenario = ['opportunistic', 'equal', 'weighted']
avg_DR = []
avg_DD = []
std_DD = []
std_DR = []
avg_avg_BO = []
std_avg_BO= []
avg_max_BO = []
std_max_BO = []

for type in typeOfScenario:
    li = []
    resultsDR = []
    resultsDD = []
    resultsBOAvg = []
    resultsBOMax = []
    for i in range(number_of_random_failures):
        li.append('source=44_%s_5LEO_5HAP_5GS_TTF_%s' % (type, TTFinString[i]))


    with open('./extension_results_xLEO/data_json/results_LEO=5_TTR=25.json', 'r') as json_file:
        data = json.load(json_file)
    
    # for i in range(0,len(li),5):
    #     resultsDR.append(data['delivery_ratio'][li[i]] + data['delivery_ratio'][li[i+1]] + data['delivery_ratio'][li[i+2]] + data['delivery_ratio'][li[i+3]] + data['delivery_ratio'][li[i+4]])
    #     resultsDD.append(data['delivery_delay'][li[i]] + data['delivery_delay'][li[i+1]] + data['delivery_delay'][li[i+2]] + data['delivery_delay'][li[i+3]] + data['delivery_delay'][li[i+4]])
    #     resultsBOAvg.append(data['buffer_occupancy_avg'][li[i]] + data['buffer_occupancy_avg'][li[i+1]] + data['buffer_occupancy_avg'][li[i+2]] + data['buffer_occupancy_avg'][li[i+3]] + data['buffer_occupancy_avg'][li[i+4]])
    #     resultsBOMax.append(data['buffer_occupancy_max'][li[i]] + data['buffer_occupancy_max'][li[i+1]] + data['buffer_occupancy_max'][li[i+2]] + data['buffer_occupancy_max'][li[i+3]] + data['buffer_occupancy_max'][li[i+4]])
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


fig, ax = plt.subplots(figsize=(WIDTH,HEIGHT))
for i in range(3):
    ax.plot(x_values[i], avg_DR[i], color=clr[i], marker=m0, label=typeOfScenario[i])
    avg_DR_arr = np.array(avg_DR[i])
    std_DR_arr = np.array(std_DR[i])
    ax.fill_between(x_values[i], avg_DR_arr - std_DR_arr, avg_DR_arr + std_DR_arr, color=clr[i], alpha=0.3)
 
ax.set_xlabel("Max deviation of TCC from 1.05h", fontsize=13)
ax.set_ylabel("Delivery ratio [% of files generated]", fontsize=13)
plt.tight_layout()
plt.grid(linewidth=LINEWIDTH, zorder=0)
ax.legend(loc='lower right', prop={'size': 10})
plt.savefig("extension_results_xLEO/plots/delivery_ratio_V9.pdf")
plt.cla()
plt.clf()


fig, ax = plt.subplots(figsize=(WIDTH,HEIGHT))
for i in range(3):
    ax.plot(x_values[i], avg_DD[i], color=clr[i], marker=m0, label=typeOfScenario[i])
    avg_DD_arr = np.array(avg_DD[i])
    std_DD_arr = np.array(std_DD[i])
    ax.fill_between(x_values[i], avg_DD_arr - std_DD_arr, avg_DD_arr + std_DD_arr, color=clr[i], alpha=0.3)
 
ax.set_xlabel("Max deviation of TCC from 1.05h", fontsize=13)
ax.set_ylabel("Delivery Delay [hours]", fontsize=13)
plt.tight_layout()
plt.grid(linewidth=LINEWIDTH, zorder=0)
ax.legend(loc='lower right', prop={'size': 10})
plt.savefig("extension_results_xLEO/plots/delivery_delay_V9.pdf")
plt.cla()
plt.clf()

fig, ax = plt.subplots(figsize=(WIDTH,HEIGHT))
for i in range(3):
    ax.plot(x_values[i], avg_avg_BO[i], color=clr[i], marker=m0, label=typeOfScenario[i])
    avg_avg_BO_arr = np.array(avg_avg_BO[i])
    std_avg_BO_arr = np.array(std_avg_BO[i])
    ax.fill_between(x_values[i], avg_avg_BO_arr - std_avg_BO_arr, avg_avg_BO_arr + std_avg_BO_arr, color=clr[i], alpha=0.3)
 
ax.set_xlabel("Max deviation of TCC from 1.05h", fontsize=13)
ax.set_ylabel("Average Time In A Buffer [hours]", fontsize=13)
plt.tight_layout()
plt.grid(linewidth=LINEWIDTH, zorder=0)
ax.legend(loc='upper left', prop={'size': 10})
plt.savefig("extension_results_xLEO/plots/BufferOccupency_V9.pdf")
plt.cla()
plt.clf()


fig, ax = plt.subplots(figsize=(WIDTH,HEIGHT))
for i in range(3):
    ax.plot(x_values[i], avg_max_BO[i], color=clr[i], marker=m0, label=typeOfScenario[i])
    avg_BO_arr = np.array(avg_max_BO[i])
    std_BO_arr = np.array(std_max_BO[i])
    ax.fill_between(x_values[i], avg_BO_arr - std_BO_arr, avg_BO_arr + std_BO_arr, color=clr[i], alpha=0.3)
 
ax.set_xlabel("Max deviation of TCC from 1.05h", fontsize=13)
ax.set_ylabel("Buffer Max Occupency", fontsize=13)
plt.tight_layout()
plt.grid(linewidth=LINEWIDTH, zorder=0)
ax.legend(loc='upper left', prop={'size': 10})
plt.savefig("extension_results_xLEO/plots/MaxBufferOccupency_V9.pdf")
plt.cla()
plt.clf()




# RunTest1_5
# for leos in number_of_LEOS_wanted:
#     scenarios = []
#     li = []
#     for folder in os.listdir('dtnsim/simulations/HAPS_Analysis'):
#         if len(str(leos)) == 2:
#             if folder[0] + folder[1] == str(leos):
#                 scenarios.append('/' + folder + '/results/')
#                 li.append(folder)
#         else:
#             if folder[0] == str(leos) and not folder[1].isdigit():
#                 scenarios.append('/' + folder + '/results/')
#                 li.append(folder)

#     # SDR part
#     # li = []
#     # for haps in number_of_HAGS_GS_wanted:
#     #     for gs in number_of_GS_wanted:
#     #         li.append("1LEO_%sGS" % (gs))
#     #     for sdr in SDR:
#     #         li.append("1LEO_%sHAP_%sGS_%sSDR" % (haps, haps, sdr))
    
    # Replace HAP with HAGS (for the legend, because the folder's name is in fact... quite wrong :) )
#     liHAGS = li.copy()
#     for i in range(len(li)):
#         if "HAP" in liHAGS[i]:
#             liHAGS[i] = liHAGS[i].replace("HAP", "HAGS")


#     # Iterate over each TTR
#     for ttr in TTR:
#         # SDR part
#         # for i in range(len(li)//4):
#         with open('extension_results_xLEO/data_json/results_LEO=%s_TTR=%s.json' % (leos, ttr), 'r') as json_file:
#             data = json.load(json_file)

#         ttf_values = data['ttf_values']
#         resultsDR = []
#         resultsDD = []
#         # SDR part
#         # for scenario in li[i*4:(i+1)*4]:
#         for scenario in li:
#             resultsDR.append(data['delivery_ratio'][scenario])
#             resultsDD.append(data['delivery_delay'][scenario])

# plot_DR_RunTest1_5(resultsDR, liHAGS, clr, ttf_values, TTF, WIDTH, HEIGHT, LINEWIDTH, m0, mar0, medgewidth, m1, mar1, number_of_GS_wanted, number_of_HAGS_GS_wanted, leos, ttr, dest):
# plot_DD_RunTest1_5(resultsDD, count, liHAGS, clr, ttf_values, TTF, WIDTH, HEIGHT, LINEWIDTH, m0, mar0, medgewidth, m1, mar1, number_of_GS_wanted, number_of_HAGS_GS_wanted, leos, ttr, dest):

# plot_SDR_RunTest5(liHAGS, clr, ttf_values, TTF, WIDTH, HEIGHT, LINEWIDTH, m0, mar0, medgewidth, m1, mar1, number_of_GS_wanted, number_of_HAGS_GS_wanted, leos, ttr, dest):


