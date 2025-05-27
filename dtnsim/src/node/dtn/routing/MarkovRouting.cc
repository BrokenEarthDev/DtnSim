#include <src/node/dtn/routing/MarkovRouting.h>
#include <unordered_map>
#include <sstream>
#include "MarkovRouting.h"
#include <fstream>
#include <string>
#include <vector>
#include <iostream>
#include <cmath>
#include "json.hpp"

int numberOfBundlesAlreadySent = 0;
// Create a dictionary to store the output
std::unordered_map<std::vector<int>, std::pair<std::string, double>> outputDict;

void loadJsonFileAndPopulateDict()
{
    std::cout << "Loading JSON file" << std::endl;
    // Load JSON file and populate outputDict
    std::ifstream inputFile("/home/benoitcoeugnet/git/dtnsim/dtnsim/simulations/HAPS_Analysis/policy.json");
    if (inputFile.is_open())
    {
        nlohmann::json jsonData;
        inputFile >> jsonData;
        inputFile.close();

        for (auto it = jsonData.begin(); it != jsonData.end(); ++it)
        {
            std::string key = it.key();
            std::stringstream ss(key.substr(1, key.size() - 2)); // Remove the square brackets
            std::vector<int> stateRead;
            int num;
            while (ss >> num)
            {
                stateRead.push_back(num);
                if (ss.peek() == ',')
                {
                    ss.ignore();
                }
            }

            std::string action = it.value()[0];
            double qValue = it.value()[1];
            // cout << "stateRead: " << stateRead[0] << " " << stateRead[1] << " " << stateRead[2] << " " << stateRead[3] << " " << stateRead[4] << endl;
            outputDict[stateRead] = std::make_pair(action, qValue);
        }
    }
    else
    {
        std::cerr << "Error opening JSON file." << std::endl;
    }
}

MarkovRouting::MarkovRouting(int eid, SdrModel *sdr, ContactPlan *localContactPlan, int totalBundles, cModule *dtn, string MeanTTF, string MeanTTR)
    : RoutingDeterministic(eid, sdr, NULL)
{
    maxBundlesThisNode = totalBundles;
    eid_ = eid;
    dtn_ = dtn;
    MeanTTF_ = MeanTTF;
    MeanTTR_ = MeanTTR;
    loadJsonFileAndPopulateDict();
}

MarkovRouting::~MarkovRouting()
{
}

bool MarkovRouting::isStateInDictionary(const std::unordered_map<std::vector<int>, std::pair<std::string, double>> &dictionary, const std::vector<int> &state)
{
    cout << "Checking if state is in dictionary" << endl;
    cout << "State: " << state[0] << " " << state[1] << " " << state[2] << " " << state[3] << " " << state[4] << endl;
    for (const auto &entry : dictionary)
    {
        const std::vector<int> &dictState = entry.first;
        bool isEqual = true;
        for (int i = 0; i < 4; i++)
        {
            if (dictState[i] != state[i])
            {
                isEqual = false;
                break;
            }
        }
        if (isEqual)
        {
            return true;
        }
    }
    return false;
}

double MarkovRouting::getQValue(const std::unordered_map<std::vector<int>, std::pair<std::string, double>> &dictionary, const std::vector<int> &state)
{
    cout << "Getting Q value" << endl;
    cout << "State: " << state[0] << " " << state[1] << " " << state[2] << " " << state[3] << " " << state[4] << endl;
    for (const auto &entry : dictionary)
    {
        const std::vector<int> &dictState = entry.first;
        if (dictState.size() >= 4 && state.size() >= 4)
        {
            bool isEqual = true;
            for (int i = 0; i < 4; i++)
            {
                if (dictState[i] != state[i])
                {
                    isEqual = false;
                    break;
                }
            }
            if (isEqual)
            {
                return entry.second.second;
            }
        }
    }
    return 0.0; // Return 0 if the state is not found in the dictionary
}

std::string MarkovRouting::getAction(const std::unordered_map<std::vector<int>, std::pair<std::string, double>> &dictionary, const std::vector<int> &state)
{
    cout << "Getting action" << endl;
    cout << "State: " << state[0] << " " << state[1] << " " << state[2] << " " << state[3] << " " << state[4] << endl;
    for (const auto &entry : dictionary)
    {
        const std::vector<int> &dictState = entry.first;
        if (dictState.size() >= 4 && state.size() >= 4)
        {
            bool isEqual = true;
            for (int i = 0; i < 4; i++)
            {
                if (dictState[i] != state[i])
                {
                    isEqual = false;
                    break;
                }
            }
            if (isEqual)
            {
                return entry.second.first;
            }
        }
    }
    return ""; // Return an empty string if the state is not found in the dictionary
}

