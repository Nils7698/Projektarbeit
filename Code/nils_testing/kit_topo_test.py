#! /usr/bin/env python3

from mininet.net import Mininet
from mininet.cli import CLI
from mininet.log import lg
from mininet.topo import Topo
from mininet.link import TCLink
import os

# Clear cache before running script, because it leads to weird behaviour
os.system("sudo mn -c")

class MyTopo(Topo):
    def __init__(self):
        Topo.__init__(self)

        # List of spine switches for North and South
        Spines_North = ['Spine_N_1', 'Spine_N_2', 'Spine_N_3', 'Spine_N_4']
        Spines_South = ['Spine_S_1', 'Spine_S_2', 'Spine_S_3', 'Spine_S_4']

        # Create North spine switches using a loop
        self.spines_north = {spine: self.addSwitch(spine) for spine in Spines_North}

        # Create South spine switches using a loop
        self.spines_south = {spine: self.addSwitch(spine) for spine in Spines_South}

        # Create links between North spine switches
        for i, spine1 in enumerate(Spines_North):
            for spine2 in Spines_North[i+1:]:
                self.addLink(self.spines_north[spine1], self.spines_north[spine2])

        # Create links between South spine switches
        for i, spine1 in enumerate(Spines_South):
            for spine2 in Spines_South[i+1:]:
                self.addLink(self.spines_south[spine1], self.spines_south[spine2])

        # Connect North and South spine switches
        for north_spine in Spines_North:
            for south_spine in Spines_South:
                self.addLink(self.spines_north[north_spine], self.spines_south[south_spine])

        # Leafs for North and South
        self.leafs_north = [f'LN{i+1}' for i in range(10)]
        self.leafs_south = [f'LS{i+1}' for i in range(10)]

        # Create Leafs and routers, and connect them to Spine switches
        for i, leaf in enumerate(self.leafs_north):
            router1 = self.addHost(f'{leaf}R1', ip=f'10.0.{i}.1/24')
            router2 = self.addHost(f'{leaf}R2', ip=f'10.0.{i}.2/24')
            self.addLink(router1, router2)
            for spine in Spines_North:
                self.addLink(router1, self.spines_north[spine])
                self.addLink(router2, self.spines_north[spine])

        for i, leaf in enumerate(self.leafs_south):
            router1 = self.addHost(f'{leaf}R1', ip=f'10.1.{i}.1/24')
            router2 = self.addHost(f'{leaf}R2', ip=f'10.1.{i}.2/24')
            self.addLink(router1, router2)
            for spine in Spines_South:
                self.addLink(router1, self.spines_south[spine])
                self.addLink(router2, self.spines_south[spine])

def configure_routes(net):
    topo = net.topo
    Leafs_North = topo.leafs_north
    Leafs_South = topo.leafs_south

    # Enable IP forwarding on all routers
    for leaf in Leafs_North + Leafs_South:
        router1 = net.get(f'{leaf}R1')
        router2 = net.get(f'{leaf}R2')
        router1.cmd("sysctl -w net.ipv4.ip_forward=1")
        router2.cmd("sysctl -w net.ipv4.ip_forward=1")

    for i, leaf in enumerate(Leafs_North):
        router1 = net.get(f'{leaf}R1')
        router2 = net.get(f'{leaf}R2')
        for j, other_leaf in enumerate(Leafs_North + Leafs_South):
            if i != j:
                router1.cmd(f'ip route add 10.{1 if j >= 10 else 0}.{j}.0/24 via 10.0.{i}.2')
                router2.cmd(f'ip route add 10.{1 if j >= 10 else 0}.{j}.0/24 via 10.0.{i}.1')

    for i, leaf in enumerate(Leafs_South):
        router1 = net.get(f'{leaf}R1')
        router2 = net.get(f'{leaf}R2')
        for j, other_leaf in enumerate(Leafs_North + Leafs_South):
            if i + 10 != j:
                router1.cmd(f'ip route add 10.{0 if j < 10 else 1}.{j if j < 10 else j - 10}.0/24 via 10.1.{i}.2')
                router2.cmd(f'ip route add 10.{0 if j < 10 else 1}.{j if j < 10 else j - 10}.0/24 via 10.1.{i}.1')

def nettopo(**kwargs):
    topo = MyTopo()
    return Mininet(topo=topo, link=TCLink, **kwargs)

if __name__ == '__main__':
    lg.setLogLevel('info')
    net = nettopo()
    net.start()
    configure_routes(net)
    CLI(net)
    net.stop()
