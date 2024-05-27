#ifndef SRC_NODE_DTN_ROUTING_RoutingCgrModelRev17Distribution_H_
#define SRC_NODE_DTN_ROUTING_RoutingCgrModelRev17Distribution_H_

#include <src/node/dtn/routing/CgrRoute.h>
#include <sstream>
#include <numeric>
#include <src/node/dtn/routing/RoutingDeterministic.h>

#define	MAX_SPEED_MPH	(150000)

class RoutingCgrModelRev17Distribution: public RoutingDeterministic {
public:
	RoutingCgrModelRev17Distribution(int eid, int nodeNum, SdrModel * sdr, ContactPlan * localContactPlan,
			ContactPlan * globalContactPlan, string routingType, bool printDebug, int numHags,
			string MeanTTF, string MeanTTR);
	virtual ~RoutingCgrModelRev17Distribution();
	virtual void routeAndQueueBundle(BundlePkt *bundle, double simTime);

	// stats recollection
	int getDijkstraCalls();
	int getDijkstraLoops();
	int getRouteTableEntriesCreated();
	int getRouteTableEntriesExplored();

	bool printDebug_ = true;

private:

	// Stats collection
	int dijkstraCalls;
	int dijkstraLoops;
	int tableEntriesCreated;
	int tableEntriesExplored;

	// Basic variables
	string routingType_;
	std::vector<int> distributionVector;
	int numHags_;
	int nodeNum_;
	double simTime_;

	void checkRoutingTypeString(void);

	// Route Table: one table per destination
	vector<vector<CgrRoute>> routeTable_;
	double routeTableLastEditTime = -1;

	typedef struct {
		Contact * predecessor;		// Predecessor Contact
		bool suppressed;			// Dijkstra exploration: suppressed
	} Work;

	void cgrForward(BundlePkt * bundle);
	void cgrEnqueue(BundlePkt * bundle, CgrRoute * bestRoute);


	void findNextBestRoute(vector<int> suppressedContactIds, int terminusNode, CgrRoute * route);

	void clearRouteTable();
	void printRouteTable(int terminusNode);
	static bool compareRoutes(CgrRoute i, CgrRoute j);
	void printContactPlan();
};

#endif /* SRC_NODE_DTN_ROUTING_ROUTINGCGRMODELREV17_H_ */