void MarkovRouting::routeAndQueueBundle(BundlePkt *bundle, double simTime)
{
    App *app = check_and_cast<App *>(dtn_->getParentModule()->getParentModule()->getSubmodule("node", this->eid_)->getSubmodule("app"));
    std::unordered_map<std::string, std::vector<int>> actionDictionary;
    // Create a dictionary to map the action to a route
    actionDictionary["[0,0,0]"] = {6, 0, 0};
    actionDictionary["[0,1,0]"] = {3, 2, 1};
    actionDictionary["[0,0,1]"] = {5, 4, 1};

    // If there are no next nodes, find the route in the json file or execute the Julia script
    if (bundle->nextNodeIDs.empty())
    {
        cout << "Empty route" << endl;
        // Get the number of bundles in the sdr
        int numBundlesThisNode = check_and_cast<Dtn *>(dtn_->getParentModule()->getParentModule()->getSubmodule("node", this->eid_)->getSubmodule("dtn"))->sdr_.getBundlesCountInSdr() + 1;
        int numBundlesNode3 = check_and_cast<Dtn *>(dtn_->getParentModule()->getParentModule()->getSubmodule("node", 3)->getSubmodule("dtn"))->sdr_.getBundlesCountInSdr();
        int numBundlesQueuedFor3 = check_and_cast<Dtn *>(dtn_->getParentModule()->getParentModule()->getSubmodule("node", 6)->getSubmodule("dtn"))->sdr_.getNumberOfBundlesToNode(3);
        int numBundlesNode5 = check_and_cast<Dtn *>(dtn_->getParentModule()->getParentModule()->getSubmodule("node", 5)->getSubmodule("dtn"))->sdr_.getBundlesCountInSdr();
        int numBundlesQueuedFor5 = check_and_cast<Dtn *>(dtn_->getParentModule()->getParentModule()->getSubmodule("node", 6)->getSubmodule("dtn"))->sdr_.getNumberOfBundlesToNode(5);
        int totalBundles = app->getBundlesNumberVec()[0];

        cout << "TotalBundles: " << totalBundles << endl;
        cout << "numBundlesQueuedFor3: " << numBundlesQueuedFor3 << ", numBundlesQueuedFor5: " << numBundlesQueuedFor5 << endl;
        // Get the simulation time
        int simulationTime = simTime / 100;

        cout << "NumBundlesThisNode: " << totalBundles - numberOfBundlesAlreadySent << ", NumBundlesNode3: " << numBundlesNode3 + numBundlesQueuedFor3 << ", NumBundlesNode5: " << numBundlesNode5 + numBundlesQueuedFor5 << ", SimulationTime: " << simulationTime << endl;

        // Define the state
        std::vector<int> state = {totalBundles - numberOfBundlesAlreadySent, numBundlesNode3 + numBundlesQueuedFor3, numBundlesNode5 + numBundlesQueuedFor5, simulationTime, 0};

        // Get the Q value from the dictionary
        double qValue = getQValue(outputDict, state);

        // If the state is not in the dictionary, execute the Julia script
        if (!isStateInDictionary(outputDict, state))
        {
            cout << "Not found or qValue is 0" << endl;

            cout << "MeanTTF: " << MeanTTF_ << ", MeanTTR: " << MeanTTR_ << endl;

            std::string command = "julia /home/benoitcoeugnet/git/dtnsim/dtnsim/simulations/HAPS_Analysis/MDPs_LSS_ActionVector.jl ";
            // Append the input parameters to the command
            command += std::to_string(totalBundles - numberOfBundlesAlreadySent) + " ";
            command += std::to_string(numBundlesNode3 + numBundlesQueuedFor3) + " ";
            command += std::to_string(numBundlesNode5 + numBundlesQueuedFor5) + " ";
            command += std::to_string(simulationTime) + " ";
            command += MeanTTF_ + " ";
            command += MeanTTR_;

            // Execute the command and retrieve the results
            std::string results = "";
            FILE *pipe = popen(command.c_str(), "r");
            if (pipe)
            {
                char buffer[16384];
                while (!feof(pipe))
                {
                    if (fgets(buffer, 16384, pipe) != NULL)
                        results += buffer;
                }
                pclose(pipe);
            }
        }

        loadJsonFileAndPopulateDict();

        // Print the dictionary
        // for (const auto& entry : outputDict) {
        //     std::cout << "State: ";
        //     for (const auto& stateValue : entry.first) {
        //         std::cout << stateValue << " ";
        //     }
        //     std::cout << ", Action: " << entry.second.first << ", Q Value: " << entry.second.second << std::endl;
        // }

        // Print the number of bundles in this sdr
        std::cout << "Bundle in sdr" << " " << numBundlesThisNode << std::endl;

        // Get the action from the dictionary
        std::string action = getAction(outputDict, state);

        cout << "Action: " << action << endl;

        // Create the route thanks to the actionDictionary
        bundle->nextNodeIDs = actionDictionary[action];
        //keep action
        // cout << "test keep action" << bundle->nextNodeIDs.at(0) == 6 << endl;
        if (bundle->nextNodeIDs.at(0) == 6) {
            app->keepAction();
            delete bundle;
        }
        else {
            if (bundle->nextNodeIDs.at(0) == 6)
            {
                app->keepAction();
                delete bundle;
            }
            // print the nextNodeIDs
            cout << "NextNodeIDs: " << bundle->nextNodeIDs.at(0) << " " << bundle->nextNodeIDs.at(1) << " " << bundle->nextNodeIDs.at(2) << endl;
            // Set the next hop for the bundle
            bundle->setNextHopEid(bundle->nextNodeIDs.at(0));
            // Enqueue the bundle to the next hop
            sdr_->enqueueBundleToNode(bundle, bundle->nextNodeIDs.at(0));

            // Increment the number of bundles already sent
            numberOfBundlesAlreadySent++;
        }
    }
    else
    { // If there is a route, pop the first hop and enqueue the bundle to the next hop
        cout << "Not empty route" << endl;
        // pop the first hop from the nextNodeIDs
        std::vector<int> nextNodeIDs = bundle->nextNodeIDs;
        nextNodeIDs.erase(nextNodeIDs.begin());
        nextNodeIDs.push_back(0);
        bundle->nextNodeIDs = nextNodeIDs;

        // Enqueue the bundle to the next hop
        cout << "NextNodeIDs: " << bundle->nextNodeIDs.at(0) << " " << bundle->nextNodeIDs.at(1) << " " << bundle->nextNodeIDs.at(2) << endl;
        bundle->setNextHopEid(bundle->nextNodeIDs.at(0));
        sdr_->enqueueBundleToNode(bundle, bundle->nextNodeIDs.at(0));
    }
}
