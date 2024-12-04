from mininet.topo import Topo
from mininet.log import setLogLevel
from mininet.net import Mininet
from mininet.cli import CLI
import argparse


# READ FIRST:
# Before starting the script, run "sudo mn -c" just in case to clear any cache 
# Running "sudo python3 topo_new.py" wont assign any hosts
# You can use "sudo python3 topo_new.py --num_hosts X" to assign X hosts for each leaf router

# [s1 ; s2] border routers (main routers)
# [s10 ; s99] leaf routers
# [s100 ; s103] north spine routers
# [s200 ; s203] south spine routers
# [s300 ; s30X] firewalls and other special(?) routers/servers



class CampusTopo(Topo):
    def __init__(self, num_hosts=0, **opts):
        
        self.num_hosts = num_hosts
        super().__init__(**opts)


    def build(self):
        # Border routers
        border_router_north = self.addSwitch('s1')
        border_router_south = self.addSwitch('s2')

        # Spine routers
        spine_routers_north = self.spine_routers_create(100, 4)
        spine_routers_south = self.spine_routers_create(200, 4)

        # Connect spine routers
        self.connect_all(spine_routers_north)
        self.connect_all(spine_routers_south)

        # Connect border routers to spine routers
        self.connect_to_spine(border_router_north, spine_routers_north)
        self.connect_to_spine(border_router_south, spine_routers_south)


        # Leaf routers, two lists that include all leaf routers - one for each campus
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
        
        #SCC Dienste Campus Nord connected to leaf_pair_north 1
        #Firewall Bypass connected to leaf_pair_north 1 & 3
        #LSDF connected to leaf_pair_north 3
        #Fileserver connected to leaf_pair_north 6
        #SCC Diense Campus Nord connected also to leaf_pair_north 10
        #bwcloud connected to leaf_pair_north 14
        
        #SCC Diense Campus Sud connected to leaf_pair_south 1
        #Firewall Bypass connected to leaf_pair_south 1 & 3
        #Institute Campus Sud connected to leaf_pair_south 2
        #VM connected to leaf_pair_south 6
        #SCC Dienste Campus Sud connected to leaf_pair_south 10
        
        # Add hosts to leaf routers if num_hosts > 0
        if self.num_hosts > 0:
            self.add_hosts_to_leaf_routers(leaf_pairs_north, self.num_hosts)
            self.add_hosts_to_leaf_routers(leaf_pairs_south, self.num_hosts)
        
        

#-----------------------------------------------------------------------#

    def spine_routers_create(self, base_id, count):
        return [self.addSwitch(f's{base_id + i}') for i in range(count)]

#-----------------------------------------------------------------------#

    def connect_all(self, routers):

        #Fully connect all routers in the given list

        for i, router1 in enumerate(routers):
            for router2 in routers[i + 1:]:
                self.addLink(router1, router2)

#-----------------------------------------------------------------------#

    def connect_to_spine(self, border_router, spine_routers):
        for spine_router in spine_routers:
            self.addLink(border_router, spine_router)

#-----------------------------------------------------------------------#

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

#-----------------------------------------------------------------------#

    def add_hosts_to_leaf_routers(self, leaf_pairs, n):
        for pair in leaf_pairs:
            for router in pair:
                for i in range(n):
                    host = self.addHost(f'h{i+1}')
                    self.addLink(router, host)
                    

topos = {'topo_new': (lambda: CampusTopo())}

if __name__ == '__main__':
    # Set up argument parser
    parser = argparse.ArgumentParser(description='Campus topology script idk')
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
    CLI(net)
    net.stop()

