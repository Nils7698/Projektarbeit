#! /usr/bin/env python3

from mininet.net import Mininet
from mininet.node import OVSSwitch
from mininet.cli import CLI
from mininet.log import lg
from mininet.topo import Topo
from mininet.link import TCLink
import os
import argparse
import random
import time

# clears Mininet cache
os.system("sudo mn -c")

'''
Scaling: factor 3000
60.000 users -> 20
100Gbit bw -> 33Mbit/s
13333333 packets -> 4444 packets
'''

debug = 0  # default
scenario_time = 60  # default
multistream = 1 # default
stddelay = '2ms'
stdQueueSize = 4444 # max queue size is in packets, so 1500 Byte (MTU) * 13333333 = 20 GB
stdbw= 33 # in MBit/s, max 1000 MBit/s 
numberOfClients = 3 # default value
hosts = []

#IPs of Servers
SCC_N1_ip = "10.0.100.200"
CAMPUS_N_ip = "10.0.101.200"
LSDF_ip = "10.0.102.200"
FILE_ip = "10.0.105.200"
SCC_N2_ip = "10.0.109.200"
BWCLOUD_ip = "10.0.113.200"

SCC_S1_ip = "10.1.100.200"
CAMPUS_S_ip = "10.1.101.200"
VM_ip = "10.1.105.200"
SCC_S2_ip = "10.1.109.200"



