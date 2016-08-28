# net_monitor

A network monitor (with a REST API on top of it) for analyzing networks and providing actionable metadata about any network.

Runs on any unix machine. Uses  mongodb for storage (by default uses a local mongodb)

The current implementation only intercepts network traffic between the machine running monitor.py and any other machines on the network. Further research would need to be done to intercept other packets on the network. Based on my current understanding, a more complex network topology would be required.
