#! /usr/bin/env python3

from mininet.net import Mininet
from mininet.cli import CLI
from mininet.node import RemoteController
from mininet.node import OVSSwitch
from mininet.log import lg
from mininet.topo import Topo
from mininet.link import TCLink

''' Topology (Grid):
LN1  --  LN2  --  LN3  --  LN4  
 |        |        |        |  
LN5  --  LN6  --  LN7  --  LN8  
 |        |        |        |  
LN9  --  LN10 --  LN11 --  LN12  
 |        |        |        |  
LN13 --  LN14 --   LN15 --   LN16  
'''

'''
For the new topology we use the Ryu network controller that needs to be installed on the system.
The controller is started in a new terminal with the following command:

ryu-manager --observe-links ryu_multipath.py

the ryu_multipath.py is from https://github.com/wildan2711/multipath // https://wildanmsyah.wordpress.com/2018/01/21/testing-ryu-multipath-routing-with-load-balancing-on-mininet/
'''


stddelay = '3ms'
stdQueueSize = 13333333 # max queue size is in packets, so 1500 Byte (MTU) * 13333333 = 20 GB
stdbw= 100 # in MBit/s, max 1000 MBit/s

class MyTopo(Topo):
    def __init__(self):
        Topo.__init__(self)


        self.leafs_north = [f'LN{i+1}' for i in range(16)]  # Define 16 leaf switches
        switches = {}

        # Create switches (LN1 to LN16)
        for ln in self.leafs_north:
            switches[ln] = self.addSwitch(ln, switch='ovsk')

        # Connect switches in a 4x4 grid structure
        for i in range(4):
            for j in range(4):
                switch_id = i * 4 + j  # Calculate switch index in the grid

                # Connect switch to its right neighbor (if not at the right edge)
                if j < 3:
                    right_id = switch_id + 1
                    self.addLink(switches[self.leafs_north[switch_id]], 
                                 switches[self.leafs_north[right_id]], 
                                 bw=stdbw, delay=stddelay)

                # Connect switch to its bottom neighbor (if not at the bottom edge)
                if i < 3:
                    down_id = switch_id + 4
                    self.addLink(switches[self.leafs_north[switch_id]], 
                                 switches[self.leafs_north[down_id]], 
                                 bw=stdbw, delay=stddelay)


        def addClient(name, linkedSwitch):
            client = self.addHost(name)
            self.addLink(client, linkedSwitch, bw=stdbw, delay=stddelay)
            return client
        
        # Add static services
        SCC_N1 = addClient('SCC_N1', switches['LN1'])
        CAMPUS_N = addClient('CAMPUS_N', switches['LN2'])
        LSDF = addClient('LSDF', switches['LN3'])
        FILE = addClient('FILE', switches['LN6'])
        SCC_N2 = addClient('SCC_N2', switches['LN9'])
        BWCLOUD = addClient('BWCLOUD', switches['LN14'])


        def addHostsToLeaf(leaf_name, num_hosts):
            for i in range(num_hosts):
                host_name = f"{leaf_name}C{i+1}"
                host = self.addHost(host_name)
                self.addLink(host, switches[leaf_name], bw=stdbw, delay=stddelay)


        # Add Clients
        addHostsToLeaf("LN2", 3)
        addHostsToLeaf("LN8", 3)
        addHostsToLeaf("LN12", 3)
        


def nettopo(**kwargs):
    topo = MyTopo()
    net = Mininet(topo=topo, switch=OVSSwitch, controller=None, link=TCLink, **kwargs)
    net.addController('c0', controller=RemoteController, port=6633)
    return net

if __name__ == '__main__':
    lg.setLogLevel('info')
    net = nettopo()
    net.start()
    
    CLI(net)
    net.stop()