class MyTopo(Topo):
    def __init__(self):
        Topo.__init__(self)

        Spine_North = self.addHost('SN')
        Spine_South = self.addHost('SS')

        # Leafs for North and South
        self.leafs_north = [f'LN{i+1}' for i in range(16)]
        self.leafs_south = [f'LS{i+1}' for i in range(13)]

        # Create Leafs and routers, and connect them to Spine switches
        # Leaf name convention: LN1R1, LS2R1, ..., LN10R1 (Leaf (North | South) [number] Router (1|2))
        # Each Leaf has 3 interfaces: 
        # - eth2 for the connection to the other leaf router in the same Subnet
        # - eth3 for the connection to the Spine switch (IP Range 10.0.201.1 - 10.0.2xx.1) / (IP Range 10.1.201.1 - 10.1.2xx.1). The last IP is reserved for the Spine switch (e.g 10.0.201.254)
        # - eth1 for the connection to clients/servers/L2-Switches in the same subnet (IP Range 10.0.100.1 - 10.0.1xx.1) / (IP Range 10.1.100.1 - 10.1.1xx.1)
        interfaceIterator = 1
        for i, leaf in enumerate(self.leafs_north):
            router1 = self.addHost(f'{leaf}R1')
            router2 = self.addHost(f'{leaf}R2')
            self.addLink(router1, router2, intfName1=f'{leaf}R1-eth2', intfName2=f'{leaf}R2-eth2', delay = stddelay, max_queue_size = stdQueueSize, bw=stdbw)
            self.addLink(router1, Spine_North, intfName1=f'{leaf}R1-eth3', intfName2='SN-eth' + str(interfaceIterator), delay = stddelay, max_queue_size = stdQueueSize, bw=stdbw)
            interfaceIterator += 1
            self.addLink(router2, Spine_North, intfName1=f'{leaf}R2-eth3', intfName2='SN-eth' + str(interfaceIterator), delay = stddelay, max_queue_size = stdQueueSize, bw=stdbw)
            interfaceIterator += 1
            #create a switch for each leaf and connect to R1
            self.addSwitch(f'{leaf}SW')
            self.addLink(f'{leaf}SW', f'{leaf}R1', intfName2 = f'{leaf}R1-eth1', delay = stddelay, max_queue_size = stdQueueSize, bw=stdbw)

        interfaceIterator = 1
        for i, leaf in enumerate(self.leafs_south):
            router1 = self.addHost(f'{leaf}R1')
            router2 = self.addHost(f'{leaf}R2')
            self.addLink(router1, router2, intfName1=f'{leaf}R1-eth2', intfName2=f'{leaf}R2-eth2', delay = stddelay, max_queue_size = stdQueueSize, bw=stdbw)
            self.addLink(router1, Spine_South, intfName1=f'{leaf}R1-eth3', intfName2='SS-eth' + str(interfaceIterator), delay = stddelay, max_queue_size = stdQueueSize, bw=stdbw)
            interfaceIterator += 1
            self.addLink(router2, Spine_South, intfName1=f'{leaf}R2-eth3', intfName2='SS-eth' + str(interfaceIterator), delay = stddelay, max_queue_size = stdQueueSize, bw=stdbw)
            interfaceIterator += 1
            #create a switch for each leaf and connect to R1
            self.addSwitch(f'{leaf}SW')
            self.addLink(f'{leaf}SW', f'{leaf}R1', intfName2 = f'{leaf}R1-eth1', delay = stddelay, max_queue_size = stdQueueSize, bw=stdbw)


        #add clients and servers

        def addClient(name, ip, linkedSwitch):
            client = self.addHost(name, ip=ip)
            self.addLink(client, linkedSwitch, delay = stddelay, bw=stdbw)
            hosts.append(client)
            return client


        #Static Services North
        addClient('SCC_N1', f"{SCC_N1_ip}/24", 'LN1SW')
        addClient('CAMPUS_N', f"{CAMPUS_N_ip}/24", 'LN2SW')
        addClient('LSDF', f"{LSDF_ip}/24", 'LN3SW')
        addClient('FILE', f"{FILE_ip}/24", 'LN6SW')
        addClient('SCC_N2', f"{SCC_N2_ip}/24", 'LN10SW')
        addClient('BWCLOUD', f"{BWCLOUD_ip}/24", 'LN14SW')


        #Static Services South
        addClient('SCC_S1', f"{SCC_S1_ip}/24", 'LS1SW')
        addClient('CAMPUS_S', f"{CAMPUS_S_ip}/24", 'LS2SW')
        addClient('VM', f"{VM_ip}/24", 'LS6SW')
        addClient('SCC_S2', f"{SCC_S2_ip}/24", 'LS10SW')

        #Clients
        for i in range(numberOfClients):
            addClient(f'LN2C{i+1}', f'10.0.101.{10+i+1}/24', 'LN2SW')
            addClient(f'LN9C{i+1}', f'10.0.108.{10+i+1}/24', 'LN9SW')
            addClient(f'LN12C{i+1}', f'10.0.111.{10+i+1}/24', 'LN12SW')

            addClient(f'LS2C{i+1}', f'10.1.101.{10+i+1}/24', 'LS2SW')
            addClient(f'LS8C{i+1}', f'10.1.107.{10+i+1}/24', 'LS8SW')
            addClient(f'LS9C{i+1}', f'10.1.108.{10+i+1}/24', 'LS9SW')
            addClient(f'LS12C{i+1}', f'10.1.111.{10+i+1}/24', 'LS12SW')
        
        
def configure_switches(net):
    """ Sets all switches in Mininet to standalone mode """
    
    print("[+] Configurating switches...")
    for switch in net.switches:
        switch.cmd('ovs-vsctl set-fail-mode {} standalone'.format(switch.name))
        
    # Check with "sudo ovs-vsctl show" in separate terminal!


