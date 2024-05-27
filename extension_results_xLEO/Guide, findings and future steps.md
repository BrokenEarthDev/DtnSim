# Guide, findings and future steps

This document provides a guide to the use of the code, an explanation of the results and an overview of future steps by a given date.

## Guide

The results can be found in the *plots* folder. In each of them there is a README with all the parameters used to get these results.

\
The simulation_creator.py file has the following functions : 
	
- Delete each simulation file at the beginning (line 62) (**Commented by default**)
- The possibility to choose how many LEOS, GS and HAGS to use (line 87)
- Create all the .ini AND script.sh to run all the repetitions of a simulation.
- The creation of a run.sh to execute all the scripts.sh (in /HAGS_Analysis)

\
The data_processing.py file has the following functions: 

- Retrieve the data from the Omnetpp simulations
- Process this data to store it in a .json file 

\
The plot_processing.py file has the following functions:

- Automatically create all the plots for all the selected simulations.

\
To run the simulations :

- run simulation_creator.py
- run runxLEO.sh
- wait :)
- run data_processing.py
- run plot_processing.py
- View the results in extension_results_xLEO/plots

\
To launch runxLEO.sh, you need to do : 
```
cd dtnsim/simulations/HAPS_Analysis/
chmod +x runLEOS.sh
/runLEOS.sh
```
Don't forget to add the right file name.

**Note 1** : In the simulation_creator.py file, there are parameters that you can copy and paste into the other documents to match the parameters (named as *shareable parameters* at line 86) \
**Note 2** : In total there are 21 HAGS/GS and 66 LEOs.\
**Note 3** : Python scripts are bound to evolve and adapt, and some lines or explanations may become incorrect.


# Findings
An explanation of what we have been working on.

## RunTest1 (first extension)

The difference between these results and those in the *results_paper* folder is that the LEOs and HAGS/GS are now taken in their order in the simulation. So even if there are 5 LEOs, GS from 1 to 5 will be taken with LEOs from 44 to 48. This was done to be reproducible and to show the progress of having multiple LEOs. Also, the ISLs are activated, which means that the full potential of the network is visible (this will be impossible if the LEOs are not close to each other, as there are only links to the 4 nearest neighbours).

But with 2 and 5 LEOs, we see that the curves in the delivery ratio intersect (for some unknown reason). This seems strange because, as we said, we are adding HAGS/GS to the existing ones, so at least the bundles can follow the same path as with less HAGS/GS. 

Also, there is a plateau at 60% for 5 LEOs and 10 GS. This could be a bug, but we can't be sure. 


## RunTest2 (weird with cgrModelRev17)

We test with 33 LEOs to see if we can get usable data. But it was unusable because it was capped at 25% for some unknown reason. But we saw that the delivery ratio was better for the HAGS-GS configuration.


## RunTest3 (33 LEOs CGRmodel350)

New results with cgrModel350 and 33 LEOs (half of all available LEOs) which seem very promising : with 1 HAGS-GS it is possible to reach 5 times the delivery ratio of 1 GS..

## RunTest4 (1 and 2 LEOs CGRmodel350)

Show that the issue came from cgrModelRev17, because now with CGRmodel350 all is fine.

## RunTest5 (Influence of SDR size in HAGS)
We cleary see that having a

## RunTest6 (Influence of ISL)


# Future steps

## Agenda
- We need to address the issue of a slow start to a simulation, especially as we increase the number of LEOs.
- We need to test with different SDR size in HAGS and GS to see the congestion and how CGR deals with it.
- Compare the in


### SDR size test
Simulations are done with the following parameters :

- TTR : 5/25
- TTF : 0.1/0.2/0.5/1/2/5/10/15/20/25/30/35/40
- number of LEOS : 1
- number of GS : 1/5/10
- number of HAGS-GS : 1/3/5
- number of repetitions : 20
- SDR : 0 (infinite)/100/200/500

Graphs shows : 
- for a given topology, the influence of the SDR
- for a given SDR, how it impact different topologies



### Intersecting curves issue
The following items have been tested:

- Not a question of hops, admittedly there are many hops of a single bundle, but it doesn't depend on the number of HAGS/GS in the simulation.
- It was in fact an issue due to the version of CGR.






