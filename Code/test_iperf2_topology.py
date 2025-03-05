from mininet.net import Mininet
from mininet.topo import Topo
from mininet.node import OVSSwitch, Controller
from mininet.cli import CLI
import time
import os

# clears Mininet cache
os.system("sudo mn -c")



def run_iperf_test(n_clients=5, test_duration=10):
    class CustomTopo(Topo):
        """Simple topology with one switch, multiple clients and one server."""
        def build(self):
            switch = self.addSwitch('s1')
            server = self.addHost('h1')
            self.addLink(server, switch)
            
            for i in range(2, n_clients + 2):  # h2 to h(n+1)
                client = self.addHost(f'h{i}')
                self.addLink(client, switch)
    
    # Create network
    net = Mininet(topo=CustomTopo(), switch=OVSSwitch, controller=None)
    net.start()
    print("[DEBUG] Configurating switches...")
    # Set fail mode to standalone to prevent it from defaulting to secure mode
    os.system("sudo ovs-vsctl set-fail-mode s1 standalone")
    
    # Get server host
    server = net.get('h1')
    print(f"Starting iPerf server on {server.IP()}...")
    server.cmd('iperf -s &')  # iperf server
    time.sleep(2)  # Give some time for the server to start to avoid any race conditions
    
    # Check if server is actually running
    print(f"[DEBUG] Checking if iPerf server is running on {server.IP()}...")
    server_status = server.cmd("pgrep iperf")
    print(server_status)
    if not server_status.strip():  # If pgrep returns nothing, server is not running
        print("[ERROR] iPerf server is not running. Restarting...")
        server.cmd('iperf -s &')
        time.sleep(2)  # Give it time to start

    # Wait before starting clients to avoid again potential race conditions
    print("[INFO] Waiting 2 seconds before starting clients...")
    time.sleep(2)

    # Start clients
    print("Starting iPerf clients...")
    for i in range(2, n_clients + 2):
        client = net.get(f'h{i}')
        print(f"Client {client.name} ({client.IP()}) testing against {server.IP()}...")
        client.cmd(f'iperf -c {server.IP()} -B {client.IP()} -t {test_duration} -P 5 | tee {client.name}_result.txt')

    time.sleep(test_duration + 2)  # Wait for tests to complete
    print("iPerf tests completed.")
    
    # Drop into CLI for debugging (optional)
    CLI(net)
    
    # Stop network
    net.stop()
    print("Network stopped.")

if __name__ == "__main__":
    run_iperf_test(n_clients=5, test_duration=10)