def configure_routes(net):
    print("[+] Configurating routers...")
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
        router1.cmd("ifconfig " + f'{leaf}R1-eth1 10.0.{100+netIterator}.1/24')
        iterator += 1
        router2.cmd("ifconfig " + f'{leaf}R2-eth3 10.0.{200+iterator}.1/24')
        router2.cmd("ifconfig " + f'{leaf}R2-eth2 10.0.{netIterator}.2/24')
        router2.cmd("ifconfig " + f'{leaf}R2-eth1 10.0.{100+netIterator}.2/24')
        iterator += 1
        netIterator += 1

    iterator = 1
    netIterator = 0
    for leaf in Leafs_South:
        router1 = net.get(f'{leaf}R1')
        router2 = net.get(f'{leaf}R2')
        router1.cmd("sysctl -w net.ipv4.ip_forward=1")
        router2.cmd("sysctl -w net.ipv4.ip_forward=1")
        router1.cmd("ifconfig " + f'{leaf}R1-eth3 10.1.{200+iterator}.1/24')
        router1.cmd("ifconfig " + f'{leaf}R1-eth2 10.1.{netIterator}.1/24')
        router1.cmd("ifconfig " + f'{leaf}R1-eth1 10.1.{100+netIterator}.1/24')
        iterator += 1
        router2.cmd("ifconfig " + f'{leaf}R2-eth3 10.1.{200+iterator}.1/24')
        router2.cmd("ifconfig " + f'{leaf}R2-eth2 10.1.{netIterator}.2/24')
        router2.cmd("ifconfig " + f'{leaf}R2-eth1 10.1.{100+netIterator}.2/24')
        iterator += 1
        netIterator += 1

    #IP configuration for Spine switches 10 for 10 leafs each spine. *2 because each leaf has 2 routers
    iterator = 1
    for i in range(16*2):
        ipNet = 200 + iterator
        net['SN'].cmd("ifconfig SN-eth" + str(i+1) + " 10.0." + str(ipNet) + "." + "254" + "/24")
        net['SS'].cmd("ifconfig SS-eth" + str(i+1) + " 10.1." + str(ipNet) + "." + "254" + "/24")
        iterator += 1

    ########## Static routes configuration ##########

    def addStaticRoutesToRouters(leaf, subnetNo, NorthSouthID):
        """Adds static routes to the routers of the leafs
        Args:
            leaf (str): Leaf name
            subnetNo (int): Subnet number
            NorthSouthID (int): 0 for North, 1 for South
        """
        router1 = net.get(f'{leaf}R1')
        router2 = net.get(f'{leaf}R2')
        #Routing for R1
        if NorthSouthID == 0:
            rangeNo = 16
        else:
            rangeNo = 13
        for i in range(0,rangeNo):
            if i == subnetNo:
                continue
            #Route to Subnet
            router1.cmd("ip route add 10." + str(NorthSouthID) + "."+ str(i) + ".0/24 via 10." + str(NorthSouthID) + "." + str(201+2*subnetNo) + ".254")
            router2.cmd("ip route add 10." + str(NorthSouthID) + "." + str(i) + ".0/24 via 10." + str(NorthSouthID) + "." + str(201+2*subnetNo+1) + ".254")
        for i in range(0,rangeNo):
            #Route to Spine
            router1.cmd("ip route add 10." + str(NorthSouthID) + "." + str(201+i) + ".0/24 via 10." + str(NorthSouthID) + "." + str(201+2*subnetNo) + ".254")
            router2.cmd("ip route add 10." + str(NorthSouthID) + "." + str(201+i) + ".0/24 via 10." + str(NorthSouthID) + "." + str(201+2*subnetNo+1) + ".254")
        for i in range(0,rangeNo):
            #Route to Clients/Servers
            router1.cmd("ip route add 10." + str(NorthSouthID) + "." + str(100+i) + ".0/24 via 10." + str(NorthSouthID) + "." + str(201+2*subnetNo) + ".254")
            router2.cmd("ip route add 10." + str(NorthSouthID) + "." + str(100+i) + ".0/24 via 10." + str(NorthSouthID) + "." + str(201+2*subnetNo+1) + ".254")

    def addStaticRoutesSpine():
        for i in range(0,16):
            net['SN'].cmd("ip route add 10.0."+ str(i) + ".0/24 via 10.0." + str(201+2*i) + ".1")
            net['SN'].cmd("ip route add 10.0."+ str(100+i) + ".0/24 via 10.0." + str(201+2*i) + ".1")
            
        for i in range(0,13):
            net['SS'].cmd("ip route add 10.1."+ str(i) + ".0/24 via 10.1." + str(201+2*i) + ".1")
            net['SS'].cmd("ip route add 10.1."+ str(100+i) + ".0/24 via 10.1." + str(201+2*i) + ".1")


    for i in range(16):
        addStaticRoutesToRouters(f'LN{i+1}', i, 0)
 
    for i in range(13):
        addStaticRoutesToRouters(f'LS{i+1}', i, 1)
   

    addStaticRoutesSpine()

    #Client/Server Routing
    print("[+] Configurating servers...")
    for i in range(0,16):
        net['SCC_N1'].cmd("ip route add 10.0."+ str(100+i) + ".0/24 via 10.0.100.1")
        net['SCC_N1'].cmd("ip route add 10.0."+ str(200+i) + ".0/24 via 10.0.100.1")
        net['SCC_N1'].cmd("ip route add 10.0."+ str(0+i) + ".0/24 via 10.0.100.1")

        net['CAMPUS_N'].cmd("ip route add 10.0."+ str(100+i) + ".0/24 via 10.0.101.1")
        net['CAMPUS_N'].cmd("ip route add 10.0."+ str(200+i) + ".0/24 via 10.0.101.1")
        net['CAMPUS_N'].cmd("ip route add 10.0."+ str(0+i) + ".0/24 via 10.0.101.1")

        net['LSDF'].cmd("ip route add 10.0."+ str(100+i) + ".0/24 via 10.0.102.1")
        net['LSDF'].cmd("ip route add 10.0."+ str(200+i) + ".0/24 via 10.0.102.1")
        net['LSDF'].cmd("ip route add 10.0."+ str(0+i) + ".0/24 via 10.0.102.1")

        net['FILE'].cmd("ip route add 10.0."+ str(100+i) + ".0/24 via 10.0.105.1")
        net['FILE'].cmd("ip route add 10.0."+ str(200+i) + ".0/24 via 10.0.105.1")
        net['FILE'].cmd("ip route add 10.0."+ str(0+i) + ".0/24 via 10.0.105.1")

        net['SCC_N2'].cmd("ip route add 10.0."+ str(100+i) + ".0/24 via 10.0.109.1")
        net['SCC_N2'].cmd("ip route add 10.0."+ str(200+i) + ".0/24 via 10.0.109.1")
        net['SCC_N2'].cmd("ip route add 10.0."+ str(0+i) + ".0/24 via 10.0.109.1")
        
        net['BWCLOUD'].cmd("ip route add 10.0."+ str(100+i) + ".0/24 via 10.0.113.1")
        net['BWCLOUD'].cmd("ip route add 10.0."+ str(200+i) + ".0/24 via 10.0.113.1")
        net['BWCLOUD'].cmd("ip route add 10.0."+ str(0+i) + ".0/24 via 10.0.113.1")

        net['SCC_S1'].cmd("ip route add 10.1."+ str(100+i) + ".0/24 via 10.1.100.1")
        net['SCC_S1'].cmd("ip route add 10.1."+ str(200+i) + ".0/24 via 10.1.100.1")
        net['SCC_S1'].cmd("ip route add 10.1."+ str(0+i) + ".0/24 via 10.1.100.1")  

        net['CAMPUS_S'].cmd("ip route add 10.1."+ str(100+i) + ".0/24 via 10.1.101.1")  
        net['CAMPUS_S'].cmd("ip route add 10.1."+ str(200+i) + ".0/24 via 10.1.101.1") 
        net['CAMPUS_S'].cmd("ip route add 10.1."+ str(0+i) + ".0/24 via 10.1.101.1") 
    
        net['VM'].cmd("ip route add 10.1."+ str(100+i) + ".0/24 via 10.1.105.1")
        net['VM'].cmd("ip route add 10.1."+ str(200+i) + ".0/24 via 10.1.105.1")
        net['VM'].cmd("ip route add 10.1."+ str(0+i) + ".0/24 via 10.1.105.1")

        net['SCC_S2'].cmd("ip route add 10.1."+ str(100+i) + ".0/24 via 10.1.109.1")
        net['SCC_S2'].cmd("ip route add 10.1."+ str(200+i) + ".0/24 via 10.1.109.1")
        net['SCC_S2'].cmd("ip route add 10.1."+ str(0+i) + ".0/24 via 10.1.109.1")

        for j in range(numberOfClients):
            net[f'LN2C{j+1}'].cmd("ip route add 10.0."+ str(100+i) + ".0/24 via 10.0.101.1")
            net[f'LN2C{j+1}'].cmd("ip route add 10.0."+ str(200+i) + ".0/24 via 10.0.101.1")
            net[f'LN2C{j+1}'].cmd("ip route add 10.0."+ str(0+i) + ".0/24 via 10.0.101.1")

            net[f'LN9C{j+1}'].cmd("ip route add 10.0."+ str(100+i) + ".0/24 via 10.0.108.1")
            net[f'LN9C{j+1}'].cmd("ip route add 10.0."+ str(200+i) + ".0/24 via 10.0.108.1")
            net[f'LN9C{j+1}'].cmd("ip route add 10.0."+ str(0+i) + ".0/24 via 10.0.108.1")

            net[f'LN12C{j+1}'].cmd("ip route add 10.0."+ str(100+i) + ".0/24 via 10.0.111.1")
            net[f'LN12C{j+1}'].cmd("ip route add 10.0."+ str(200+i) + ".0/24 via 10.0.111.1")
            net[f'LN12C{j+1}'].cmd("ip route add 10.0."+ str(0+i) + ".0/24 via 10.0.111.1")

            net[f'LS2C{j+1}'].cmd("ip route add 10.1."+ str(100+i) + ".0/24 via 10.1.101.1")
            net[f'LS2C{j+1}'].cmd("ip route add 10.1."+ str(200+i) + ".0/24 via 10.1.101.1")
            net[f'LS2C{j+1}'].cmd("ip route add 10.1."+ str(0+i) + ".0/24 via 10.1.101.1")

            net[f'LS8C{j+1}'].cmd("ip route add 10.1."+ str(100+i) + ".0/24 via 10.1.107.1")
            net[f'LS8C{j+1}'].cmd("ip route add 10.1."+ str(200+i) + ".0/24 via 10.1.107.1")
            net[f'LS8C{j+1}'].cmd("ip route add 10.1."+ str(0+i) + ".0/24 via 10.1.107.1")

            net[f'LS9C{j+1}'].cmd("ip route add 10.1."+ str(100+i) + ".0/24 via 10.1.108.1")
            net[f'LS9C{j+1}'].cmd("ip route add 10.1."+ str(200+i) + ".0/24 via 10.1.108.1")
            net[f'LS9C{j+1}'].cmd("ip route add 10.1."+ str(0+i) + ".0/24 via 10.1.108.1")

            net[f'LS12C{j+1}'].cmd("ip route add 10.1."+ str(100+i) + ".0/24 via 10.1.111.1")
            net[f'LS12C{j+1}'].cmd("ip route add 10.1."+ str(200+i) + ".0/24 via 10.1.111.1")
            net[f'LS12C{j+1}'].cmd("ip route add 10.1."+ str(0+i) + ".0/24 via 10.1.111.1")

    # Start IPerf Servers for all static services
    # Default port of iperf3 is 5201
    
    # Because we are doing tests on Campus North only, we'll have to open more ports so that we
    # can run multiple tests simultaneously. Iperf3 requires separate ports for each test!
    
    for port in range(5201, 5202 + numberOfClients*3):  # numberOfClients*3 ports for each server
        net['SCC_N1'].cmd(f"iperf3 -s -p {port} &")
        net['CAMPUS_N'].cmd(f"iperf3 -s -p {port} &")
        net['LSDF'].cmd(f"iperf3 -s -p {port} &")
        net['FILE'].cmd(f"iperf3 -s -p {port} &")
        net['SCC_N2'].cmd(f"iperf3 -s -p {port} &")
        net['BWCLOUD'].cmd(f"iperf3 -s -p {port} &")

    
    net['SCC_S1'].cmd("iperf3 -s &")
    net['CAMPUS_S'].cmd("iperf3 -s &")
    net['VM'].cmd("iperf3 -s &")
    net['SCC_S2'].cmd("iperf3 -s &")



    '''
    Netzwerk Szenarios:
    
    
    1. Backup-Welle am Abend:
    Jeden Abend gegen 22 Uhr starten automatisierte Backup-Prozesse auf den Endgeräten der  Mitarbeiter. Diese verbinden sich gleichzeitig mit dem zentralen Fileserver der Universität, um wichtige Dokumente und Konfigurationsdateien zu sichern. D.h. alle Clients ---> FILE 
    '''
    
