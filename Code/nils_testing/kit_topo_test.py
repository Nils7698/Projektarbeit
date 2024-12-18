#! /usr/bin/env python3

from mininet.net import Mininet
from mininet.cli import CLI
from mininet.log import lg
from mininet.topo import Topo
from mininet.link import TCLink
from mininet.nodelib import LinuxBridge
import os

os.system("sudo mn -c")


class MyTopo(Topo):
    def __init__(self):
        Topo.__init__(self)


#################### --SPINES-- ####################
    
        # List of spine switches for North and South
        Spines_North = ['Spine_N_1', 'Spine_N_2', 'Spine_N_3', 'Spine_N_4']
        Spines_South = ['Spine_S_1', 'Spine_S_2', 'Spine_S_3', 'Spine_S_4']

        # Create North spine switches using a loop
        spines_north = {spine: self.addSwitch(spine) for spine in Spines_North}

        # Create South spine switches using a loop
        spines_south = {spine: self.addSwitch(spine) for spine in Spines_South}

        # Create links between North spine switches
        for i, spine1 in enumerate(Spines_North):
            for spine2 in Spines_North[i+1:]:
                self.addLink(spines_north[spine1], spines_north[spine2])

        # Create links between South spine switches
        for i, spine1 in enumerate(Spines_South):
            for spine2 in Spines_South[i+1:]:
                self.addLink(spines_south[spine1], spines_south[spine2])

        # Connect North and South spine switches (assuming each North spine connects to each South spine)
        for north_spine in Spines_North:
            for south_spine in Spines_South:
                self.addLink(spines_north[north_spine], spines_south[south_spine])




#################### --LEAFS-- ####################


# configuration
def conf(network):
    print("test") #add routing configs



def nettopo(**kwargs):
    topo = MyTopo()
    return Mininet(topo=topo, link=TCLink, controller = None, switch = LinuxBridge, **kwargs)


if __name__ == '__main__':
    lg.setLogLevel('info')
    net = nettopo()
    net.start()
    conf(net)
    CLI(net)
    net.stop()

