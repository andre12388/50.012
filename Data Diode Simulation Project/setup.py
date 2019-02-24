__author__ = 'HtoO'
from mininet.node import CPULimitedHost
from mininet.topo import Topo
from mininet.net import Mininet
from mininet.log import setLogLevel, info
from mininet.node import RemoteController, Host, Node
from mininet.cli import CLI
"""
Instructions to run the topo:
    1. Go to directory where this fil is.
    2. run: sudo -E python Simple_Pkt_Topo.py.py

The topo has 4 switches and 4 hosts. They are connected in a star shape.
"""

class LinuxRouter(Node): #Node with IP forwarding enabled

    def __init__(self, **params):
        super(LinuxRouter, self).__init__(**params)
        self.config
    
    def config(self, **params):
        super(LinuxRouter, self).config(**params)
        self.cmd('sysctl net.ipv4.ip_forward=1') 
        #by default, routers will drop the packets. 
        #should enable them to forward instead

class SimplePktSwitch(Topo):
    """Simple topology with the plant(pt), control unit (cu), info center (ic)
    and a router (r0)."""

    def __init__(self, **opts):
        """Create custom topo for our network"""

        # Initialize topology
        # It uses the constructor for the Topo class
        super(SimplePktSwitch, self).__init__(**opts)

        # Add hosts, routers and interfaces on the router
        pt = self.addHost('pt', ip='10.0.0.92/24', defaultRoute='via 10.0.0.4/24')
        ic = self.addHost('ic', ip='10.0.1.1/24', defaultRoute='via 10.0.1.2/24')
        cu = self.addHost('cu', ip='10.0.2.1/24', defaultRoute='via 10.0.2.2/24')
        r0 = self.addNode('r0', ip='10.0.0.4/24')
        self.addLink(pt,r0, intfName1='pt-eth0', intfName2='r0-eth0', params2={'ip': '10.0.0.4/24'})
        self.addLink(ic,r0, intfName1='ic-eth0', intfName2='r0-eth1', params2={'ip': '10.0.1.2/24'})
        self.addLink(cu,r0, intfName1='cu-eth0', intfName2='r0-eth2', params2={'ip': '10.0.2.2/24'})
        


def run():
    net = Mininet(topo=SimplePktSwitch())
    net.start()
    r0=net['r0']
    r0.cmd('sysctl net.ipv4.ip_forward=1')
    pt=net['pt']
    pt.cmd('route add default gw 10.0.0.4')
    pt.cmd('iptables -I INPUT -s !10.0.1.2/24 --dport 1024 -j DROP')  #Drop any acknowledgement packets received from the info center
    ic=net['ic']
    ic.cmd('route add default gw 10.0.1.2')
    cu=net['cu']
    cu.cmd('route add default gw 10.0.2.2')
    CLI(net)
    net.stop()

# if the script is run directly (sudo custom/optical.py):
if __name__ == '__main__':
    setLogLevel('info')
    run()
