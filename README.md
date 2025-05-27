# dtnsim-support-hags-mdps

As this entire repository is still under development, some of the files may be useless or even broken. This document provides a brief overview of the repository.

## General architecture

- The _/dtnsim_ folder is the main simulator. The /src folder contains all the modules, and the /simulations folder contains all the .ini files.
- The _/documentation_ folder contains papers that has been published / in under review on the subject.
- The _/results_paper_ folder contains the results from the initial paper.
- The _/extension_results_xLEO_ folder is the extension we have been working on, containing multiple LEOs. We published a paper on this extension. It also contains the MDP part, which is still under development.

## Documentation folder overview

I have organised the documents in the order that I think is best for reading.

About HAGS:
- _Juan_Benoit__HAGS__Opportunities_and_Challenges__Magazine_ (AESM)_ : a magazine paper explaning the general opportunities and challenges.
- _A Novel Non-Terrestrial Networks Architecture_ : the initial paper presenting the architecture and some results
- _Benoit_Pablo_Juan_Jorge_Halim__Routing_in_All_Optical_LEO_Constellations_with_High_Altitude_Ground_Stations_ is the extention paper we wrote about multiple LEOs (and therefore including some routing)


About MDPs (these are general and are here to learn more about MDPs): 
- https://github.com/JuliaPOMDP/POMDPs.jl : the package we used for MDP simulation in this work. The online documentation and tutorials for this packages are very helpful for understanding MDPs and their implementation.
- _NTN Days_ : A presentation made for a conference with general explanation of the subject.
- _A Consise Intro to Dec-POMDPs_ : an interesting "introduction" to POMDPs.
- _Powell-Reinforcement-Learning-and-Stochastic-Optimization_ : some interesting insights into MDPs to further understand the concepts.

## Extension_results_xLEO overview (nothing MDPs related)

- _simulation_creator.py_ : to create .ini configuration files + .sh file to execute the simulation. I guess it's still working. 
- _simulation_creatorGUI.py_ : work in progress, not currently working (but maybe one day).
- _data_processing.py_ : to process the data from omnetpp simulations and put it in a .json file.
- _plot_processing.py_ : plot the data from the .json file.
- _data_json_ and  _plots_ have the results.


## dtnsim/simulations/HAPS_Analysis overview

Everything related to MDPs is stored in this folder. The current working file is _MDPs_LSS_ActionVector.jl_, _LSS_ standing for Large State Space. The files with _GPU_ and _Qlearning_ are not working. The last two are previous implementations.

The folders like _/1LEO_2HAP_2GS_*_ contain the scenarios we are working on. _EQ_ stands for Equal, _W_ on Weighted and _M_ for Markov. The first two directly refer to the routing schemes in the extension paper.

### General explanation

1) Scenario:

The scenario used is a 1 LEO – 2 HAGS – 2 GS network. The goal of the MDP is to determine which of the two HAGS is best for sending data. The input includes the probability of cloud coverage in each HAGS, the current state of the network, and the contact plan.

2) Markov in Julia

The MDP is solved using a Monte Carlo Tree Search to find a near-optimal solution by simulating the evolution of the network. This uses statistical behaviours that are more or less hard-coded in the Julia file. For each timestamp, the MDP has two parts: the first looks at the LEO-to-HAGS part, and the second transfers packets from HAGS to GS (see the transition function).

3) Link between Julia and Omnetpp:

The file _dtnsim/src/node/dtn/routing/MarkovRouting.cc_ makes the link between the .jl files and the Omnetpp simulations. In this file, _MDPsLSSActionVector.jl_ is called with the correct parameters, and the results are returned for use in Omnetpp.

4) Steps:

What has been done:
- Markov computation
- Link with Omnetpp simulations
- A scenario has been chosen.
- The weather can be changed for each iteration of the MDP.

What are the limitations?
- Not very well optimised (takes a long time to compute).
- I think the 'keep' action is still not implemented. I can work on this quickly if needed.
- We still don't have any good results to show.

5) Future work:

In my opinion, there is a some work left to be done to achieve good results, but the foundations are in place. We still need to define the MDP and its use in Omnetpp more precisely, and finally find something interesting to show by comparing this MDP routing scheme with heuristics such as Equal and Weighted distributions.
