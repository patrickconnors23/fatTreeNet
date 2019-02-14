from mininet.topo import Topo

class FatTreeTopo(Topo):
    def __init__(self, k):
        Topo.__init__(self)
	self.counter = 0
        podNum = k
        numHosts = k ** 3 / 4
        numCoreSwitches = ( k / 2 ) ** 2
        numAggSwitches = (k / 2) * k
        numEdgeSwitches = (k / 2) * k
        linksPerPod = numEdgeSwitches / podNum

        # Build Core Switches
        self.coreSwitches = [self.addCustomSwitch("c", coreId) for coreId in range(numCoreSwitches)]
        print("Core switches: ",len(self.coreSwitches))

        # Build Aggregate Switches
        self.aggSwitches = [self.addCustomSwitch("a", aggId) for aggId in range(numAggSwitches)]
        print("Agg switches: ",len(self.aggSwitches))
            
        # Build Edge Switches
        self.edgeSwitches = [self.addCustomSwitch("e", edgeId) for edgeId in range(numEdgeSwitches)]
        print("Edge switches: ",len(self.edgeSwitches))

        # Build Hosts
        self.hosts_ = [self.addHost('h%d' % hostId, ip='10.0.0.%d' % (hostId+1)) for hostId in range(numHosts)]

        # Link Hosts to Edge
	# High host port num, low edge port num
        hostsToEdge = numHosts / numEdgeSwitches
        for i in range(numEdgeSwitches):
            for j in range(hostsToEdge):
                self.addLink(self.edgeSwitches[i], self.hosts_[i*hostsToEdge + j], j + 1, 0)
	

        # Link edge to Agg
	# High edge port num, low agg port num
	edgePortsAlloc = hostsToEdge
        for i in range(podNum):
            podOffset = linksPerPod * i
            for j in range(linksPerPod):
                for z in range(linksPerPod):
                    self.addLink(self.edgeSwitches[podOffset + j], self.aggSwitches[podOffset + z], edgePortsAlloc + z + 1, j + 1)

        # Link Agg to Core
	# High Agg port num, core port num depends on pod
	aggPortsAlloc = hostsToEdge
        for i in range(podNum):
            podOffset = linksPerPod * i
            for j in range(linksPerPod):
                for z in range(linksPerPod):
                    self.addLink(self.aggSwitches[podOffset + j], self.coreSwitches[j * linksPerPod + z], aggPortsAlloc + z + 1, i + 1)

    def addCustomSwitch(self, switchType, ID):
	self.counter += 1
	return self.addSwitch("s"+switchType+str(ID), dpid=str(self.counter), protocols="OpenFlow10")

    @classmethod
    def create(cls, count):
        return cls(count)

topos = {'fat_topo': FatTreeTopo.create}