def scenario_backup(net, numberOfClients):
    
    print(f"[+] Initializing backup...")
    os.system(f"mkdir -p {numberOfClients}_scenario_backup")
    # To delete the folder use "sudo rm -r {numberOfClients}_scenario_backup"
    
    port = 5201 # default iperf3 port
    
    for j in range(1, numberOfClients + 1):
        clients = [f'LN2C{j}', f'LN9C{j}', f'LN12C{j}'] # Only North Campus!
        
        if debug:
            print(f"[DEBUG] Processing the following clients for iteration {j}: {clients}")
        
        for i in range(min(numberOfClients, len(clients))):
            client = clients[i]
            
            if client in net:  # Check if client exists in the network
                if multistream:
                   parallel_streams = random.randint(1, 5)  # Random number of parallel connections
                else:
                   parallel_streams = 1
                bandwidth = random.choice(["0.625MB", "3.25MB", "9.875MB", "19.75MB", "33MB"]) # Random bandwidth
                
                if debug:
                    print(f"[DEBUG] Starting iperf3 from {client} to FILE server with {parallel_streams} stream(s) and {bandwidth} bandwidth on port {port}...")
                
                if multistream: # if multistreaming enabled
                    net[client].cmd(f"iperf3 -c {FILE_ip} -p {port} -P {parallel_streams} -b {bandwidth} -t {scenario_time} --json > {numberOfClients}_scenario_backup/{scenario_time}sec_ms_backup_{client}.json &")
                    net[client].cmd(f"ping -c {scenario_time} {FILE_ip} > {numberOfClients}_scenario_backup/{scenario_time}sec_ms_ping_backup_{client}.txt &")
                
                else: # if only one stream per client
                    net[client].cmd(f"iperf3 -c {FILE_ip} -p {port} -P {parallel_streams} -b {bandwidth} -t {scenario_time} --json > {numberOfClients}_scenario_backup/{scenario_time}sec_backup_{client}.json &")
                    net[client].cmd(f"ping -c {scenario_time} {FILE_ip} > {numberOfClients}_scenario_backup/{scenario_time}sec_ping_backup_{client}.txt &")
                    
                port = port + 1 # Take the next free port

    
    '''
    2.  Arbeitsalltag
    Während eines typischen Arbeitstages in der Universität greifen verschiedene Nutzer auf unterschiedliche Server zu:
    Studierende verbinden sich mit dem E-Learning-System der Uni, nutzen VPN-Zugänge für Online-Datenbanken oder greifen auf den WLAN-Druckerserver zu. Dozierende und Mitarbeiter laden Vorlesungsmaterialien auf die Webserver hoch oder nutzen Remote-Desktop-Verbindungen, um sich mit Hochleistungsrechnern im Rechenzentrum zu verbinden. Forschende übertragen große Datenmengen zwischen lokalen Arbeitsplätzen und HPC-Clustern für simulationsbasierte Berechnungen. 
    '''
