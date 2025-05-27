import os
import random
import multiprocessing

#-------------------------------------------- FUNCTION --------------------------------------------#
# To filter the contact plan to only keep the desired number of LEOs, GS and HAPS-GS
def contact_filterer(input_file, output_file, LEO_IDS_to_keep, GST_IDS_to_keep, HAPS_IDS_to_keep):
    with open(input_file, 'r') as file:
        lines = file.readlines()

    filtered_lines = []
    contacts_to_remove = []

    # Contact to remove between LEO and GS
    for leo in LEO_IDS_to_keep:
        for gs in GST_IDS_to_keep:
            contacts_to_remove.append((leo, gs))
    
    # Convert in string
    NODE_IDS_to_keep = [1] + LEO_IDS_to_keep + GST_IDS_to_keep + HAPS_IDS_to_keep
    for i in range(len(NODE_IDS_to_keep)):
        NODE_IDS_to_keep[i] = str(NODE_IDS_to_keep[i])

    #print(NODE_IDS_to_keep, output_file)

    # Make a link between an HAGS and its GS
    if HAPS_IDS_to_keep != []:
        for i in range(len(HAPS_IDS_to_keep)):
            filtered_lines.append('a contact +0 +604800 %s %s 1\n' % (HAPS_IDS_to_keep[i], GST_IDS_to_keep[i]))
            filtered_lines.append('a contact +0 +604800 %s %s 1\n' % (GST_IDS_to_keep[i], HAPS_IDS_to_keep[i]))


    # Filter the contact plan
    for line in lines:
        take = True
        columns = line.strip().split()

        # Remove contacts between LEO and GS in case of HAPS
        if HAPS_IDS_to_keep != []:
            for contact in contacts_to_remove:
                if(columns[4] == str(contact[0]) and columns[5] == str(contact[1])):
                    take = False
                if(columns[4] == str(contact[1]) and columns[5] == str(contact[0])):
                    take = False
                
            if len(columns) >= 6 and columns[4] in NODE_IDS_to_keep and columns[5] in NODE_IDS_to_keep and take:
                columns[6] = '1'  # data rate to 1
                line2 = ' '.join(columns)
                filtered_lines.append(line2 + '\n')

        # For GS only
        else:
            if len(columns) >= 6 and columns[4] in NODE_IDS_to_keep and columns[5] in NODE_IDS_to_keep:
                columns[6] = '1'  # data rate to 1
                line2 = ' '.join(columns)
                filtered_lines.append(line2 + '\n')
    

    with open(output_file, 'w') as file:
        file.writelines(filtered_lines)


#-------------------------------------------- CLEAN UP --------------------------------------------#
# # Delete all the simulation files in dtnsim/simulations/HAPS_Analysis 

# for folder in os.listdir('dtnsim/simulations/HAPS_Analysis'):
#     if folder[0].isdigit():
#         os.system('rm -r dtnsim/simulations/HAPS_Analysis/' + folder)

# Delete run.sh file
# os.system('rm dtnsim/simulations/HAPS_Analysis/run.sh')

# Delete all the contact plans in dtnsim/simulations/HAPS_Analysis/FilteredContactPlans
# for file in os.listdir('dtnsim/simulations/HAPS_Analysis/FilteredContactPlans'):
#     os.system('rm dtnsim/simulations/HAPS_Analysis/FilteredContactPlans/' + file)




#--------------------------------------- PARAMETERS OF THE SIMULATIONS ---------------------------------------#
name_to_id = {}

# Store the parameters and their associated key
with open('extension_results_xLEO/contactPlan/contact_plan_7d_name_to_id_mapping.txt', 'r') as file:
    for line in file:
        name, id = line.strip().split()
        name_to_id[id] = name

# Shareable parameters
number_of_LEOS_wanted = [1]
number_of_GS_wanted = []
number_of_HAGS_GS_wanted = [2]
number_of_repetitions = 20
number_of_random_failures = 11
SDR = 0
TTR, TTF = [], []


# Specific parameters
number_of_bundles = 100
name = 'weighted'
distribution = 'equal'  # 'equal', 'randomWeighted', 'weighted' or 'opportunistic'

