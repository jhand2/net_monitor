# net_monitor

monitor.py only runs on Linux. It does not run on other popular UNIX operating systems due to the use of AF_PACKET, which is linux specific. In particular, monitor.py does not run on BSD based systems like Mac OSX.

A network monitor (with a REST API on top of it) for analyzing networks and providing actionable metadata about network traffic on any machine.

Uses  mongodb for storage (by default uses a local mongodb)

The current implementation only intercepts network traffic between the machine running monitor.py and any other machines that interact with it. Further research would need to be done to intercept other packets on the network. Based on my current understanding, a more complex network topology would be required.
