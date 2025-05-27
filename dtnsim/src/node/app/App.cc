#include "src/node/app/App.h"

Define_Module (App);



void App::initialize()
{
	this->numberOfBundlesScheduledThisTime = 0;
	// Store this node eid
	this->eid_ = this->getParentModule()->getIndex();

	// Configure Traffic Generator
	if (par("enable"))
	{
		const char *bundlesNumberChar = par("bundlesNumber");
		cStringTokenizer bundlesNumberTokenizer(bundlesNumberChar, ",");
		while (bundlesNumberTokenizer.hasMoreTokens())
			bundlesNumberVec_.push_back(atoi(bundlesNumberTokenizer.nextToken()));

		const char *destinationEidChar = par("destinationEid");
		cStringTokenizer destinationEidTokenizer(destinationEidChar, ",");
		while (destinationEidTokenizer.hasMoreTokens())
		{
			string destinationEidStr = destinationEidTokenizer.nextToken();
			int destinationEid = stoi(destinationEidStr);
			if (destinationEid > this->getParentModule()->getVectorSize())
			{
				throw cException((string("Error: wrong destinationEid = ") + destinationEidStr).c_str());
			}
			destinationEidVec_.push_back(destinationEid);
		}

		const char *sizeChar = par("size");
		cStringTokenizer sizeTokenizer(sizeChar, ",");
		while (sizeTokenizer.hasMoreTokens())
			sizeVec_.push_back(atoi(sizeTokenizer.nextToken()));

		const char *startChar = par("start");
		cStringTokenizer startTokenizer(startChar, ",");
		while (startTokenizer.hasMoreTokens())
			startVec_.push_back(atof(startTokenizer.nextToken()));

		if ((bundlesNumberVec_.size() != destinationEidVec_.size()) || (bundlesNumberVec_.size() != sizeVec_.size() || (bundlesNumberVec_.size() != startVec_.size())))
		{
            string str1 = "Error in App Traffic: Node[" + to_string(this->getParentModule()->getIndex()) + "]" + ", bundlesNumberVec, destinationEidVec, sizeVec, startVec: Sizes Missmatch!";
            throw cException((str1).c_str());
		}

		for (unsigned int i = 0; i < bundlesNumberVec_.size(); i++)
		{
			// Create the traffic generator message and store the pointer in a member variable
			this->trafficGenMsgPtr = new TrafficGeneratorMsg("trafGenMsg");
			TrafficGeneratorMsg * trafficGenMsg = this->trafficGenMsgPtr;
			trafficGenMsg->setSchedulingPriority(TRAFFIC_TIMER);
			trafficGenMsg->setKind(TRAFFIC_TIMER);
			trafficGenMsg->setBundlesNumber(bundlesNumberVec_.at(i));
			trafficGenMsg->setDestinationEid(destinationEidVec_.at(i));
			trafficGenMsg->setSize(sizeVec_.at(i));
			trafficGenMsg->setInterval(par("interval"));
			trafficGenMsg->setTtl(par("ttl"));
			scheduleAt(startVec_.at(i), trafficGenMsg);
		}
	}

	//@NANDO: DUMMY CODE FOR GENERATE TRAFFIC
	string externalEventsFile = par("externalTrafficEvents");
	if(externalEventsFile.compare("") != 0)
	{
		double ts;
		string name;
		char c;
		int from, to;
		string size;

		ifstream infile(externalEventsFile);
		while (infile >> ts >> c >> name >> from >> to >> size){
			if( from+1 == this->eid_)
			{
				TrafficGeneratorMsg * trafficGenMsg = new TrafficGeneratorMsg("trafGenMsg");
				trafficGenMsg->setSchedulingPriority(TRAFFIC_TIMER);
				trafficGenMsg->setKind(TRAFFIC_TIMER);
				trafficGenMsg->setBundlesNumber(1);
				trafficGenMsg->setDestinationEid(to+1);
				trafficGenMsg->setSize(pow(10,6));
				//trafficGenMsg->setInterval(par("interval").doubleValue());
				trafficGenMsg->setTtl(10000);
				scheduleAt(ts, trafficGenMsg);
			}
		}
	}
	//@NANDO: END DUMMY CODE FOR GENERATE TRAFFIC

	// Register signals
	appBundleSent = registerSignal("appBundleSent");
	appBundleReceived = registerSignal("appBundleReceived");
	appBundleReceivedHops = registerSignal("appBundleReceivedHops");
	appBundleReceivedDelay = registerSignal("appBundleReceivedDelay");
}

