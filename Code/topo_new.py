from mininet.topo import Topo
from mininet.log import setLogLevel
from mininet.net import Mininet
from mininet.cli import CLI
from mininet.node import Host

import argparse


# READ FIRST:
# Before starting the script, run "sudo mn -c" just in case to clear any cache
# Running "sudo python3 topo_new.py" wont assign any hosts
# You can use "sudo python3 topo_new.py --num_hosts X" to assign X hosts for each leaf router

# [s1 ; s2] border routers (main routers)
# [s10 ; s99] leaf routers
# [s100 ; s103] north spine routers
# [s200 ; s203] south spine routers
# [s300 ; s30X] firewalls and other special(?) routers
# [h0 ; h9 ] service servers

# Commands:
# "hX iperf -s &" host X now operates as server, listens for incomming traffic
# "hY iperf -c hX -t 10 -d" host Y connects to host X and both exchange data
#


class CampusTopo(Topo):
    def __init__(self, num_hosts=0, **opts):

        self.num_hosts = num_hosts
        super().__init__(**opts)


    def build(self):
        # Border routers
        border_router_north = self.addSwitch('s1')
        border_router_south = self.addSwitch('s2')

        # Spine routers
        spine_routers_north = self.create_spine_routers(100, 4)
        spine_routers_south = self.create_spine_routers(200, 4)

        # Connect spine routers
        self.connect_all(spine_routers_north)
        self.connect_all(spine_routers_south)

        # Connect border routers to spine routers
        self.connect_to_spine(border_router_north, spine_routers_north)
        self.connect_to_spine(border_router_south, spine_routers_south)


        # Leaf routers, two lists, one for each campus
        leaf_pairs_north = self.create_and_connect_leaf_pairs(10, 14, spine_routers_north)
        leaf_pairs_south = self.create_and_connect_leaf_pairs(50, 10, spine_routers_south)

        # Firewalls
        firewall_north = self.addSwitch('s300')
        firewall_south = self.addSwitch('s301')
        self.addLink(firewall_north, border_router_north)
        # Firewall_north connected also to leaf_pair_north 10
        self.addLink(firewall_north, leaf_pairs_north[9][0])
        self.addLink(firewall_north, leaf_pairs_north[9][1])

        self.addLink(firewall_south, border_router_south)
        # Firewall_south connected also to leaf_pair_south 10
        self.addLink(firewall_south, leaf_pairs_south[9][0])
        self.addLink(firewall_south, leaf_pairs_south[9][1])

        # Firewall bypass routers(?)
        firewall_bypass_north = self.addSwitch('s302')
        # Link to pair 1
        self.addLink(firewall_bypass_north, leaf_pairs_north[0][0])
        self.addLink(firewall_bypass_north, leaf_pairs_north[0][1])
        # Link to pair 3
        self.addLink(firewall_bypass_north, leaf_pairs_north[2][0])
        self.addLink(firewall_bypass_north, leaf_pairs_north[2][1])

        firewall_bypass_south = self.addSwitch('s303')
        # Link to pair 1
        self.addLink(firewall_bypass_south, leaf_pairs_south[0][0])
        self.addLink(firewall_bypass_south, leaf_pairs_south[0][1])
        # Link to pair 3
        self.addLink(firewall_bypass_south, leaf_pairs_south[2][0])
        self.addLink(firewall_bypass_south, leaf_pairs_south[2][1])

        # Firewall Bypass connected to leaf_pair_north 1 & 3
        # Firewall Bypass connected to leaf_pair_south 1 & 3

        # All of following hosts operate as servers
        service_servers = self.create_service_servers(leaf_pairs_north, leaf_pairs_south)
        #self.activate_service_servers(service_servers)

        # Add hosts to leaf routers if num_hosts > 0
        if self.num_hosts > 0:
            self.add_hosts_to_leaf_routers(leaf_pairs_north, self.num_hosts)
            self.add_hosts_to_leaf_routers(leaf_pairs_south, self.num_hosts)

    #def activate_service_servers(self, service_servers):
    #    for server_name in service_servers:
    #        print(f"Activating iperf server on {server_name}")
    #        # start the iperf server in background
    #        server = net.get(server_name)
    #        server.cmd('iperf -s &') # server is of type str but it should be an object to work....

    def create_service_servers(self, leaf_pairs_north, leaf_pairs_south):
        service_servers = []

        #SCC Dienste Campus Nord connected to leaf_pair_north 1, 10
        SCC_north = self.addHost('h1')

        print(f"{SCC_north} of type {type(SCC_north)}")
        self.addLink(SCC_north, leaf_pairs_north[0][0])
        self.addLink(SCC_north, leaf_pairs_north[0][1])
        self.addLink(SCC_north, leaf_pairs_north[9][0])
        self.addLink(SCC_north, leaf_pairs_north[9][1])
        service_servers.append(SCC_north)

        #Institute Campus Nord connected to leaf_pair_north 2
        institute_north = self.addHost('h2')
        self.addLink(institute_north, leaf_pairs_north[1][0])
        self.addLink(institute_north, leaf_pairs_north[1][1])
        service_servers.append(institute_north)

        #LSDF connected to leaf_pair_north 3
        LSDF = self.addHost('h3')
        self.addLink(LSDF, leaf_pairs_north[2][0])
        self.addLink(LSDF, leaf_pairs_north[2][1])
        service_servers.append(LSDF)

        #Fileserver connected to leaf_pair_north 6
        fileserver = self.addHost('h4')
        self.addLink(fileserver, leaf_pairs_north[5][0])
        self.addLink(fileserver, leaf_pairs_north[5][1])
        service_servers.append(fileserver)

        #bwcloud connected to leaf_pair_north 14
        bwcloud = self.addHost('h5')
        self.addLink(bwcloud, leaf_pairs_north[13][0])
        self.addLink(bwcloud, leaf_pairs_north[13][1])
        service_servers.append(bwcloud)

        #SCC Diense Campus Sud connected to leaf_pair_south 1, 10
        SCC_south = self.addHost('h6')
        self.addLink(SCC_south, leaf_pairs_south[0][0])
        self.addLink(SCC_south, leaf_pairs_south[0][1])
        self.addLink(SCC_south, leaf_pairs_south[9][0])
        self.addLink(SCC_south, leaf_pairs_south[9][1])
        service_servers.append(SCC_south)

        #Institute Campus Sud connected to leaf_pair_south 2
        institute_south = self.addHost('h7')
        self.addLink(institute_south, leaf_pairs_south[1][0])
        self.addLink(institute_south, leaf_pairs_south[1][1])
        service_servers.append(institute_south)

        #VM connected to leaf_pair_south 6
        VM = self.addHost('h8')
        self.addLink(VM, leaf_pairs_south[5][0])
        self.addLink(VM, leaf_pairs_south[5][1])
        service_servers.append(VM)

        return service_servers

    def create_spine_routers(self, base_id, count):
        return [self.addSwitch(f's{base_id + i}') for i in range(count)]

    def connect_all(self, routers):

        #Fully connect all routers in the given list

        for i, router1 in enumerate(routers):
            for router2 in routers[i + 1:]:
                self.addLink(router1, router2)

    def connect_to_spine(self, border_router, spine_routers):
        for spine_router in spine_routers:
            self.addLink(border_router, spine_router)

    def create_and_connect_leaf_pairs(self, start_id, n, spine_routers):
        leaf_pairs = []
        for i in range(n):
            leaf1 = self.addSwitch(f's{start_id + 2 * i}')
            leaf2 = self.addSwitch(f's{start_id + 2 * i + 1}')
            self.addLink(leaf1, leaf2)  # Connect the pair
            for spine_router in spine_routers:
                self.addLink(leaf1, spine_router)
                self.addLink(leaf2, spine_router)
            leaf_pairs.append((leaf1, leaf2))
        return leaf_pairs

    def add_hosts_to_leaf_routers(self, leaf_pairs, n):
        host_counter = 10 #enables unique host names for each host
        for pair in leaf_pairs:
            for router in pair:
                for i in range(n):
                    host = self.addHost(f'h{host_counter}')
                    self.addLink(router, host)
                    host_counter += 1


