import time, math
from ryu.base import app_manager
from ryu.controller import ofp_event, dpset
from ryu.controller.handler import MAIN_DISPATCHER
from ryu.controller.handler import set_ev_cls
# from ryu.lib.ip import ipv4_to_bi

class Controller(app_manager.RyuApp):
    
    def addHostIPRule(self, switchObj, hostID, outPort):
		destHostIP = "10.0.0.%d" % hostID
		ofproto = switchObj.ofproto

        # Send the ARP/IP packets to the proper host
        match = switchObj.ofproto_parser.OFPMatch(dl_type=0x806, nw_dst=destHostIP)
        action = switchObj.ofproto_parser.OFPActionOutput(outPort)
        mod = switchObj.ofproto_parser.OFPFlowMod(
                datapath=switchObj, match=match, cookie=0,
                command=ofproto.OFPFC_ADD, idle_timeout=0, hard_timeout=0,
                priority=1100,
                flags=ofproto.OFPFF_SEND_FLOW_REM, actions=[action])
        switchObj.send_msg(mod)
		print "hostID: ", hostID
		print "outPort: ", outPort
		print action

        match = switchObj.ofproto_parser.OFPMatch(dl_type=0x800, nw_dst=destHostIP)
        action = switchObj.ofproto_parser.OFPActionOutput(outPort)
        mod = switchObj.ofproto_parser.OFPFlowMod(
                datapath=switchObj, match=match, cookie=0,
                command=ofproto.OFPFC_ADD, idle_timeout=0, hard_timeout=0,
                priority=1000,
                flags=ofproto.OFPFF_SEND_FLOW_REM, actions=[action])
        switchObj.send_msg(mod)

    def addInPortRule(self, switchObj, inPort, outPort):
		ofproto = switchObj.ofproto

        # Send the ARP/IP packets to the proper host
        match = switchObj.ofproto_parser.OFPMatch(in_port=inPort, dl_type=0x806)
        action = switchObj.ofproto_parser.OFPActionOutput(outPort)
        mod = switchObj.ofproto_parser.OFPFlowMod(
                datapath=switchObj, match=match, cookie=0,
                command=ofproto.OFPFC_ADD, idle_timeout=0, hard_timeout=0,
                priority=1500,
                flags=ofproto.OFPFF_SEND_FLOW_REM, actions=[action])
        switchObj.send_msg(mod)

		print "inPort: ", inPort
		print "outPort: ", outPort
		print action

	# Match IP Packets
        match = switchObj.ofproto_parser.OFPMatch(in_port=inPort, 
						dl_type=0x800)
						
        action = switchObj.ofproto_parser.OFPActionOutput(outPort)
        mod = switchObj.ofproto_parser.OFPFlowMod(
                datapath=switchObj, match=match, cookie=0,
                command=ofproto.OFPFC_ADD, idle_timeout=0, hard_timeout=0,
                priority=1400,
                flags=ofproto.OFPFF_SEND_FLOW_REM, actions=[action])
        switchObj.send_msg(mod)

    def prepareCore(self, sw, sName, k):
		print "Setting Core Rule for switch ", sName
		if k > 2:
			hostsPerPod = (k ** 3 / 4) / k
			for i in range(k ** 3 / 4):
				op = i / hostsPerPod + 1
				self.addHostIPRule(switchObj=sw,
					hostID=i+1,
					outPort=(op))
		else:
			self.addHostIPRule(switchObj=sw,
				hostID=2,
				outPort=2)
			self.addHostIPRule(switchObj=sw,
				hostID=1,
				outPort=1)
		print
		print

    def prepareEdge(self, sw, sName, k):
#       add rule for packets going up
		print "Setting Edge Rule for switch ", sName 

		def isInMicroPod(sNum, hNum, k):
			hostOffset = (k / 2) * sNum
			rng = [i for i in range(hostOffset, hostOffset + (k / 2))]
			return hNum in rng

		sNum = int(sName[2:])
		hostOffset = (k / 2) * sNum
		for i in range(k ** 3 / 4):
			if isInMicroPod(sNum, i, k):
				self.addHostIPRule(sw,
					hostID=(i + 1),
					outPort=(i - hostOffset + 1))
			else:
				self.addHostIPRule(sw,
					hostID=(i+1),
					outPort=k)
		
		print
		print

    def prepareAgg(self, sw, sName, k):
#       add rule for packets going up
		print "Setting Agg Rule for switch", sName
		print "Up Rule"
		
		def isInPod(sNum, hNum, k):
			pod = int(math.ceil(sNum / (k / 2)))
			hostsPerPod = ( k ** 3 ) / 4 / k
			hostOffset = pod * hostsPerPod
			rng = [i for i in range(hostOffset, hostOffset + hostsPerPod)]
			return hNum in rng
			
		sNum = int(sName[2:])
		pod = int(math.ceil(sNum / (k / 2)))
		hostsPerPod = ( k ** 3 ) / 4 / k
		hostOffset = pod * hostsPerPod
		for i in range(k ** 3 / 4):
			print i
			if isInPod(sNum, i, k):
				hostNumInPod = i - hostOffset
				switchesPerPod = k / 2
				outPort = hostNumInPod / switchesPerPod + 1
				self.addHostIPRule(sw,
						hostID=(i + 1),
						outPort=(outPort))
			else:
				self.addHostIPRule(sw,
						hostID=(i+1),
						outPort=(k))
		print 
		print 

    def prepareSwitch(self, sw, numPorts):
		if len(sw.ports) > 0:
			switchName = sw.ports[1].name.split("-")[0]
			sType = switchName[1]
			if sType == "e":
				self.prepareEdge(sw, switchName, numPorts)
			elif sType == "a":
				self.prepareAgg(sw, switchName, numPorts)
			elif sType == "c":
				self.prepareCore(sw, switchName, numPorts)

    @set_ev_cls(dpset.EventDP)
    def switchStatus(self, ev):
		numPorts = len(ev.dp.ports) - 1
		self.prepareSwitch(ev.dp, numPorts)



