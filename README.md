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

#### KIT Topology  
The **`kit_topology`** file in the `Code` folder contains the latest representation of the KIT network topology.  

To run the topology, use:  
sudo python3 kit_topology_v5.py [--clients N]

The --clients parameter is optional. It defines the number of clients per leaf switch.
If omitted, the default value is 3 clients per leaf.

### New SDN-Enabled Topology

The `newTopology` folder contains a more complex network topology that integrates an SDN controller for advanced network management.

____________________

### Naming Convention for Data Files
Each topology generates a folder to store measured data for different scenarios. The naming convention for these folders follows the format:

[number_of_clients_per_leaf]__scenario__[scenario_type]

`number_of_clients_per_leaf`: The number of clients assigned to each leaf pair.
`scenario_type`: The type of scenario being tested (e.g., backup, normal).

Examples:

`3_scenario_backup` → Each leaf pair has three clients that initiate communication with the servers, tested under a backup scenario.

`5_scenario_backup` → Each leaf pair has five clients, tested under a backup scenario.

### Naming Convention for Client Data Files
For each client, the measured data is stored in a separate `.json` file following this naming convention:

[duration]__[ms]__[scenario_type]_[client_name].json

`duration`: The length of the test or simulation (e.g., 60sec for 60 seconds, 600sec for 10 minutes etc).

`ms (optional)`: Stands for multistreaming, indicating that parallel streaming or multiple connections between the client and server were enabled. If ms is not included, the test was conducted using single-streaming.

`scenario_type`: The type of scenario being tested (e.g., backup, normal, emergency).

`client_name`: The name of the client.

Examples:

`60sec_backup_LN12C1.json` → Contains all measured data for client LN12C1, tested under the backup scenario for 60 seconds using single-streaming.

`600sec_ms_normal_LN12C1.json` → Contains all measured data for client LN12C1, tested under the normal scenario for 600 seconds (10 minutes) with multistreaming enabled.
