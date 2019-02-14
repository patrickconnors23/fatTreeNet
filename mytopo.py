from mininet.topo import Topo

class MyTopo(Topo):
    def __init__(self, count):
        Topo.__init__(self)
        vertexCount = count
	self.counter = 1

	self.addHost("h0")
	self.addHost("h1")
	self.AS("se0")
#	self.AS("se1")
#	self.AS("sa0")
#	self.AS("sa1")
#	self.AS("sc0")
	self.addLink("h0","se0", 1, 2)
	self.addLink("h1","se0", 1, 1)
#	self.addLink("se0","sa0")
#	self.addLink("se1","sa1")
#	self.addLink("sa0","sc0")
#	self.addLink("sa1","sc0")
    def AS(self, name):
	self.addSwitch(name, dpid=str(self.counter))
	self.counter += 1

    @classmethod
    def create(cls, count):
        return cls(count)

topos = {'top': MyTopo.create}