if distribution == 'equal':
    TTR = [5,25]
    TTF = [0.1,40]  

elif distribution == 'randomWeighted':
    # Loop to choose how many random values of TTR and TTF we want
    for i in range(number_of_random_failures):
    # for each GS, we randomly choose a value of TTR and TTF
        ttr,ttf = [],[]
        for j in range(number_of_HAGS_GS_wanted[0]):
            ttr.append(random.randint(5, 25))
            ttf.append(round(random.uniform(0.1, 40), 1))
        TTR.append(ttr)
        TTF.append(ttf)

    TTRinString, TTFinString = [], []
    for i in range(number_of_random_failures):
        ttrInString,ttfInString = '',''
        for j in range(number_of_HAGS_GS_wanted[0]):
            ttrInString += str(TTR[i][j]) + '_'
            ttfInString += str(TTF[i][j]) + '_'

        # print(ttrInString, ttfInString)

        TTRinString += [ttrInString[:-1]]
        TTFinString += [ttfInString[:-1]]

    # print(TTRinString, TTFinString)   

elif distribution == 'weighted':
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

    TTRinString, TTFinString = [], []
    for i in range(number_of_random_failures):
        ttrInString,ttfInString = '',''
        for j in range(number_of_HAGS_GS_wanted[0]):
            ttrInString += str(TTR[i][j]) + '_'
            ttfInString += str(TTF[i][j]) + '_'

        TTRinString += [ttrInString[:-1] ]
        TTFinString += [ttfInString[:-1]]

    # print(TTRinString, TTFinString)

# Find the first key that have a value that began with 'LEO'
first_LEO = 1
while name_to_id[str(first_LEO)][0:3] != 'LEO':
    first_LEO += 1 

input_file = 'extension_results_xLEO/contactPlan/contact_plan_7d_node-ids.txt'



#--------------------------------------- FILTERING THE CONTACT PLAN ---------------------------------------#
if distribution == 'equal':
    for number_of_LEOS in number_of_LEOS_wanted:
        LEO_IDS_to_keep = [first_LEO + i for i in range(number_of_LEOS)]

        for number_of_GS in number_of_GS_wanted:
            GST_IDS_to_keep = [2 + 2*i for i in range(number_of_GS)]
            output_file = 'dtnsim/simulations/HAPS_Analysis/FilteredContactPlans/contact_plan_7d_node-ids_%sLEO_%sGS_%sSDR.txt' % (number_of_LEOS, number_of_GS, SDR)
            contact_filterer(input_file, output_file, LEO_IDS_to_keep, GST_IDS_to_keep, [])

        for number_of_HAGS_GS in number_of_HAGS_GS_wanted:
            GST_IDS_to_keep = [2 + 2*i for i in range(number_of_HAGS_GS)]
            HAPS_IDS_to_keep = [3 + 2*i for i in range(number_of_HAGS_GS)]
            output_file = 'dtnsim/simulations/HAPS_Analysis/FilteredContactPlans/contact_plan_7d_node-ids_%sLEO_%sHAP_%sGS_EQ.txt' % (number_of_LEOS, number_of_HAGS_GS, number_of_HAGS_GS)
            contact_filterer(input_file, output_file, LEO_IDS_to_keep, GST_IDS_to_keep, HAPS_IDS_to_keep)

