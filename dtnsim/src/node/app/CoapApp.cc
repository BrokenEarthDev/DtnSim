#include "src/node/app/CoapApp.h"
Define_Module(CoapApp);

CoapApp::CoapApp() {}
CoapApp::~CoapApp() { cancelAndDelete(retxTimer_); }

void CoapApp::initialize()
{
    eid_ = getParentModule()->getIndex();
    role_ = par("role").stringValue();

    coapSent = registerSignal("coapSent");
    coapAcked = registerSignal("coapAcked");
    coapRetransmitted = registerSignal("coapRetransmitted");
    coapFailed = registerSignal("coapFailed");
    coapRoundTripDelay = registerSignal("coapRoundTripDelay");

    if (par("enable") && role_ == "sender")
        scheduleAt(par("start"), new cMessage("start", TRAFFIC_TIMER));
}

void CoapApp::sendCoapMessage()
{
    BundlePkt* bundle = new BundlePkt("coapBundle", BUNDLE);
    bundle->setSchedulingPriority(BUNDLE);
    bundle->setBundleId(bundle->getId());
    bundle->setBitLength(par("size").intValue() * 8);
    bundle->setByteLength(par("size"));
    bundle->setSourceEid(eid_);
    bundle->setDestinationEid(par("destinationEid"));
    bundle->setCreationTimestamp(simTime());
    bundle->setTtl(1e6);
    bundle->setCustodyTransferRequested(false);  // reliability is CoAP's job here, not BP's
    bundle->setCritical(false);
    bundle->setReturnToSender(false);
    bundle->setQos(2);
    bundle->setBundleIsCustodyReport(false);
    bundle->setHopCount(0);
    bundle->setNextHopEid(0);
    bundle->setSenderEid(0);
    bundle->setCustodianEid(eid_);
    bundle->getVisitedNodes().clear();
    CgrRoute emptyRoute; emptyRoute.nextHop = EMPTY_ROUTE;
    bundle->setCgrRoute(emptyRoute);

    bundle->setCoapMessageId(pendingMessageId_);
    bundle->setCoapToken(pendingMessageId_);
    bundle->setCoapType(par("confirmable") ? COAP_CON : COAP_NON);
    bundle->setCoapPayloadLength(par("size"));

    send(bundle, "gateToDtn$o");
    emit(coapSent, true);

    if (par("confirmable"))
    {
        retxTimer_ = new cMessage("coapRetx", COAP_RETX_TIMER);
        scheduleAt(simTime() + par("ackTimeout").doubleValue(), retxTimer_);
    }
}

void CoapApp::handleMessage(cMessage* msg)
{
    if (msg->getKind() == TRAFFIC_TIMER)
    {
        pendingMessageId_ = nextMessageId_++;
        retxCount_ = 0;
        sendCoapMessage();
        delete msg;
    }
    else if (msg->getKind() == COAP_RETX_TIMER)
    {
        retxCount_++;
        if (retxCount_ > par("maxRetransmit").intValue()) { emit(coapFailed, true); }
        else { emit(coapRetransmitted, true); sendCoapMessage(); }
        delete msg;
        retxTimer_ = nullptr;
    }
    else if (msg->getKind() == BUNDLE)
    {
        handleIncomingBundle(check_and_cast<BundlePkt*>(msg));
    }
}

void CoapApp::handleIncomingBundle(BundlePkt* bundle)
{
    if (bundle->getCoapType() == COAP_ACK)
    {
        if (retxTimer_) { cancelAndDelete(retxTimer_); retxTimer_ = nullptr; }
        emit(coapAcked, true);
        emit(coapRoundTripDelay, simTime() - bundle->getCreationTimestamp());
    }
    else if (bundle->getCoapType() == COAP_CON)
    {
        BundlePkt* ack = new BundlePkt("coapAck", BUNDLE);
        ack->setSchedulingPriority(BUNDLE);
        ack->setBundleId(ack->getId());
        ack->setBitLength(8); ack->setByteLength(1);
        ack->setSourceEid(eid_);
        ack->setDestinationEid(bundle->getSourceEid());
        ack->setCreationTimestamp(bundle->getCreationTimestamp()); // preserved so the sender can compute RTT
        ack->setTtl(1e6);
        ack->setCustodyTransferRequested(false);
        ack->setCritical(false); ack->setReturnToSender(false);
        ack->setQos(2); ack->setBundleIsCustodyReport(false);
        ack->setHopCount(0); ack->setNextHopEid(0); ack->setSenderEid(0);
        ack->setCustodianEid(eid_);
        ack->getVisitedNodes().clear();
        CgrRoute er; er.nextHop = EMPTY_ROUTE; ack->setCgrRoute(er);
        ack->setCoapMessageId(bundle->getCoapMessageId());
        ack->setCoapToken(bundle->getCoapToken());
        ack->setCoapType(COAP_ACK);
        ack->setCoapPayloadLength(0);
        send(ack, "gateToDtn$o");
    }
    delete bundle;
}

void CoapApp::finish() {}