def scenario_normal(net, numberOfClients):

    print(f"[+] Initializing a simulation of an average workday...")
    os.system(f"mkdir -p {numberOfClients}_scenario_normal")
    # To delete the folder use "sudo rm -r {numberOfClients}_scenario_normal"
    
    port = 5201 # default iperf3 port
    
    # Define the list of servers for North Campus
    north_campus_servers = {
    "SCC_N1": SCC_N1_ip, 
    "CAMPUS_N": CAMPUS_N_ip, 
    "LSDF": LSDF_ip, 
    "FILE": FILE_ip, 
    "SCC_N2": SCC_N2_ip, 
    "BWCLOUD": BWCLOUD_ip
     }

    
    for j in range(1, numberOfClients + 1):
        clients = [f'LN2C{j}', f'LN9C{j}', f'LN12C{j}'] # Only North Campus!
        
        if debug:
            print(f"[DEBUG] Processing the following clients for iteration {j}: {clients}")
        
        for i in range(min(numberOfClients, len(clients))):
            client = clients[i]
            
            if client in net:  # Check if client exists in the network
                # Randomly select the server
                server, server_ip = random.choice(list(north_campus_servers.items()))

                
                # Randomize other parameters
                if multistream:
                   parallel_streams = random.randint(1, 5)  # Random number of parallel connections
                else:
                   parallel_streams = 1 
                bandwidth = random.choice(["0.625MB", "3.25MB", "9.875MB", "19.75MB", "33MB"])
                
                if debug:
                    print(f"[DEBUG] Starting iperf3 from {client} to {server} server with {parallel_streams} stream(s) and {bandwidth} bandwidth on port {port}...")
                
                if multistream: # if multistreaming enabled
                    net[client].cmd(f"iperf3 -c {server_ip} -p {port} -P {parallel_streams} -b {bandwidth} -t {scenario_time} --json > {numberOfClients}_scenario_normal/{scenario_time}sec_ms_normal_{client}.json &")
                    net[client].cmd(f"ping -c {scenario_time} {FILE_ip} > {numberOfClients}_scenario_normal/{scenario_time}sec_ms_ping_normal_{client}.txt &")
                
                else: # only one stream per client
                    net[client].cmd(f"iperf3 -c {server_ip} -p {port} -P {parallel_streams} -b {bandwidth} -t {scenario_time} --json > {numberOfClients}_scenario_normal/{scenario_time}sec_normal_{client}.json &")
                    net[client].cmd(f"ping -c {scenario_time} {FILE_ip} > {numberOfClients}_scenario_normal/{scenario_time}sec_ping_normal_{client}.txt &")
                
                port = port + 1 # Take the next free port
    
    
    '''
    3. Notfall – Netzwerk-Ausfall und Failover-Test (Geht nur bei neuer Topologie weil dynamisch routing)

    In einer Universität ist eine stabile Netzwerkverbindung essenziell, um Vorlesungen, Forschungsarbeiten und Verwaltungsaufgaben sicherzustellen. Doch was passiert, wenn ein zentraler Router oder ein wichtiger Link ausfällt?
    In diesem Szenario wird simuliert, dass ein zentraler Netzwerk-Knoten (z. B. der Haupt-Router im Rechenzentrum) plötzlich ausfällt.
    zB mit "link down" auf einem SDN-Switch einer Route und schauen was passiert.
    '''
