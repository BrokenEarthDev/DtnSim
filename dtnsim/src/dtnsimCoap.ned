package src;

import src.node.NodeCoap;
import src.central.Central;

network dtnsimCoap
{
    parameters:
        int nodesNumber = default(0);
        @display("bgb=503,408");

    submodules:
        node[nodesNumber+1]: NodeCoap {
            parameters:
                @display("p=169,50");
        }

        central: Central {
            parameters:
                @display("p=40,150");
        }

    connections:
}
