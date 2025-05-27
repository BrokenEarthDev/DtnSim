import os
import random
import json
import multiprocessing
import tkinter as tk
import tkinter.ttk as ttk
import style as style

class windows(tk.Tk):
    def __init__(self, *args, **kwargs):
        tk.Tk.__init__(self, *args, **kwargs)
        self.wm_title("Simulation generator")
        self.geometry("1000x1000")

        container = tk.Frame(self, height=1000, width=1000)
        container.pack(side="top", fill="both", expand=True)
        container.grid_rowconfigure(0, weight=1)
        container.grid_columnconfigure(0, weight=1)

        self.frames = {}
        for F in (MainPage,):
            frame = F(container, self)

            self.frames[F] = frame
            frame.grid(row=0, column=0, sticky="nsew")

        self.show_frame(MainPage)
    
    def show_frame(self, cont):
        frame = self.frames[cont]
        frame.tkraise()


class MainPage(tk.Frame):
    def __init__(self, parent, controller):
        with open("data.json", 'r') as file:
            data = json.load(file)
            self.leos_wanted = data.get('leos_wanted', 0)  
            self.gs_wanted = data.get('gs_wanted', 0)
            self.hags_gs_wanted = data.get('hags_gs_wanted', 0)
            self.repetitions = data.get('repetitions', 0)
            self.number_of_bundles = data.get('number_of_bundles', 0)
            self.distribution = data.get('distribution', 'greedy')
            self.TTR = data.get('TTR', 0)
            self.TTF = data.get('TTF', 0)
        # Frame and grid for the frame
        tk.Frame.__init__(self, parent)
        self.grid_rowconfigure(0, weight=1) 
        self.grid_columnconfigure(0, weight=1)

        # Scrollable canvas
        self.canvas = tk.Canvas(self)
        self.canvas.grid(row=0, column=0, sticky="news")
        self.vsb = ttk.Scrollbar(self, orient="vertical", command=self.canvas.yview)
        self.vsb.grid(row=0, column=6, sticky='ns')
        self.canvas.configure(yscrollcommand=self.vsb.set) 
        self.canvas.update_idletasks()
        self.canvas.config(scrollregion=self.canvas.bbox("all"))
        self.canvas.grid_columnconfigure((1,2,3,4,5,6), weight=1)

        # Button for the program
        self.bLaunch = ttk.Button(self.canvas, text="Launch the generator", command=main) # Button to launch the program
        self.bLaunch.grid(row=0, column=0, pady=20)
        self.bSave= ttk.Button(self.canvas, text="Save the config", command=self.save_to_json) # Button to save the config
        self.bSave.grid(row=0, column=1)
        self.bDelete = ttk.Button(self.canvas, text="Delete all the scenario folders", command=clean) # Button to delete all the scenario folders
        self.bDelete.grid(row=0, column=2)

        # Labels and entries for the parameters
        self.label_LEOS = ttk.Label(self.canvas, text="LEOs wanted:")
        self.label_LEOS.grid(row=1, column=0, padx=20, sticky="e")
        self.entry_LEOS = ttk.Entry(self.canvas)
        self.entry_LEOS.grid(row=1, column=1)
        self.entry_LEOS.insert(0, self.leos_wanted)

        self.label_GS = ttk.Label(self.canvas, text="GS wanted:")
        self.label_GS.grid(row=2, column=0, padx=20, sticky="e")
        self.entry_GS = ttk.Entry(self.canvas)
        self.entry_GS.grid(row=2, column=1)
        self.entry_LEOS.insert(0, self.gs_wanted)

        self.label_HAGS_GS = ttk.Label(self.canvas, text="HAGS-GS wanted:")
        self.label_HAGS_GS.grid(row=3, column=0, padx=20, sticky="e")
        self.entry_HAGS_GS = ttk.Entry(self.canvas)
        self.entry_HAGS_GS.grid(row=3, column=1)
        self.entry_HAGS_GS.insert(0, self.hags_gs_wanted)

        self.label_repetitions = ttk.Label(self.canvas, text="Number of repetitions:")
        self.label_repetitions.grid(row=4, column=0, padx=20, sticky="e")
        self.entry_repetitions = ttk.Entry(self.canvas)
        self.entry_repetitions.grid(row=4, column=1)
        self.entry_repetitions.insert(0, self.repetitions)

        self.label_number_of_bundles = ttk.Label(self.canvas, text="Number of bundles:")
        self.label_number_of_bundles.grid(row=6, column=0, padx=20, sticky="e")
        self.entry_number_of_bundles = ttk.Entry(self.canvas)
        self.entry_number_of_bundles.grid(row=6, column=1)
        self.entry_number_of_bundles.insert(0, self.number_of_bundles)

        self.label_distribution = ttk.Label(self.canvas, text="Distribution:")
        self.label_distribution.grid(row=7, column=0, padx=20, pady=20, sticky="e")
        self.combo_distribution = ttk.Combobox(self.canvas, values=["greedy", "equal", "weighted"])
        self.combo_distribution.grid(row=7, column=1)
        self.combo_distribution.set(self.distribution)

        self.label_TTR = ttk.Label(self.canvas, text="TTR:")
        self.label_TTR.grid(row=8, column=0, padx=20, sticky="e")
        self.text_TTR = tk.Text(self.canvas, height=5, width=30)
        self.text_TTR.insert('1.0', self.TTR)
        self.text_TTR.grid(row=8, column=1)
        self.text_TTR.bind("<Key>", self.adjust_text_TTR)
        self.text_TTR.bind("<FocusIn>", self.adjust_text_TTR)

        self.label_TTF = ttk.Label(self.canvas, text="TTF:")
        self.label_TTF.grid(row=9, column=0, padx=20, sticky="e")
        self.text_TTF = tk.Text(self.canvas, height=5, width=30)
        self.text_TTF.insert('1.0', self.TTF)
        self.text_TTF.grid(row=9, column=1)
        self.text_TTF.bind("<Key>", self.adjust_text_TTF)
        self.text_TTF.bind("<FocusIn>", self.adjust_text_TTF)

    def adjust_text_TTR(self, event=None):
        self.text_TTR.update_idletasks()
        new_height = min(20, max(6, int(self.text_TTR.count('1.0', 'end-1c', 'lines')[0])))
        new_width = min(30, max(10, int(self.text_TTR.count('1.0', 'end-1c', 'chars')[0])))
        self.text_TTR.config(height=new_height, width=new_width)

    def adjust_text_TTF(self, event=None):
        self.text_TTF.update_idletasks()
        new_height = min(20, max(6, int(self.text_TTF.count('1.0', 'end-1c', 'lines')[0])))
        new_width = min(30, max(10, int(self.text_TTF.count('1.0', 'end-1c', 'chars')[0])))
        self.text_TTF.config(height=new_height, width=new_width)

    def save_to_json(self, filename='data.json'):
        self.leos_wanted = self.entry_LEOS.get()
        self.gs_wanted = self.entry_GS.get()
        self.hags_gs_wanted = self.entry_HAGS_GS.get()
        self.repetitions = self.entry_repetitions.get()
        self.number_of_bundles = self.entry_number_of_bundles.get()
        self.distribution = self.combo_distribution.get()
        self.TTR = self.text_TTR.get("1.0", "end-1c")
        self.TTF = self.text_TTF.get("1.0", "end-1c")
        data = {
            'leos_wanted': self.leos_wanted,
            'gs_wanted': self.gs_wanted,
            'hags_gs_wanted': self.hags_gs_wanted,
            'repetitions': self.repetitions,
            'number_of_bundles': self.number_of_bundles,
            'distribution': self.distribution,
            'TTR': self.TTR,
            'TTF': self.TTF
        }
        with open(filename, 'w') as file:
            json.dump(data, file, indent=4) 


