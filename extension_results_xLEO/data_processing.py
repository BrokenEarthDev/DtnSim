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
                input_path = INPUT_PATH + scenario + "General-TTF=%sh,TTR=%sh-#%d.sca" % (str(x), str(TTR), rep)

                xss.append(x)

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
                input_path = INPUT_PATH + scenario + "General-TTF=%sh,TTR=%sh-#%d.sca" % (str(x), str(TTR), rep)

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
def get_buffer_occupancy(INPUT_PATH, scenarios, xs, repetitions, node):
    results = {}

    for scenario in scenarios:

        xss = []
        values_avg = []
        values_max = []

        for x in xs:
            for rep in repetitions:
                input_path = INPUT_PATH + scenario + "General-TTF=%sh-#%d.sca" % (str(x), rep)

                xss.append(x)

                conn = sqlite3.connect(input_path)
                conn.row_factory = sqlite3.Row
                cur = conn.cursor()
                
                query_total_packets = "SELECT SUM(scalarValue) AS result FROM scalar WHERE scalarName='%s'" % "appBundleSent:count"
                cur.execute(query_total_packets)
                rows0 = cur.fetchall()
                value_total_packets = 0 if (rows0[0]["result"] == None) else rows0[0]["result"]
                
                query_avg = "SELECT AVG(scalarValue) AS result FROM scalar WHERE scalarName='%s'" % "sdrBundleStored:timeavg"
                query_avg += " AND moduleName='dtnsim.node[%s].dtn'" % node
                cur.execute(query_avg)
                rows1 = cur.fetchall()
                value_avg = 0 if (rows1[0]["result"] == None) else rows1[0]["result"]
                values_avg.append(value_avg/value_total_packets * 100)

                query_max = "SELECT AVG(scalarValue) AS result FROM scalar WHERE scalarName='%s'" % "sdrBundleStored:max"
                query_max += " AND moduleName='dtnsim.node[%s].dtn'" % node
                cur.execute(query_max)
                rows2 = cur.fetchall()
                value_max = 0 if (rows2[0]["result"] == None) else rows2[0]["result"]
                values_max.append(value_max/value_total_packets * 100)

        results[scenario] = (xss, values_avg, values_max)
    return results



#--------------------------------------- PARAMETERS ---------------------------------------#
# Shareable parameters
number_of_LEOS_wanted =[1]
number_of_GS_wanted = [1,5,10]
number_of_HAGS_GS_wanted = [1,3,5]
number_of_repetitions = 20
TTR = [5,25]
TTF = [0.1,0.2,0.5,1,2,5,10,15,20,25,30,35,40]
SDR = [0,1,2]


INPUT_PATH = "dtnsim/simulations/HAPS_Analysis"
repetitions = list(range(0,number_of_repetitions))
#--------------------------------------- PROCESSING ---------------------------------------#
for leos in number_of_LEOS_wanted:
    scenarios = []
    li = []
    # Get the scenarios names by reading the folders in the directory
    for folder in os.listdir('dtnsim/simulations/HAPS_Analysis'):
        if len(str(leos)) == 2:
            if folder[0] + folder[1] == str(leos):
                scenarios.append('/' + folder + '/results/')
                li.append(folder)
        else:
            if folder[0] == str(leos) and not folder[1].isdigit():
                scenarios.append('/' + folder + '/results/')
                li.append(folder)
    

    # Iterate over each TTR
    for ttr in TTR:
        # Get the results
        resultsDR = get_delivery_ratio(INPUT_PATH, scenarios, TTF, repetitions, ttr)
        resultsDD = get_delivery_delay(INPUT_PATH, scenarios, TTF, repetitions, ttr)

        # Save the results in a json file
        data = {
            "ttf_values": resultsDR[scenarios[0]][0],
            "delivery_ratio": {
                scenario: result[1] for scenario, result in zip(li, resultsDR.values())
            },
            "delivery_delay": {
                scenario: result[1] for scenario, result in zip(li, resultsDD.values())
            }
        }
        
        with open('extension_results_xLEO/data_json/results_LEO=%s_TTR=%s.json' % (leos, ttr), 'w') as json_file:
            json.dump(data, json_file)

        print("Data processing for %s LEOS and for TTR=%s is done" % (leos,ttr))

    