elif distribution == 'weighted' or distribution == 'randomWeighted':
    def process_filtering(input_file, output_file, LEO_IDS_to_keep, GST_IDS_to_keep, HAPS_IDS_to_keep):
        contact_filterer(input_file, output_file, LEO_IDS_to_keep, GST_IDS_to_keep, HAPS_IDS_to_keep)

    if __name__ == '__main__':
        processes = []
        for i in range(number_of_random_failures):
            for number_of_LEOS in number_of_LEOS_wanted:
                LEO_IDS_to_keep = [first_LEO + i for i in range(number_of_LEOS)]

                for number_of_GS in number_of_GS_wanted:
                    GST_IDS_to_keep = [2 + 2*i for i in range(number_of_GS)]
                    output_file = 'dtnsim/simulations/HAPS_Analysis/FilteredContactPlans/contact_plan_7d_node-ids_%sLEO_%sGS_%sSDR_TTR_%s_TTF_%s.txt' % (number_of_LEOS, number_of_GS, SDR, TTRinString[i], TTFinString[i])
                    p = multiprocessing.Process(target=process_filtering, args=(input_file, output_file, LEO_IDS_to_keep, GST_IDS_to_keep, []))
                    processes.append(p)
                    p.start()

                for number_of_HAGS_GS in number_of_HAGS_GS_wanted:
                    GST_IDS_to_keep = [2 + 2*i for i in range(number_of_HAGS_GS)]
                    HAPS_IDS_to_keep = [3 + 2*i for i in range(number_of_HAGS_GS)]
                    output_file = 'dtnsim/simulations/HAPS_Analysis/FilteredContactPlans/contact_plan_7d_node-ids_%sLEO_%sHAP_%sGS_TTR_%s_TTF_%s_%s.txt' % (number_of_LEOS, number_of_HAGS_GS, number_of_HAGS_GS, TTRinString[i], TTFinString[i], name)
                    p = multiprocessing.Process(target=process_filtering, args=(input_file, output_file, LEO_IDS_to_keep, GST_IDS_to_keep, HAPS_IDS_to_keep))
                    processes.append(p)
                    p.start()

        for process in processes:
            process.join()


#--------------------------------------- CREATE SIMULATION FILES ---------------------------------------#
# Create folders for the simulation 
FOLDERS_NAME = []
if distribution == 'equal':
    for number_of_LEOS in number_of_LEOS_wanted:
        for number_of_GS in number_of_GS_wanted:
            FOLDERS_NAME.append('%sLEO_%sGS' % (number_of_LEOS, number_of_GS))
        for number_of_HAGS_GS in number_of_HAGS_GS_wanted:
            FOLDERS_NAME.append('%sLEO_%sHAP_%sGS_EQ' % (number_of_LEOS, number_of_HAGS_GS, number_of_HAGS_GS))

    # Write the omnetpp.ini file
    for output_file_name in FOLDERS_NAME: 
        folder_path = 'dtnsim/simulations/HAPS_Analysis/' + output_file_name
        os.makedirs(folder_path, exist_ok=True)

        with open('dtnsim/simulations/HAPS_Analysis/' + output_file_name + '/omnetpp.ini' , 'w') as file:
            file.write('[General]\n')
            file.write('allow-object-stealing-on-deletion = true\n')
            file.write('network = src.dtnsim\n')
            file.write('repeat = %s\n' % number_of_repetitions)
            file.write('sim-time-limit = 604801s\n')
            file.write('outputvectormanager-class="omnetpp::envir::SqliteOutputVectorManager"\n')
            file.write('outputscalarmanager-class="omnetpp::envir::SqliteOutputScalarManager"\n')
            file.write('**.vector-recording=false\n')
            file.write('result-dir = results\n')
            file.write('dtnsim.nodesNumber = 109\n')
            file.write("dtnsim.node[*].dtn.routing = \"cgrModelRev17Distribution\"\n")

            if distribution != 'random':
                hags_match = output_file_name.find("HAP")
                num_hags = output_file_name[hags_match-2] + output_file_name[hags_match-1] if output_file_name[hags_match-2].isdigit() else output_file_name[hags_match-1]
                file.write("dtnsim.node[*].dtn.numHags = %s\n" % num_hags)

            file.write("dtnsim.node[*].dtn.routingType = \"routeListType:allPaths-firstDepleted,volumeAware:allContacts,extensionBlock:on,contactPlan:global,distribution:weighted,sdrModel:perNode\"\n")
            file.write("#dtnsim.node[*].dtn.printRoutingDebug=true\n")
            file.write("\n")
            file.write("dtnsim.central.contactsFile = \"../FilteredContactPlans/contact_plan_7d_node-ids_%s.txt\"\n" % (output_file_name))
            file.write("#dtnsim.node[*].dtn.saveBundleMap = true\n")
            file.write("#dtnsim.central.saveTopology = true\n")
            file.write("#dtnsim.central.saveFlows = true\n")
            file.write("#dtnsim.central.saveLpFlows = true\n")
            file.write("\n")
            file.write("# traffic generation\n")
            # for i in range(number_of_LEOS):
            #     node_index = first_LEO + i
            #     file.write("dtnsim.node[%s].app.enable=true\n" % node_index)
            #     file.write("dtnsim.node[%s].app.bundlesNumber=\"%s\"\n" % (node_index, number_of_bundles))
            #     file.write("dtnsim.node[%s].app.start=\"0\"\n" % node_index)
            #     file.write("dtnsim.node[%s].app.destinationEid=\"1\"\n" % node_index)
            #     file.write("dtnsim.node[%s].app.size=\"100\"\n" % node_index)
            file.write('dtnsim.node[44].app.enable=true\n')
            file.write('dtnsim.node[44].app.bundlesNumber="%s"\n' % number_of_bundles)
            file.write('dtnsim.node[44].app.start="0"\n')
            file.write('dtnsim.node[44].app.destinationEid="1"\n')
            file.write('dtnsim.node[44].app.size="100"\n')
            
            # Put the right SDR for the HAPS
            # for i in range(number_of_HAGS_GS):
            #     node_index = 3 + 2*i
            #     file.write("dtnsim.node[%s].dtn.sdrSize=%s\n" % (node_index, SDR))


            file.write("\n")
            file.write("# Nodes's failure rates\n")
            file.write("dtnsim.node[*].fault.faultSeed = ${repetition}*100\n")
            file.write("dtnsim.node[*].fault.meanTTF = ${TTF=%s}\n" % ','.join([str(ttf)+'h' for ttf in TTF]))
            file.write("dtnsim.node[*].fault.meanTTR = ${TTR=%s}\n" % ','.join([str(ttr)+'h' for ttr in TTR]))
            file.write("\n")
            file.write("\n".join([f"dtnsim.node[{i}].fault.enable = true" for i in range(2, 43, 2)]))

