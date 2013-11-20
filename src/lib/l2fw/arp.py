# -*- coding: utf-8 -*-
import socket

"""
 ARPクエリを通す
"""
def allow_request(datapath, port_a, port_b, port_c, priority=0):
	ofproto     = datapath.ofproto
	parser      = datapath.ofproto_parser

	match_a = parser.OFPMatch(in_port=port_a, eth_type=0x806)
	match_b = parser.OFPMatch(in_port=port_b, eth_type=0x806)
	match_c = parser.OFPMatch(in_port=port_c, eth_type=0x806)

	actions_a = [parser.OFPActionOutput(port_b), parser.OFPActionOutput(port_c)]
	actions_b = [parser.OFPActionOutput(port_c), parser.OFPActionOutput(port_a)]
	actions_c = [parser.OFPActionOutput(port_a), parser.OFPActionOutput(port_b)]

	inst_a = [parser.OFPInstructionActions(ofproto.OFPIT_APPLY_ACTIONS, actions_a)]
	inst_b = [parser.OFPInstructionActions(ofproto.OFPIT_APPLY_ACTIONS, actions_b)]
	inst_c = [parser.OFPInstructionActions(ofproto.OFPIT_APPLY_ACTIONS, actions_c)]

	mod_a = parser.OFPFlowMod(datapath=datapath, priority=priority, match=match_a, instructions=inst_a)
	mod_b = parser.OFPFlowMod(datapath=datapath, priority=priority, match=match_b, instructions=inst_b)
	mod_c = parser.OFPFlowMod(datapath=datapath, priority=priority, match=match_c, instructions=inst_c)

	datapath.send_msg(mod_a)
	datapath.send_msg(mod_b)
	datapath.send_msg(mod_c)