class CustomCLI(CLI):

#Note: atm hosts are reachable if they are connected to the same leaf router; otherwise are unreachable
    def do_check_latency(self, line):
        args = line.split()
        if len(args) == 0: #no arguments
            print("[+] Checking latency between all hosts...")
            result = self.mn.pingAll()
            print(f"Average latency: {result} % packet loss")
        elif len(args) == 2:
            src, dest = args[0], args[1]
            print(f"[+] Checking latency between {src} and {dest}...")
            host_src = self.mn.get(src)
            host_dest = self.mn.get(dest)
            try:
                result = host_src.cmd(f"ping -c 4 {host_dest.IP()}") #4 pings is general practice
                print(f"[+] {host_src}->{host_dest}\n{result}")
                result = host_dest.cmd(f"ping -c 4 {host_src.IP()}")
                print(f"[+] {host_dest}->{host_src}\n{result}")
            except Exception as e:
                print(f"[!] Error: {e}")
        else:
            print("[?] Usage: check_latency [<src> <dest>]")

#Note: make dest host operate as server when performing iperf otherwise it wont work. also dont make all hosts act as servers, it is more convinient, however it will impact the overall performance significantly
    def do_check_bw(self, line):
        args = line.split()
        if len(args) == 0:
            print("[+] Checking bandwidth between all hosts...")
            try:
                result = self.mn.iperf()
                print(f"[+] Bandwidth:\n{result}")
            except Exception as e:
                print(f"[!] Error: {e}")
        elif len(args) == 2:
            src, dest = args[0], args[1]
            print(f"[+] Checking bandwidth between {src} and {dest}...")
            try:
                host_src = self.mn.get(src)
                host_dest = self.mn.get(dest)
                host_dest.cmd("iperf -s &") #make host act as server
                result = host_src.cmd(f"iperf -c {host_dest.IP()} -t 10")
                print(f"[+] {host_src}->{host_dest}\n{result}")
                host_dest.cmd("pkill iperf") #close iperf
                
            except Exception as e:
                print(f"[!] Error: {e}")
        else:
            print("[?] Usage: check_bw [<src> <dest>]")


topos = {'topo_new': (lambda: CampusTopo())}

if __name__ == '__main__':
    # Set up argument parser
    parser = argparse.ArgumentParser(description='Campus topology script')
    parser.add_argument(
        '--num_hosts',
        type=int,
        default=0,
        help='Number of hosts to attach to each router'
    )
    args = parser.parse_args()

    # Set log level and create topology with the provided number of hosts
    setLogLevel('info')
    topo = CampusTopo(num_hosts=args.num_hosts)
    net = Mininet(topo=topo)
    net.start()
    CustomCLI(net)
    net.stop()

