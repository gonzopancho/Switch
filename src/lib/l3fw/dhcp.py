# -*- coding: utf-8 -*-
import socket

"""
 DHCPクエリを通す
"""
def allow_request(datapath, sw_port_dst, sw_port_src, priority=0):
	allow_udp_request(datapath, sw_port_dst, sw_port_src, priority)

"""
PORTA(UDP:68) <- PORTB(UDP:67)
 PORTBからPORTAへのudpの68番ポートのみ許可
"""
def allow_udp_request(datapath, port_a, port_b, priority):
	ofproto     = datapath.ofproto
	parser      = datapath.ofproto_parser

	match_a = parser.OFPMatch(in_port=port_a, eth_type=0x800, ip_proto=socket.IPPROTO_UDP, udp_src=67)
	match_b = parser.OFPMatch(in_port=port_b, eth_type=0x800, ip_proto=socket.IPPROTO_UDP, udp_dst=67)

	inst_a = [parser.OFPInstructionActions(ofproto.OFPIT_APPLY_ACTIONS, [parser.OFPActionOutput(port_b)])]
	inst_b = [parser.OFPInstructionActions(ofproto.OFPIT_APPLY_ACTIONS, [parser.OFPActionOutput(port_a)])]

	mod_a = parser.OFPFlowMod(datapath=datapath, priority=priority, match=match_a, instructions=inst_a)
	mod_b = parser.OFPFlowMod(datapath=datapath, priority=priority, match=match_b, instructions=inst_b)

	datapath.send_msg(mod_a)
	datapath.send_msg(mod_b)