def scenario_emergency(net, numberOfClients):
    print("[!] Implementation pending in new topology...")
    time.sleep(2)
    pass
    
    
    
    # Command (Bitrate/Throughput, Cwnd, CPU, Cong. Control Type): LN2C1 iperf -c SCC_N1 -p 5001 -t 60 -P 5 -V | tee results.csv
    # [CLIENT] iperf 3 -c [SERVER] -p [PORT] -t [TIME] -P [PARALLEL CONNECTIONS] -V Verbose für mehr Infos | tee [OUTPUT FILE]
    # Additional parameter -b 100M : Bandwidth 100M

    # Command (RTT min/avg/max/mdev): LN2C1 ping -c 10 SCC_N1 > rtt_log.txt

    # Command (Congestion Control Type): SCC_N1 sysctl net.ipv4.tcp_congestion_control
    # Zum ändern: sysctl -w net.ipv4.tcp_congestion_control=bbr (oder cubic, reno, etc.)

    # Command (Queue Size): SCC_N1 tc -s qdisc show 
    # tc -s qdisc show 


class CustomCLI(CLI):

    def do_debug(self, arg):
        """Toggle debug mode. Usage: debug 1 (enable) / debug 0 (disable)"""
        global debug
        if arg.strip() == "1":
            debug = 1
            print("[!] Debug mode enabled.")
        elif arg.strip() == "0":
            debug = 0
            print("[!] Debug mode disabled.")
        else:
            print("[!] Usage: debug 1 (enable) / debug 0 (disable)")
      
      
    def do_multistream(self, arg):
        """Toggle debug mode. Usage: debug 1 (enable) / debug 0 (disable)"""
        global multistream
        if arg.strip() == "1":
            multistream = 1
            print("[!] Multistream enabled.")
        elif arg.strip() == "0":
            multistream = 0
            print("[!] Multistream disabled.")
        else:
            print("[!] Usage: multistream 1 (enable) / multistream 0 (disable)")
            
                
    def do_scenario_time(self, arg):
        global scenario_time
        try:
            value = int(arg.strip())
            if 5 <= value:
                scenario_time = value
                print(f"[+] Scenario will run for {scenario_time} sec")
            else:
                print("[!] Scenario should run for at least 5 sec")
        except ValueError:
            print("[!] Invalid input. Usage: scenario_time [sec]")
    
    def do_scenario(self, arg):
        """Run a scenario. Usage: scenario 1"""
        if arg.strip() == "1":
            print("[+] Running scenario 'Backup-Welle am Abend'...")
            scenario_backup(self.mn, numberOfClients)
            print(f"[!] Don't terminate until simulation is over...(~{scenario_time}sec)")
            time.sleep(scenario_time+3)
            print("[+] Done.")
        elif arg.strip() == "2":
            print("[+] Running scenario 'Arbeitsalltag'...")
            scenario_normal(self.mn, numberOfClients)
            print(f"[!] Don't terminate until simulation is over...(~{scenario_time}sec)")
            time.sleep(scenario_time+3)
            print("[+] Done.")
        elif arg.strip() == "3":
            print("[+] Running scenario 'Notfall – Netzwerk-Ausfall und Failover-Test'...")
            scenario_emergency(self.mn, numberOfClients) 
              
        else:
            print("[!] Unknown scenario. Usage: scenario [1|2|3]")


