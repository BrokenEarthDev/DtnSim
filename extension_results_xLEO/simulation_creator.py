import os

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

    print(NODE_IDS_to_keep, output_file)

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

# # Delete run.sh file
# os.system('rm dtnsim/simulations/HAPS_Analysis/run.sh')

# # Delete all the contact plans in dtnsim/simulations/HAPS_Analysis/FilteredContactPlans
# for file in os.listdir('dtnsim/simulations/HAPS_Analysis/FilteredContactPlans'):
#     os.system('rm dtnsim/simulations/HAPS_Analysis/FilteredContactPlans/' + file)




#--------------------------------------- FILTER CONTACT PLAN ---------------------------------------#
name_to_id = {}

# Store the parameters and their associated key
with open('extension_results_xLEO/contactPlan/contact_plan_7d_name_to_id_mapping.txt', 'r') as file:
    for line in file:
        name, id = line.strip().split()
        name_to_id[id] = name

# Shareable parameters
number_of_LEOS_wanted =[1]
number_of_GS_wanted = [1,5,10]
number_of_HAGS_GS_wanted = [1,3,5]
number_of_repetitions = 20
TTR = [5,25]
TTF = [0.1,0.2,0.5,1,2,5,10,15,20,25,30,35,40]
SDR = 0

# Specific parameters
number_of_bundles = 50

# Find the first key that have a value that began with 'LEO'
first_LEO = 1
while name_to_id[str(first_LEO)][0:3] != 'LEO':
    first_LEO += 1 

input_file = 'extension_results_xLEO/contactPlan/contact_plan_7d_node-ids.txt'

# To iterate over the number of LEOS, GS and HAPS
for number_of_LEOS in number_of_LEOS_wanted:
    LEO_IDS_to_keep = [first_LEO + i for i in range(number_of_LEOS)]

    for number_of_GS in number_of_GS_wanted:
        GST_IDS_to_keep = [2 + 2*i for i in range(number_of_GS)]
        output_file = 'dtnsim/simulations/HAPS_Analysis/FilteredContactPlans/contact_plan_7d_node-ids_%sLEO_%sGS_%sSDR.txt' % (number_of_LEOS, number_of_GS, SDR)
        contact_filterer(input_file, output_file, LEO_IDS_to_keep, GST_IDS_to_keep, [])

    for number_of_HAGS_GS in number_of_HAGS_GS_wanted:
        GST_IDS_to_keep = [2 + 2*i for i in range(number_of_HAGS_GS)]
        HAPS_IDS_to_keep = [3 + 2*i for i in range(number_of_HAGS_GS)]
        output_file = 'dtnsim/simulations/HAPS_Analysis/FilteredContactPlans/contact_plan_7d_node-ids_%sLEO_%sHAP_%sGS_%sSDR.txt' % (number_of_LEOS, number_of_HAGS_GS, number_of_HAGS_GS, SDR)
        contact_filterer(input_file, output_file, LEO_IDS_to_keep, GST_IDS_to_keep, HAPS_IDS_to_keep)




#--------------------------------------- CREATE SIMULATION FILES ---------------------------------------#
# Create folders for the simulation with the filtered contact plans

