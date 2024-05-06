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

#--------------------------------------- PARAMETERS ---------------------------------------#
# Shareable parameters
number_of_LEOS_wanted =[33]
number_of_GS_wanted = [1]
number_of_HAGS_GS_wanted = [1]
number_of_repetitions = 10
TTR = [5,25]
TTF = [0.1,0.2,0.5,1,2,5,10]
#SDR = [0,2]



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
num_light_colors = 5
# Generate lighter/luminous color palette
light_palette = sns.color_palette("bright", n_colors=num_light_colors)
# Generate darker color palette
dc = sns.color_palette("dark", n_colors=num_dark_colors)
dark_palette = [dc[0], dc[1], dc[2], dc[4]]
# Combine the two palettes
clr = dark_palette + light_palette


# One line of value for each TTR
values= [0.1, 0.1, 0.1, 0.1, 0.1, 0.1, 0.1, 0.1, 0.1]


#--------------------------------------- PLOTING ---------------------------------------#
for leos in number_of_LEOS_wanted:
    scenarios = []
    li = []
    for folder in os.listdir('dtnsim/simulations/HAPS_Analysis'):
        if len(str(leos)) == 2:
            if folder[0] + folder[1] == str(leos):
                scenarios.append('/' + folder + '/results/')
                li.append(folder)
        else:
            if folder[0] == str(leos) and not folder[1].isdigit():
                scenarios.append('/' + folder + '/results/')
                li.append(folder)
    

    # Replace HAP with HAGS (for the legend, because the folder's name is in fact... quite wrong :) )
    liHAGS = li.copy()
    for i in range(len(li)):
        if "HAP" in liHAGS[i]:
            liHAGS[i] = liHAGS[i].replace("HAP", "HAGS")


    # Iterate over each TTR
    for ttr in TTR:
        with open('extension_results_xLEO/data_json/results_LEO=%s_TTR=%s.json' % (leos, ttr), 'r') as json_file:
            data = json.load(json_file)

        ttf_values = data['ttf_values']
        resultsDR = []
        resultsDD = []
        for scenario in li:
            resultsDR.append(data['delivery_ratio'][scenario])
            resultsDD.append(data['delivery_delay'][scenario])


        for stations in range(number_of_stations):
            count.append(len([value for value in ttf_values  if value < values[stations]]))

#--------------------------------------- PLOT SDR ---------------------------------------#

        # fig, ax = plt.subplots(figsize=(WIDTH,HEIGHT))
        # for i in range(len(number_of_GS_wanted)):
        #     for sdr in SDR:
        #         sns.lineplot(x=ttf_values, y=resultsDR[i][sdr], color=clr[i], marker=m0, label=f"{liHAGS[i]} - SDR Size {sdr}", markersize=mar0, markeredgecolor=clr[i], markerfacecolor='none', markeredgewidth=medgewidth, ax=ax)

        # for j in range(len(number_of_GS_wanted), len(number_of_GS_wanted) + len(number_of_HAGS_GS_wanted)):
        #     for sdr in SDR:
        #         sns.lineplot(x=ttf_values, y=resultsDR[j][sdr], color=clr[j], marker=m1, label=f"{liHAGS[j]} - SDR Size {sdr}", markersize=mar1, markeredgecolor=clr[j], ax=ax)

        # ax.set_xlabel("TCC [hours]", fontsize=13)
        # ax.set_ylabel("Delivery ratio [% of files generated]", fontsize=13)
        # plt.tight_layout()

        # plt.grid(linewidth=LINEWIDTH, zorder=0)
        # ax.legend(loc='lower right', prop={'size': 10})
        # plt.xscale('log')
        # plt.xticks(TTF, [str(val) for val in TTF])
        # plt.savefig("extension_results_xLEO/plots/delivery_ratio_LEO=%s_TTR=%s.pdf" % (str(leos), str(ttr)))
        # plt.cla()
        # plt.clf()


#--------------------------------------- PLOT DR ---------------------------------------#
        fig, ax = plt.subplots(figsize=(WIDTH,HEIGHT))
        for i in range(len(number_of_GS_wanted)):
            sns.lineplot(x=ttf_values, y=resultsDR[i], color=clr[i], marker=m0, label=liHAGS[i], markersize=mar0, markeredgecolor=clr[i], markerfacecolor='none', markeredgewidth=medgewidth, ax=ax)
        
        for j in range(len(number_of_GS_wanted), len(number_of_GS_wanted) + len(number_of_HAGS_GS_wanted)):
            sns.lineplot(x=ttf_values, y=resultsDR[j], color=clr[j], marker=m1, label=liHAGS[j], markersize=mar1, markeredgecolor=clr[j], ax=ax)

        ax.set_xlabel("TCC [hours]", fontsize=13)
        ax.set_ylabel("Delivery ratio [% of files generated]", fontsize=13)
        plt.tight_layout()

        plt.grid(linewidth=LINEWIDTH, zorder=0)
        ax.legend(loc='lower right', prop={'size': 10})
        plt.xscale('log')
        plt.xticks(TTF, [str(val) for val in TTF])
        plt.savefig("extension_results_xLEO/plots/delivery_ratio_LEO=%s_TCS=%s.pdf" % (str(leos), str(ttr)))
        plt.cla()
        plt.clf()


#--------------------------------------- PLOT DD ---------------------------------------#
        fig, ax = plt.subplots(figsize=(WIDTH,HEIGHT))

        cte = len(repetitions)
        grey_color = "#CCCCCC"

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
        plt.savefig("extension_results_xLEO/plots/delivery_delay_LEO=%s_TCS=%s.pdf" % (str(leos), str(ttr)))
        plt.cla()
        plt.clf()


        print("Plots for %s LEOS and TTR=%s are done" % (leos, ttr))