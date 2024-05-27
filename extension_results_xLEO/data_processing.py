import sqlite3
import matplotlib.pyplot as plt
import seaborn as sns
import os
import pandas as pd
from mpl_toolkits.axes_grid1.inset_locator import zoomed_inset_axes
from mpl_toolkits.axes_grid1.inset_locator import mark_inset
from matplotlib.ticker import FixedFormatter, FixedLocator
import json

#--------------------------------------- FUNCTIONS ---------------------------------------#

# results["data"] = (xss, values)
def get_delivery_ratio(INPUT_PATH, scenarios, xs, repetitions, TTR):
    results = {}

    for scenario in scenarios:

        xss = []
        values = []

        for x in xs:
            for rep in repetitions:
                # input_path = INPUT_PATH + scenario + "General-TTF=%sh,TTR=%sh-#%d.sca" % (str(x), str(TTR), rep)
                input_path = INPUT_PATH + scenario + "General-#%d.sca" % (rep)

                xss.append(x)

                print(input_path)
                conn = sqlite3.connect(input_path)
                conn.row_factory = sqlite3.Row
                cur = conn.cursor()

                cur.execute("SELECT SUM(scalarValue) AS result FROM scalar WHERE scalarName='%s'"%("appBundleSent:count"))
                rows1 = cur.fetchall()
                tx_packets = 0 if (rows1[0]["result"] == None) else rows1[0]["result"]

                cur.execute("SELECT SUM(scalarValue) AS result FROM scalar WHERE scalarName='%s'"%("appBundleReceived:count"))
                rows1 = cur.fetchall()
                rx_packets = 0 if (rows1[0]["result"] == None) else rows1[0]["result"]

                delivery_ratio = float(rx_packets) / float(tx_packets) * 100
                values.append(delivery_ratio)

        results[scenario] = (xss, values)
    return results

# results["data"] = (xss, values)
def get_delivery_delay(INPUT_PATH, scenarios, xs, repetitions, TTR):
    results = {}

    for scenario in scenarios:

        xss = []
        values = []

        for x in xs:
            for rep in repetitions:
                #input_path = INPUT_PATH + scenario + "General-TTF=%sh,TTR=%sh-#%d.sca" % (str(x), str(TTR), rep)
                input_path = INPUT_PATH + scenario + "General-#%d.sca" % (rep)

                xss.append(x)

                conn = sqlite3.connect(input_path)
                conn.row_factory = sqlite3.Row
                cur = conn.cursor()

                query = "SELECT AVG(scalarValue) AS result FROM scalar WHERE scalarName='%s'" % "appBundleReceivedDelay:mean"
                cur.execute(query)
                rows1 = cur.fetchall()
                mean_delay = 0 if (rows1[0]["result"] == None) else rows1[0]["result"] / 3600
                values.append(mean_delay)

        results[scenario] = (xss, values)
    return results

# results["data"] = (xss, avg_values, max_values)
def get_buffer_occupancy(INPUT_PATH, scenarios, xs, repetitions, nodes):
    results = {}

    for scenario in scenarios:

        xss = []
        values_avg = []
        values_max = []

        for x in xs:
            for rep in repetitions:
                input_path = INPUT_PATH + scenario + "General-#%d.sca" % (rep)

                xss.append(x)

                print(input_path)
                conn = sqlite3.connect(input_path)
                conn.row_factory = sqlite3.Row
                cur = conn.cursor()

                query_total_packets = "SELECT SUM(scalarValue) AS result FROM scalar WHERE scalarName='%s'" % "appBundleSent:count"
                cur.execute(query_total_packets)
                rows0 = cur.fetchall()
                value_total_packets = 0 if (rows0[0]["result"] == None) else rows0[0]["result"]

                query_avg = "SELECT AVG(scalarValue) AS result FROM scalar WHERE scalarName='%s'" % "sdrBundleStored:timeavg"
                nodes_str = ','.join(f"'dtnsim.node[{node}].dtn'" for node in nodes)
                query_avg += f" AND moduleName IN ({nodes_str})"
                cur.execute(query_avg)
                rows1 = cur.fetchall()
                value_avg = 0 if (rows1[0]["result"] == None) else rows1[0]["result"]
                values_avg.append(value_avg/value_total_packets * 100)

                query_max = "SELECT AVG(scalarValue) AS result FROM scalar WHERE scalarName='%s'" % "sdrBundleStored:max"
                query_max += f" AND moduleName IN ({nodes_str})"
                cur.execute(query_max)
                rows2 = cur.fetchall()
                value_max = 0 if (rows2[0]["result"] == None) else rows2[0]["result"]
                values_max.append(value_max/value_total_packets * 100)

        results[scenario] = (xss, values_avg, values_max)
    return results