FOLDERS_NAME = []
for number_of_LEOS in number_of_LEOS_wanted:
    for number_of_GS in number_of_GS_wanted:
        FOLDERS_NAME.append('%sLEO_%sGS_%sSDR' % (number_of_LEOS, number_of_GS, SDR))
    for number_of_HAGS_GS in number_of_HAGS_GS_wanted:
        FOLDERS_NAME.append('%sLEO_%sHAP_%sGS_%sSDR' % (number_of_LEOS, number_of_HAGS_GS, number_of_HAGS_GS, SDR))
       
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
        file.write("dtnsim.node[*].dtn.routing = \"cgrModel350\"\n")
        file.write("#dtnsim.node[*].dtn.routing = \"cgrModelRev17\"\n")
        file.write("dtnsim.node[*].dtn.routingType = \"routeListType:allPaths-firstDepleted,volumeAware:allContacts,extensionBlock:on,contactPlan:local\"\n")
        file.write("#dtnsim.node[*].dtn.printRoutingDebug=true\n")
        file.write("\n")
        file.write("dtnsim.central.contactsFile = \"../FilteredContactPlans/contact_plan_7d_node-ids_%s.txt\"\n" % (output_file_name))
        file.write("#dtnsim.node[*].dtn.saveBundleMap = true\n")
        file.write("#dtnsim.central.saveTopology = true\n")
        file.write("#dtnsim.central.saveFlows = true\n")
        file.write("#dtnsim.central.saveLpFlows = true\n")
        file.write("\n")
        file.write("# traffic generation\n")
        for i in range(number_of_LEOS):
            node_index = first_LEO + i
            file.write("dtnsim.node[%s].app.enable=true\n" % node_index)
            file.write("dtnsim.node[%s].app.bundlesNumber=\"%s\"\n" % (node_index, number_of_bundles))
            file.write("dtnsim.node[%s].app.start=\"0\"\n" % node_index)
            file.write("dtnsim.node[%s].app.destinationEid=\"1\"\n" % node_index)
            file.write("dtnsim.node[%s].app.size=\"100\"\n" % node_index)
        
        # Put the right SDR for the HAPS
        for i in range(number_of_HAGS_GS):
            node_index = 3 + 2*i
            file.write("dtnsim.node[%s].dtn.sdrSize=%s\n" % (node_index, SDR))

        file.write("#dtnsim.node[3].dtn.sdrSize = 9\n")
        file.write("\n")
        file.write("# Nodes's failure rates\n")
        file.write("dtnsim.node[*].fault.faultSeed = ${repetition}*100\n")
        file.write("dtnsim.node[*].fault.meanTTF = ${TTF=%s}\n" % ','.join([str(ttf)+'h' for ttf in TTF]))
        file.write("dtnsim.node[*].fault.meanTTR = ${TTR=%s}\n" % ','.join([str(ttr)+'h' for ttr in TTR]))
        file.write("\n")
        file.write("dtnsim.node[2].fault.enable = true\n")
        file.write("dtnsim.node[4].fault.enable = true\n")
        file.write("dtnsim.node[6].fault.enable = true\n")
        file.write("dtnsim.node[8].fault.enable = true\n")
        file.write("dtnsim.node[10].fault.enable = true\n")
        file.write("dtnsim.node[12].fault.enable = true\n")
        file.write("dtnsim.node[14].fault.enable = true\n")
        file.write("dtnsim.node[16].fault.enable = true\n")
        file.write("dtnsim.node[18].fault.enable = true\n")
        file.write("dtnsim.node[20].fault.enable = true\n")
        file.write("dtnsim.node[22].fault.enable = true\n")
        file.write("dtnsim.node[24].fault.enable = true\n")
        file.write("dtnsim.node[26].fault.enable = true\n")
        file.write("dtnsim.node[28].fault.enable = true\n")
        file.write("dtnsim.node[30].fault.enable = true\n")
        file.write("dtnsim.node[32].fault.enable = true\n")
        file.write("dtnsim.node[34].fault.enable = true\n")
        file.write("dtnsim.node[36].fault.enable = true\n")
        file.write("dtnsim.node[38].fault.enable = true\n")
        file.write("dtnsim.node[40].fault.enable = true\n")
        file.write("dtnsim.node[42].fault.enable = true\n")

# Create the script.sh file
for output_file_name in FOLDERS_NAME:
    with open('dtnsim/simulations/HAPS_Analysis/' + output_file_name + '/script.sh', 'w') as file:
        file.write("#!/bin/bash\n")
        file.write("\n")
        file.write("opp_runall -j8 ../../../dtnsim omnetpp.ini -n ../../../src -u Cmdenv -c General\n")
        file.write("\n")
        file.write(": <<'END'\n")
        file.write("END\n")


# Create the run.sh file
i = 0
nbFiles = len(number_of_GS_wanted) + len(number_of_HAGS_GS_wanted)
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