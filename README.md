# Projektarbeit - Simulierung des KIT-Netzwerks mit Mininet für die Sammlung von Daten

[Ausarbeitung in Overleaf](https://de.overleaf.com/read/vhmxkngntjpv#83789b)

### TODOS
- [x] Configure routing in Spine North
- [x] Configure routing in Spine South
- [x] Add KIT Services
- [x] look what metrics we can collect
- [x] create new, complex topology
- [x] Create networking scenarios
- [ ] execute the scenarios and save data

____________________

### How To

#### KIT Topology  
The **`kit_topology`** file in the `Code` folder contains the latest representation of the KIT network topology.  

To run the topology, use:  
sudo python3 kit_topology_v5.py [--clients N]

The --clients parameter is optional. It defines the number of clients per leaf switch.
If omitted, the default value is 3 clients per leaf.

### New SDN-Enabled Topology

The `newTopology` folder contains a more complex network topology that integrates an SDN controller for advanced network management.