elif distribution == 'weighted' or distribution == 'randomWeighted':
    for i in range(number_of_random_failures):
        for number_of_LEOS in number_of_LEOS_wanted:
            for number_of_GS in number_of_GS_wanted:
                FOLDERS_NAME.append('%sLEO_%sGS' % (number_of_LEOS, number_of_GS))
            for number_of_HAGS_GS in number_of_HAGS_GS_wanted:
                FOLDERS_NAME.append('%sLEO_%sHAP_%sGS_TTR_%s_TTF_%s_%s' % (number_of_LEOS, number_of_HAGS_GS, number_of_HAGS_GS, TTRinString[i], TTFinString[i], name))

    i = 0
    # Write the omnetpp.ini file
    for output_file_name in FOLDERS_NAME: 
        folder_path = 'dtnsim/simulations/HAPS_Analysis/' + output_file_name
        os.makedirs(folder_path, exist_ok=True)

        with open('dtnsim/simulations/HAPS_Analysis/' + output_file_name + '/omnetpp.ini' , 'w') as file:
            file.write('[General]\n')
            file.write('allow-object-stealing-on-deletion = true\n')
            file.write('network = src.dtnsim\n')
            file.write('repeat = %s\n' % number_of_repetitions)
            file.write('sim-time-limit = 604801s\n')
            file.write('outputvectormanager-class="omnetpp::envir::SqliteOutputVectorManager"\n')
            file.write('outputscalarmanager-class="omnetpp::envir::SqliteOutputScalarManager"\n')
            file.write('**.vector-recording=false\n')
            file.write('result-dir = results\n')
            file.write('dtnsim.nodesNumber = 109\n')
            file.write("dtnsim.node[*].dtn.routing = \"cgrModelRev17Distribution\"\n")

            hags_match = output_file_name.find("HAP")
            num_hags = output_file_name[hags_match-2] + output_file_name[hags_match-1] if output_file_name[hags_match-2].isdigit() else output_file_name[hags_match-1]
            file.write("dtnsim.node[*].dtn.numHags = %s\n" % num_hags)
            file.write("dtnsim.node[*].dtn.MeanTTF = \"%s\"\n" % TTFinString[i])
            file.write("dtnsim.node[*].dtn.MeanTTR = \"%s\"\n" % TTRinString[i])

            file.write("dtnsim.node[*].dtn.routingType = \"routeListType:allPaths-firstDepleted,volumeAware:allContacts,extensionBlock:on,contactPlan:global,distribution:equal,sdrModel:perNode\"\n")
            file.write("#dtnsim.node[*].dtn.printRoutingDebug=true\n")
            file.write("\n")
            file.write("dtnsim.central.contactsFile = \"../FilteredContactPlans/contact_plan_7d_node-ids_%s.txt\"\n" % (output_file_name))

            file.write('dtnsim.node[44].app.enable=true\n')
            file.write('dtnsim.node[44].app.bundlesNumber="%s"\n' % number_of_bundles)
            file.write('dtnsim.node[44].app.start="0"\n')
            file.write('dtnsim.node[44].app.destinationEid="1"\n')
            file.write('dtnsim.node[44].app.size="100"\n')

            file.write("\n")
            file.write("# Nodes's failure rates\n")
            for j in range(len(TTF[i])):
                file.write("dtnsim.node[%s].fault.faultSeed = ${repetition}*100\n" % str(j*2+2))
                file.write("dtnsim.node[%s].fault.meanTTF = %sh\n" % (j*2+2, TTF[i][j]))
                file.write("dtnsim.node[%s].fault.meanTTR = %sh\n" % (j*2+2, TTR[i][j]))
            file.write("\n")
            file.write("\n".join([f"dtnsim.node[{i}].fault.enable = true" for i in range(2, 2*len(TTF[i])+2, 2)]))
        i+=1

