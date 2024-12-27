#! /usr/bin/env python3

from mininet.net import Mininet
from mininet.cli import CLI
from mininet.log import lg
from mininet.topo import Topo
from mininet.link import TCLink
import os

os.system("sudo mn -c")

class MyTopo(Topo):
    def __init__(self):
        Topo.__init__(self)

        Spine_North = self.addHost('SN')
        Spine_South = self.addHost('SS')

        # Leafs for North and South
        self.leafs_north = [f'LN{i+1}' for i in range(10)]
        self.leafs_south = [f'LS{i+1}' for i in range(10)]

        # Create Leafs and routers, and connect them to Spine switches
        # Leaf name convention: LN1R1, LS2R1, ..., LN10R1 (Leaf (North | South) [number] Router (1|2))
        # Each Leaf has 3 interfaces: 
        # - eth2 for the connection to the other leaf router in the same Subnet
        # - eth3 for the connection to the Spine switch (IP Range 10.0.200.1 - 10.0.200.x) / (IP Range 10.1.200.1 - 10.1.200.x)
        # - eth1 for the connection to clients/servers/L2-Switches in the same subnet (for later use)
        interfaceIterator = 1
        for i, leaf in enumerate(self.leafs_north):
            router1 = self.addHost(f'{leaf}R1')
            router2 = self.addHost(f'{leaf}R2')
            self.addLink(router1, router2, intfName1=f'{leaf}R1-eth2', intfName2=f'{leaf}R2-eth2')
            self.addLink(router1, Spine_North, intfName1=f'{leaf}R1-eth3', intfName2='SN-eth' + str(interfaceIterator))
            interfaceIterator += 1
            self.addLink(router2, Spine_North, intfName1=f'{leaf}R2-eth3', intfName2='SN-eth' + str(interfaceIterator))
            interfaceIterator += 1

        interfaceIterator = 1
        for i, leaf in enumerate(self.leafs_south):
            router1 = self.addHost(f'{leaf}R1')
            router2 = self.addHost(f'{leaf}R2')
            self.addLink(router1, router2, intfName1=f'{leaf}R1-eth2', intfName2=f'{leaf}R2-eth2')
            self.addLink(router1, Spine_South, intfName1=f'{leaf}R1-eth3', intfName2='SS-eth' + str(interfaceIterator))
            interfaceIterator += 1
            self.addLink(router2, Spine_South, intfName1=f'{leaf}R2-eth3', intfName2='SS-eth' + str(interfaceIterator))
            interfaceIterator += 1



def configure_routes(net):
    topo = net.topo
    Leafs_North = topo.leafs_north
    Leafs_South = topo.leafs_south


    net['SN'].cmd("sysctl -w net.ipv4.ip_forward=1")
    net['SS'].cmd("sysctl -w net.ipv4.ip_forward=1")
    ########## IP configuration for each network interface ##########
    iterator = 1
    netIterator = 0
    for leaf in Leafs_North:
        router1 = net.get(f'{leaf}R1')
        router2 = net.get(f'{leaf}R2')
        router1.cmd("sysctl -w net.ipv4.ip_forward=1")
        router2.cmd("sysctl -w net.ipv4.ip_forward=1")
        router1.cmd("ifconfig " + f'{leaf}R1-eth3 10.0.{200+iterator}.1/24')
        router1.cmd("ifconfig " + f'{leaf}R1-eth2 10.0.{netIterator}.1/24')
        iterator += 1
        router2.cmd("ifconfig " + f'{leaf}R2-eth3 10.0.{200+iterator}.1/24')
        router2.cmd("ifconfig " + f'{leaf}R2-eth2 10.0.{netIterator}.2/24')
        iterator += 1
        netIterator += 1

    iterator = 1
    netIterator = 0
    for leaf in Leafs_South:
        router1 = net.get(f'{leaf}R1')
        router2 = net.get(f'{leaf}R2')
        router1.cmd("sysctl -w net.ipv4.ip_forward=1")
        router2.cmd("sysctl -w net.ipv4.ip_forward=1")
        router1.cmd("ifconfig " + f'{leaf}R1-eth3 10.1.200.{iterator}/24')
        router1.cmd("ifconfig " + f'{leaf}R1-eth2 10.1.{netIterator}.1/24')
        iterator += 1
        router2.cmd("ifconfig " + f'{leaf}R2-eth3 10.1.200.{iterator}/24')
        router2.cmd("ifconfig " + f'{leaf}R2-eth2 10.1.{netIterator}.2/24')
        iterator += 1
        netIterator += 1

    #IP configuration for Spine switches 10 for 10 leafs each spine. *2 because each leaf has 2 routers
    iterator = 1
    for i in range(10*2):
        ipNet = 200 + iterator
        net['SN'].cmd("ifconfig SN-eth" + str(i+1) + " 10.0." + str(ipNet) + "." + "254" + "/24")
        net['SS'].cmd("ifconfig SS-eth" + str(i+1) + " 10.1." + str(ipNet) + "." + "254" + "/24")
        iterator += 1

    ########## Static routes configuration ##########

    # net['LN1R1'].cmd("ip route add 10.0.1.0/24 via 10.0.201.254")
    # net['LN1R1'].cmd("ip route add 10.0.203.0/24 via 10.0.201.254")

    # net['SN'].cmd("ip route add 10.0.0.0/24 via 10.0.201.1")
    # net['SN'].cmd("ip route add 10.0.1.0/24 via 10.0.203.1")

    # net['LN2R1'].cmd("ip route add 10.0.0.0/24 via 10.0.203.254")
    # net['LN2R1'].cmd("ip route add 10.0.201.0/24 via 10.0.203.254")

    #TODO: Get Routing from each leaf to each leaf to work
    #TODO: Get Routing from Spine to spine to work
    #TODO: Clean up the code


    ''' ##TEST for clean up of code##
    def addStaticRoutes(leaf, subnetNo):
        router1 = net.get(f'{leaf}R1')
        router2 = net.get(f'{leaf}R2')
        for i in range(0,10):
            if i == subnetNo:
                continue
            router1.cmd("ip route add 10.0."+ str(i) + ".0/24 via 10.0.201.254")
            print("ip route add 10.0."+ str(i) + ".0/24 via 10.0.201.254")
            router1.cmd("ip route add 10.0." + str(201+i) + ".0/24 via 10.0.201.254")
            print("ip route add 10.0." + str(201+i) + ".0/24 via 10.0.201.254")

    addStaticRoutes('LN1', 0)
    '''

    #Route LN1R1 --- LN2R1
    net['LN1R1'].cmd("ip route add 10.0.1.0/24 via 10.0.201.254")
    net['LN1R1'].cmd("ip route add 10.0.203.0/24 via 10.0.201.254")
    
    net['SN'].cmd("ip route add 10.0.0.0/24 via 10.0.201.1")
    net['SN'].cmd("ip route add 10.0.1.0/24 via 10.0.203.1")

    net['LN2R1'].cmd("ip route add 10.0.0.0/24 via 10.0.203.254")
    net['LN2R1'].cmd("ip route add 10.0.201.0/24 via 10.0.203.254")





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