#-------------------------------------------- FILTERING OF THE CONTACT PLAN --------------------------------------------#
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
def clean():
    # Delete all the simulation files in dtnsim/simulations/HAPS_Analysis 
    os.system('rm -r dtnsim/simulations/HAPS_Analysis/source*')

    # Delete run.sh file
    os.system('rm dtnsim/simulations/HAPS_Analysis/run*')

    # Delete all the contact plans in dtnsim/simulations/HAPS_Analysis/FilteredContactPlans
    for file in os.listdir('dtnsim/simulations/HAPS_Analysis/FilteredContactPlans'):
        os.system('rm dtnsim/simulations/HAPS_Analysis/FilteredContactPlans/' + file)


#-------------------------------------------- MAIN --------------------------------------------#
def main():
    # Shareable parameters
    with open('data.json', 'r') as file:
        data = json.load(file)

    LEOS_wanted = [int(element) for element in data['leos_wanted'].split(",")]
    GS_wanted = [int(element) for element in data['gs_wanted'].split(",")]
    HAGS_GS_wanted = [int(element) for element in data['hags_gs_wanted'].split(",")]
    number_of_repetitions = int(data['repetitions'])
    cycle_source = 5
    SDR = 0

    # Specific parameters
    number_of_bundles = [int(element) for element in data['hags_gs_wanted'].split(",")]
    distribution = data['distribution']

    # TTR and TTF initialisation
    TTR = []
    cleaned_string = data['TTR'].strip("[]")
    print("cleaned_string", cleaned_string)
    elements = cleaned_string.split("],\n[")
    print("elements", elements)
    for elem in elements:
        TTR.append([float(e) for e in elem.split(",")])
    TTF = []
    cleaned_string = data['TTF'].strip("[]")
    elements = cleaned_string.split("],\n[")
    for elem in elements:
        TTF.append([float(e) for e in elem.split(",")])
    TTRinString, TTFinString = [], []

    # Link between the name of the node and its id
    name_to_id = {}
    with open('extension_results_xLEO/contactPlan/contact_plan_7d_name_to_id_mapping.txt', 'r') as file:
        for line in file:
            name, id = line.strip().split()
            name_to_id[id] = name


    if distribution == 'equal':
        TTR = [5,25]
        TTF = [0.1,0.2,0.5,1,2,5,10,15,20,25,30,35,40]  


    elif distribution == 'weighted':  
        # TTF = [[3.05,3.05,3.05,3.05,3.05],
        #        [2.95,3.0,3.05,3.1,3.15],
        #         [2.85,2.95,3.05,3.15,3.25],
        #         [2.75,2.9,3.05,3.2,3.35],
        #         [2.65,2.85,3.05,3.25,3.45],
        #         [2.55,2.8,3.05,3.3,3.55],
        #         [2.45,2.75,3.05,3.35,3.65],
        #         [2.35,2.7,3.05,3.4,3.75],
        #         [2.25,2.65,3.05,3.45,3.85],
        #         [2.15,2.6,3.05,3.5,3.95],
        #         [2.05,2.55,3.05,3.55,4.05]
        #        ]
        
        for i in range(len(TTF)):
            ttrInString,ttfInString = '',''
            for hags_gs in range(len(HAGS_GS_wanted)):
                ttrInString += str(TTR[i][hags_gs]) + '_'
                ttfInString += str(TTF[i][hags_gs]) + '_'

            TTRinString += [ttrInString[:-1] ]
            TTFinString += [ttfInString[:-1]]

        # print(TTFinString)

    input_file = 'extension_results_xLEO/contactPlan/contact_plan_7d_node-ids.txt'



    #--------------------------------------- FILTERING THE CONTACT PLAN ---------------------------------------#
    if len(TTF) == 1:
        for LEOS in LEOS_wanted:
            for GS in GS_wanted:
                output_file = 'dtnsim/simulations/HAPS_Analysis/FilteredContactPlans/contact_plan_7d_node-ids_%sLEO_%sGS.txt' % (number_of_LEOS, number_of_GS)
                contact_filterer(input_file, output_file, LEOS_wanted, GS_wanted, [])

            for HAGS_GS in HAGS_GS_wanted:
                GST_IDS_to_keep = [element - 1 for element in HAGS_GS_wanted]
                output_file = 'dtnsim/simulations/HAPS_Analysis/FilteredContactPlans/contact_plan_7d_node-ids_%sLEO_%sHAP_%sGS.txt' % (number_of_LEOS, number_of_HAGS_GS, number_of_HAGS_GS)
                contact_filterer(input_file, output_file, LEOS_wanted, GST_IDS_to_keep, HAGS_GS_wanted)   

    else:
        def process_filtering(input_file, output_file, LEO_IDS_to_keep, GST_IDS_to_keep, HAPS_IDS_to_keep):
            contact_filterer(input_file, output_file, LEO_IDS_to_keep, GST_IDS_to_keep, HAPS_IDS_to_keep)

        if __name__ == '__main__':
            processes = []
            for i in range(len(TTF)):
                for LEOS in LEOS_wanted:
                    for number_of_GS in GS_wanted:
                        output_file = 'dtnsim/simulations/HAPS_Analysis/FilteredContactPlans/contact_plan_7d_node-ids_%sLEO_%sGS.txt' % (number_of_LEOS, number_of_GS)
                        p = multiprocessing.Process(target=process_filtering, args=(input_file, output_file, LEOS_wanted, GST_IDS_to_keep, []))
                        processes.append(p)
                        p.start()

                    for HAGS_GS in HAGS_GS_wanted:
                        GST_IDS_to_keep = [element - 1 for element in HAGS_GS_wanted]
                        output_file = 'dtnsim/simulations/HAPS_Analysis/FilteredContactPlans/contact_plan_7d_node-ids_%sLEO_%sHAP_%sGS.txt' % (number_of_LEOS, number_of_HAGS_GS, number_of_HAGS_GS)
                        # output_file = 'dtnsim/simulations/HAPS_Analysis/FilteredContactPlans/contact_plan_7d_node-ids_paper'
                        p = multiprocessing.Process(target=process_filtering, args=(input_file, output_file, LEOS_wanted, GST_IDS_to_keep, HAGS_GS_wanted))
                        processes.append(p)
                        p.start()

            for process in processes:
                process.join()


    #--------------------------------------- CREATE SIMULATION FILES ---------------------------------------#
    # Create folders for the simulation 
    FOLDERS_NAME = []
    if len(TTF) == 1:
        for LEOS in LEOS_wanted:
            for GS in GS_wanted:
                FOLDERS_NAME.append('%sLEO_%sGS' % (LEOS, GS))
            for HAGS_GS in HAGS_GS_wanted:
                FOLDERS_NAME.append('%sLEO_%sHAP_%sGS_EQ' % (LEOS, HAGS_GS, HAGS_GS))

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

                file.write("dtnsim.node[*].dtn.routingType = \"routeListType:allPaths-firstDepleted,volumeAware:allContacts,extensionBlock:on,contactPlan:local,distribution:weighted,sdrModel:perNode\"\n")
                file.write("#dtnsim.node[*].dtn.printRoutingDebug=true\n")
                file.write("\n")
                file.write("dtnsim.central.contactsFile = \"../FilteredContactPlans/contact_plan_7d_node-ids_%s.txt\"\n" % (output_file_name))
                file.write("#dtnsim.node[*].dtn.saveBundleMap = true\n")
                file.write("#dtnsim.central.saveTopology = true\n")
                file.write("#dtnsim.central.saveFlows = true\n")
                file.write("#dtnsim.central.saveLpFlows = true\n")
                file.write("\n")
                file.write("# traffic generation\n")
                for LEOS in LEOS_wanted:
                    file.write("dtnsim.node[%s].app.enable=true\n" % LEOS)
                    file.write("dtnsim.node[%s].app.bundlesNumber=\"%s\"\n" % (LEOS, number_of_bundles[LEOS_wanted.index(LEOS)]))
                    file.write("dtnsim.node[%s].app.start=\"0\"\n" % LEOS)
                    file.write("dtnsim.node[%s].app.destinationEid=\"1\"\n" % LEOS)
                    file.write("dtnsim.node[%s].app.size=\"100\"\n" % LEOS)
                
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

    else:
        for source in range(cycle_source):
            for i in range(len(TTF)):
                for LEOS in LEOS_wanted:
                    for GS in GS_wanted:
                        FOLDERS_NAME.append('%sLEO_%sGS' % (LEOS, GS))
                    for HAGS_GS in HAGS_GS_wanted:
                        FOLDERS_NAME.append('source=%s_%s_%sLEO_%sHAP_%sGS_TTF_%s' % (str(44+source), name, LEOS, HAGS_GS, HAGS_GS, TTFinString[i]))

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
                ttf_index = output_file_name.find("TTF_")
                ttf_string = output_file_name[ttf_index + 4:]
                file.write("dtnsim.node[*].dtn.MeanTTF = \"%s\"\n" % ttf_string)
                file.write("dtnsim.node[*].dtn.MeanTTR = \"%s\"\n" % TTRinString[0])

                file.write("dtnsim.node[*].dtn.routingType = \"routeListType:allPaths-firstDepleted,volumeAware:allContacts,extensionBlock:on,contactPlan:local,distribution:%s,sdrModel:perNode\"\n" % name)
                file.write("#dtnsim.node[*].dtn.printRoutingDebug=true\n")
                file.write("\n")
                file.write("dtnsim.central.contactsFile = \"../FilteredContactPlans/contact_plan_7d_node-ids_paper.txt\" \n")

                file.write('dtnsim.node[%s].app.enable=true\n' % output_file_name[7:9])
                file.write('dtnsim.node[%s].app.bundlesNumber="%s"\n' % (output_file_name[7:9], number_of_bundles))
                file.write('dtnsim.node[%s].app.start="0"\n' % output_file_name[7:9])
                file.write('dtnsim.node[%s].app.destinationEid="1"\n' % output_file_name[7:9])
                file.write('dtnsim.node[%s].app.size="100"\n' % output_file_name[7:9])

                file.write("\n")
                file.write("# Nodes's failure rates\n")
                ttf_string_tab = ttf_string.split('_')
                for j in range(5):
                    file.write("dtnsim.node[%s].fault.faultSeed = ${repetition}*100\n" % str(j*2+2))
                    file.write("dtnsim.node[%s].fault.meanTTF = %sh\n" % (j*2+2, ttf_string_tab[j]))
                    file.write("dtnsim.node[%s].fault.meanTTR = %sh\n" % (j*2+2, TTR[0][0]))
                file.write("\n")
                file.write("\n".join([f"dtnsim.node[{i}].fault.enable = true" for i in range(2, 2*5+2, 2)]))
            i+=1

    # Create the script.sh file
    for output_file_name in FOLDERS_NAME:
        with open('dtnsim/simulations/HAPS_Analysis/' + output_file_name + '/script.sh', 'w') as file:
            file.write("#!/bin/bash\n")
            file.write("\n")
            file.write("opp_runall -b1 -j1 ../../../dtnsim omnetpp.ini -n ../../../src -u Cmdenv -c General \n")
            file.write("\n")
            file.write(": <<'END'\n")
            file.write("END\n")


    # Create the run.sh file
    if len(TTF) == 1:
        for LEOS in LEOS_wanted: 
            for output_file_name in FOLDERS_NAME:     
                if output_file_name[0] == str(LEOS): 
                    with open('dtnsim/simulations/HAPS_Analysis/run%sLEOS.sh' % LEOS, 'w') as file:
                        file.write("#!/bin/bash\n\n")
                        file.write("cd %s\n" % output_file_name)
                        file.write("chmod +x script.sh\n") 
                        file.write("./script.sh &\n")
                        file.write("cd ..\n\n")

            with open('dtnsim/simulations/HAPS_Analysis/run%sLEOS.sh' % LEOS, 'a') as file:
                file.write("\nwait\n")

    else:
        for LEOS in LEOS_wanted:
            for output_file_name in FOLDERS_NAME:
                if output_file_name[7:9] == str(LEOS):
                    with open('dtnsim/simulations/HAPS_Analysis/run%sLEOS.sh' % LEOS, 'w') as file:
                        file.write("#!/bin/bash\n\n")
                        file.write("cd %s\n" % output_file_name)
                        file.write("chmod +x script.sh\n") 
                        file.write("./script.sh &\n")
                        file.write("cd ..\n\n")

            with open('dtnsim/simulations/HAPS_Analysis/run%sLEOS.sh' % LEOS, 'a') as file:
                file.write("\nwait\n")


if __name__ == "__main__":
    testObj = windows()
    testObj.mainloop()