# Create the script.sh file
for output_file_name in FOLDERS_NAME:
    with open('dtnsim/simulations/HAPS_Analysis/' + output_file_name + '/script.sh', 'w') as file:
        file.write("#!/bin/bash\n")
        file.write("\n")
        file.write("opp_runall -j6 ../../../dtnsim omnetpp.ini -n ../../../src -u Cmdenv -c General\n")
        file.write("\n")
        file.write(": <<'END'\n")
        file.write("END\n")


# Create the run.sh file
if distribution == 'equal':
    i = 0
    nbFiles = (len(number_of_GS_wanted) + len(number_of_HAGS_GS_wanted))
    for output_file_name in FOLDERS_NAME:
        if i % nbFiles == 0:
            with open('dtnsim/simulations/HAPS_Analysis/run%sLEOS.sh' % number_of_LEOS_wanted[i//nbFiles], 'w') as file:
                file.write("#!/bin/bash\n\n")

        with open('dtnsim/simulations/HAPS_Analysis/run%sLEOS.sh' % number_of_LEOS_wanted[i//nbFiles], 'a') as file:
            file.write("cd %s\n" % output_file_name)
            file.write("chmod +x script.sh\n") 
            file.write("./script.sh &\n")
            file.write("cd ..\n\n")

        if i+1 % nbFiles == 0:
            with open('dtnsim/simulations/HAPS_Analysis/run%sLEOS.sh' % number_of_LEOS_wanted[i//nbFiles], 'a') as file:
                file.write("\nwait\n")
                
        i += 1

elif distribution == 'weighted' or distribution == 'randomWeighted':
    i = 0
    nbFiles = (len(number_of_GS_wanted) + len(number_of_HAGS_GS_wanted))*number_of_random_failures
    for output_file_name in FOLDERS_NAME:
        if i % nbFiles == 0:
            with open('dtnsim/simulations/HAPS_Analysis/run%sLEOS.sh' % number_of_LEOS_wanted[i//nbFiles], 'w') as file:
                file.write("#!/bin/bash\n\n")

        with open('dtnsim/simulations/HAPS_Analysis/run%sLEOS.sh' % number_of_LEOS_wanted[i//nbFiles], 'a') as file:
            file.write("cd %s\n" % output_file_name)
            file.write("chmod +x script.sh\n") 
            file.write("./script.sh &\n")
            file.write("cd ..\n\n")

        if i+1 % nbFiles == 0:
            with open('dtnsim/simulations/HAPS_Analysis/run%sLEOS.sh' % number_of_LEOS_wanted[i//nbFiles], 'a') as file:
                file.write("\nwait\n")
                
        i += 1
