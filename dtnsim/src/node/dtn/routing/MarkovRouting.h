#ifndef MARKOVROUTING_H
#define MARKOVROUTING_H

#include <vector>
#include "CgrRoute.h"
#include <sstream>
#include <numeric>
#include <unordered_map>
#include "RoutingDeterministic.h"
#include <src/node/dtn/Dtn.h>
#include <src/node/app/App.h>
#include <src/node/dtn/SdrModel.h>

namespace std {
    template <>
    struct hash<std::vector<int>> {
        size_t operator()(const std::vector<int>& v) const {
            std::hash<int> hasher;
            size_t seed = 0;
            for (int i : v) {
                seed ^= hasher(i) + 0x9e3779b9 + (seed << 6) + (seed >> 2);
            }
            return seed;
        }
    };
}

class MarkovRouting : public RoutingDeterministic {
public:
    MarkovRouting(int eid, SdrModel* sdr, ContactPlan* localContactPlan, int totalBundles, cModule* dtn,  string MeanTTF, string MeanTTR);
    ~MarkovRouting();
    void routeAndQueueBundle(BundlePkt* bundle, double simTime);
    void setBundlesInSdr(int bundNum);

private:
    int eid_;

    bool isStateInDictionary(const std::unordered_map<std::vector<int>, std::pair<std::string, double>>& dictionary, const std::vector<int>& state);
    double getQValue(const std::unordered_map<std::vector<int>, std::pair<std::string, double>>& dictionary, const std::vector<int>& state);
    string getAction(const std::unordered_map<std::vector<int>, std::pair<std::string, double>>& dictionary, const std::vector<int>& state);
    std::unordered_map<std::string, std::vector<int>> actionDictionary;

    cModule * dtn_;

    string MeanTTF_;
    string MeanTTR_;
    int maxBundlesThisNode;
};

#endif // MARKOVROUTING_H