void App::handleMessage(cMessage *msg)
{
	if (msg->getKind() == TRAFFIC_TIMER)
	{
		TrafficGeneratorMsg* trafficGenMsg = check_and_cast<TrafficGeneratorMsg *>(msg);
		BundlePkt* bundle = new BundlePkt("bundle", BUNDLE);
		bundle->setSchedulingPriority(BUNDLE);

		// Bundle properties
		char bundleName[200];
		sprintf(bundleName, "Src:%d,Dst:%d(id:%d)", (int)this->eid_, (int)trafficGenMsg->getDestinationEid(), (int) bundle->getId());
		bundle->setBundleId(bundle->getId());
		bundle->setName(bundleName);
		bundle->setBitLength(trafficGenMsg->getSize() * 8);
		bundle->setByteLength(trafficGenMsg->getSize());

		// Bundle fields (set by source node)
		bundle->setSourceEid(this->eid_);
		bundle->setDestinationEid(trafficGenMsg->getDestinationEid());
		bundle->setReturnToSender(par("returnToSender"));
		bundle->setCritical(par("critical"));
		bundle->setCustodyTransferRequested(par("custodyTransfer"));
		bundle->setTtl(trafficGenMsg->getTtl());
		bundle->setCreationTimestamp(simTime());
		bundle->setQos(2);
		bundle->setBundleIsCustodyReport(false);

		// Bundle meta-data (set by intermediate nodes)
		bundle->setHopCount(0);
		bundle->setNextHopEid(0);
		bundle->setSenderEid(0);
		bundle->setCustodianEid(this->eid_);
		bundle->getVisitedNodesForUpdate().clear();
		CgrRoute emptyRoute;
		emptyRoute.nextHop = EMPTY_ROUTE;
		bundle->setCgrRoute(emptyRoute);

		Dtn *dtn = check_and_cast<Dtn *>(this->getParentModule()->getParentModule()->getSubmodule("node", this->eid_)->getSubmodule("dtn"));
		int bundlesInSdr = dtn->sdr_.getBundlesCountInSdr();

		cout << "bundlesInSdr: " << bundlesInSdr << endl;

		// Keep generating traffic
		trafficGenMsg->setBundlesNumber((trafficGenMsg->getBundlesNumber() - 1));
		if (trafficGenMsg->getBundlesNumber() == 0)
			delete msg;
		else
		{
			if (par("delay")) // schedule for next time
			{
				cout << "delay: " << par("delay") << endl;
				cout << "numberOfBundlesScheduledThisTime: " << this->numberOfBundlesScheduledThisTime << endl;
				if (bundlesInSdr + this->numberOfBundlesScheduledThisTime < 1) {
					cout << "Less than 2 bundles will be in Dtn this time" << endl;
					scheduleAt(simTime() + trafficGenMsg->getInterval(), msg);
				} 
				else {
					cout << "2 bundles already in Dtn or scheduled to be sent to dtn" << endl;
					scheduleAt(simTime() + 100 + trafficGenMsg->getInterval(), msg);
				}
			}
			else
			{
				cout << "delay: " << par("delay") << endl;
				scheduleAt(simTime() + trafficGenMsg->getInterval(), msg);
			}
		}

		if (par("delay"))
			if (bundlesInSdr + this->numberOfBundlesScheduledThisTime < 2) {
				cout << "bundleInSdr: " << bundlesInSdr << " " << ", simTime: " << simTime() << " " << " => Bundle sent" << endl;
				this->numberOfBundlesScheduledThisTime ++;
				send(bundle, "gateToDtn$o");
				emit(appBundleSent, true);
			}
			else
			{
				trafficGenMsg->setBundlesNumber((trafficGenMsg->getBundlesNumber() + 1));
				cancelEvent(msg);
				cout << bundlesInSdr << " " << simTime() << " " << "Bundle resheduled" << endl;
				scheduleAt(simTime() + 100 + trafficGenMsg->getInterval(), msg);
				delete bundle;
			}
		else
		{
			cout << "simTime: " << simTime() << " " << " => Bundle sent" << endl;
			send(bundle, "gateToDtn$o");
			emit(appBundleSent, true);
		}
		return;
	}
	else if (msg->getKind() == BUNDLE)
	{
		BundlePkt* bundle = check_and_cast<BundlePkt *>(msg);
		int destinationEid = bundle->getDestinationEid();

		if (this->eid_ == destinationEid)
		{
			emit(appBundleReceived, true);
			emit(appBundleReceivedHops, bundle->getHopCount());
			emit(appBundleReceivedDelay, simTime() - bundle->getCreationTimestamp());
			delete msg;
		}
		else
		{
			throw cException("Error: message received in wrong destination");
		}
	}
}

// function called by MarkovRouting to increase by one the number of bundles 
// that needed to be generated, simuling the fact that a bundle is keeped in the SDR 
void App::keepAction()
{
	this->trafficGenMsgPtr->setBundlesNumber((trafficGenMsgPtr->getBundlesNumber() + 1));
}

void App::finish()
{

}

App::App()
{

}

App::~App()
{

}

int App::getEid() const
{
	return eid_;
}

vector<int> App::getBundlesNumberVec()
{
	return this->bundlesNumberVec_;
}

vector<int> App::getDestinationEidVec()
{
	return this->destinationEidVec_;
}

vector<int> App::getSizeVec()
{
	return this->sizeVec_;
}

vector<double> App::getStartVec()
{
	return this->startVec_;
}
