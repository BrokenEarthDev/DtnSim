#ifndef COAPAPP_H_
#define COAPAPP_H_

#include <omnetpp.h>
#include "src/node/MsgTypes.h"
#include "src/dtnsim_m.h"

using namespace omnetpp;
using namespace std;

#define COAP_CON 0
#define COAP_NON 1
#define COAP_ACK 2

class CoapApp : public cSimpleModule
{
    public:
        // Constructor -- OMNeT++ requires this even when empty; real setup happens in initialize().
        CoapApp();

        // Destructor -- cancels and frees the retransmit timer if one is still pending when the module is destroyed.
        virtual ~CoapApp();

    protected:
        // Called once at simulation startup. Reads this node's role ("sender"/"receiver") and,
        // if it's an enabled sender, schedules the first outgoing CoAP message at the configured start time.
        virtual void initialize();

        // Main event dispatcher. Three cases: (1) the traffic-start timer fires -> send the first message,
        // (2) the retransmit timer fires -> resend or give up past maxRetransmit, (3) a bundle arrived from
        // Dtn -> hand it to handleIncomingBundle().
        virtual void handleMessage(cMessage *msg);

        // Called once at simulation end. No cleanup needed here -- signals already recorded results live.
        virtual void finish();

    private:
        int eid_;
        string role_;
        int nextMessageId_ = 0;
        int pendingMessageId_ = 0;
        int retxCount_ = 0;
        cMessage* retxTimer_ = nullptr;

        // Builds one CoAP-carrying bundle (CON or NON per the "confirmable" parameter) and sends it
        // to Dtn like any normal bundle. If confirmable, also arms the ack-timeout retransmit timer.
        void sendCoapMessage();

        // Processes a bundle received from Dtn. If it's an ACK, this node was the sender -- cancel the
        // retransmit timer and record the round-trip delay. If it's a CON, this node is the receiver --
        // build and send back an ACK bundle carrying the same messageId/token.
        void handleIncomingBundle(BundlePkt* bundle);

        // Signals for @statistic collection -- sent count, ack count, retransmit count, failure count,
        // and round-trip delay (sender side only; populated when an ACK arrives).
        simsignal_t coapSent, coapAcked, coapRetransmitted, coapFailed, coapRoundTripDelay;
};

#endif /* COAPAPP_H_ */