#--------------------------------------- PARAMETERS ---------------------------------------#
# Shareable parameters
number_of_LEOS_wanted = [5]
number_of_GS_wanted = []
number_of_HAGS_GS_wanted = [5]
number_of_repetitions = 100
# TTR = [5,25]
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

SDR = [0,100,200,500]


INPUT_PATH = "./dtnsim/simulations/HAPS_Analysis"
repetitions = list(range(0,number_of_repetitions))
#--------------------------------------- PROCESSING ---------------------------------------#
for leos in number_of_LEOS_wanted:
    scenarios = []
    simulationName = []
    # Get the scenarios names by reading the folders in the directory
    for folder in os.listdir('./dtnsim/simulations/HAPS_Analysis'):
        if len(str(leos)) == 2:
            if folder[0] + folder[1] == str(leos):
                scenarios.append('/' + folder + '/results/')
                simulationName.append(folder)
        else:
            if folder[0] == str(leos) and not folder[1].isdigit():
                scenarios.append('/' + folder + '/results/')
                simulationName.append(folder)
    # scenarios = []
    # simulationName = []
    # for number_of_LEOS in number_of_LEOS_wanted:
    #     for number_of_GS in number_of_GS_wanted:
    #         scenarios.append('/' + '%sLEO_%sGS' % (number_of_LEOS, number_of_GS) + '/results/')
    #         simulationName.append('%sLEO_%sGS' % (number_of_LEOS, number_of_GS))
    #     for number_of_HAGS_GS in number_of_HAGS_GS_wanted:
    #         scenarios.append('/' + '%sLEO_%sHAP_%sGS' % (number_of_LEOS, number_of_HAGS_GS, number_of_HAGS_GS) + '/results/')
    #         simulationName.append('%sLEO_%sHAP_%sGS' % (number_of_LEOS, number_of_HAGS_GS, number_of_HAGS_GS))
    #         scenarios.append('/' + '%sLEO_%sHAP_%sGS_EQ' % (number_of_LEOS, number_of_HAGS_GS, number_of_HAGS_GS) + '/results/')
    #         simulationName.append('%sLEO_%sHAP_%sGS_EQ' % (number_of_LEOS, number_of_HAGS_GS, number_of_HAGS_GS))

    # Iterate over each TTR
    # for ttr in TTR:
    ttr = 25
    # Get the results
    #print(scenarios)
    resultsDR = get_delivery_ratio(INPUT_PATH, scenarios, TTF, repetitions, ttr)
    resultsDD = get_delivery_delay(INPUT_PATH, scenarios, TTF, repetitions, ttr)
    resultsBO = get_buffer_occupancy(INPUT_PATH, scenarios, TTF, repetitions, [3, 5, 7, 9, 11])

    # Save the results in a json file
    data = {
        "ttf_values": resultsDR[scenarios[0]][0],
        "delivery_ratio": {
            scenario: result[1] for scenario, result in zip(simulationName, resultsDR.values())
        },
        "delivery_delay": {
            scenario: result[1] for scenario, result in zip(simulationName, resultsDD.values())
        },
        "buffer_occupancy_avg": {
            scenario: result[1] for scenario, result in zip(simulationName, resultsBO.values())
        },
        "buffer_occupancy_max": {
            scenario: result[2] for scenario, result in zip(simulationName, resultsBO.values())
        }
    }


    with open('extension_results_xLEO/data_json/results_LEO=%s_TTR=%s.json' % (leos, ttr), 'w') as json_file:
        json.dump(data, json_file)

    print("Data processing for %s LEOS and for TTR=%s is done" % (leos,ttr))