def parse_arguments():
    parser = argparse.ArgumentParser(description="KIT Topology - Network Simulation")
    parser.add_argument("--clients", type=int, default=numberOfClients, help="Number of clients (default: 3)")
    return parser.parse_args()


def nettopo(**kwargs):
    topo = MyTopo()
    return Mininet(topo=topo, switch=OVSSwitch, controller=None, link=TCLink, **kwargs)

if __name__ == '__main__':
    args = parse_arguments()
    numberOfClients = args.clients  # Set the global based on the argument
    
    if numberOfClients < 1 or numberOfClients > 10:
        print("[!] Number of clients must be between 1 and 10")
        exit(1)
        
    lg.setLogLevel('info')
    net = nettopo()
    net.start()
    configure_switches(net)
    configure_routes(net)
    print(f"[+] Number of Clients (per Leaf): {numberOfClients}")
    print("[+] Number of Clients (total): ", numberOfClients * 7)
    # NOTE!
    # For our tests we use only the clients on 3 leaf pairs (LN2*, LN9*, LN12*) out of 7 (LN2*, LN9*, LN12*, LS2*, LS8*, LS9*, LS12*)
    # Because we run the tests on the North Campus network only!
    print("[?] Custom commands: debug [val], scenario [val], scenario_time [val], multistream [val]") # also --clients [val]
    CustomCLI(net)
    net.stop()
