# -*- coding: utf-8 -*-
from ryu.lib.mac import haddr_to_bin

"""
 パッチパネルの操作
"""
def patch(datapath, port_a, port_b, priority=0):
	ofproto     = datapath.ofproto
	parser      = datapath.ofproto_parser

	match_a = parser.OFPMatch(in_port=port_a)
	match_b = parser.OFPMatch(in_port=port_b)

	inst_a = [parser.OFPInstructionActions(ofproto.OFPIT_APPLY_ACTIONS, [parser.OFPActionOutput(port_b)])]
	inst_b = [parser.OFPInstructionActions(ofproto.OFPIT_APPLY_ACTIONS, [parser.OFPActionOutput(port_a)])]

	mod_a = parser.OFPFlowMod(datapath=datapath, priority=priority, match=match_a, instructions=inst_a)
	mod_b = parser.OFPFlowMod(datapath=datapath, priority=priority, match=match_b, instructions=inst_b)

	datapath.send_msg(mod_a)
	datapath.send_msg(mod_b)

"""
 パッチパネルの操作
"""
def rewrite_gw_patch(datapath, auth_ip, auth_mac, gw_ip, gw_mac, port_a, port_g, priority=0):
	ofproto     = datapath.ofproto
	parser      = datapath.ofproto_parser

	"""
	GUESTLAN -> AUTHLAN 認証サーバ意外へのパケットは全てMACアドレスを書き換えて、認証サーバへ
	AUTHLAN -> GUESTLAN 認証サーバ意外へ宛先が向いていたパケットをゲートウェイのMACアドレスに書き換え返す

	(アプローチ)
	1.認証サーバへのリクエストエントリを追加
	2.認証サーバをGWとすり替えるエントリの追加
	"""

	"""	
	1.認証サーバへのリクエストエントリを追加
	"""
	match_a = parser.OFPMatch(in_port=port_a, eth_type=0x800, ipv4_src=auth_ip)
	match_g = parser.OFPMatch(in_port=port_g, eth_type=0x800, ipv4_dst=auth_ip)

	inst_a = [parser.OFPInstructionActions(ofproto.OFPIT_APPLY_ACTIONS, [parser.OFPActionOutput(port_g)])]
	inst_g = [parser.OFPInstructionActions(ofproto.OFPIT_APPLY_ACTIONS, [parser.OFPActionOutput(port_a)])]

	mod_a = parser.OFPFlowMod(datapath=datapath, priority=priority + 1, match=match_a, instructions=inst_a)
	mod_g = parser.OFPFlowMod(datapath=datapath, priority=priority + 1, match=match_g, instructions=inst_g)

	datapath.send_msg(mod_a)
	datapath.send_msg(mod_g)

	"""
	2.認証サーバをGWとすり替えるエントリの追加
	"""
	match_a = parser.OFPMatch(in_port=port_a, eth_type=0x800)
	match_g = parser.OFPMatch(in_port=port_g, eth_type=0x800)

	action_a = parser.OFPMatchField.make(ofproto.OXM_OF_ETH_SRC, haddr_to_bin(gw_mac))
	action_g = parser.OFPMatchField.make(ofproto.OXM_OF_ETH_DST, haddr_to_bin(auth_mac))

	actions_a = [parser.OFPActionSetField(action_a), parser.OFPActionOutput(port_g)]
	actions_g = [parser.OFPActionSetField(action_g), parser.OFPActionOutput(port_a)]

	inst_a = [parser.OFPInstructionActions(ofproto.OFPIT_APPLY_ACTIONS, actions_a)]
	inst_g = [parser.OFPInstructionActions(ofproto.OFPIT_APPLY_ACTIONS, actions_g)]

	mod_a = parser.OFPFlowMod(datapath=datapath, priority=priority, match=match_a, instructions=inst_a)
	mod_g = parser.OFPFlowMod(datapath=datapath, priority=priority, match=match_g, instructions=inst_g)

	datapath.send_msg(mod_a)
	datapath.send_msg(mod_g)

"""
 MACアドレスのパッチパネル操作
"""
def add_mac_patch(datapath, port_a, port_b, mac_addr, priority=0):
	ofproto     = datapath.ofproto
	parser      = datapath.ofproto_parser
 
	match_a = parser.OFPMatch(in_port=port_a, eth_dst=mac_addr)
	match_b = parser.OFPMatch(in_port=port_b, eth_src=mac_addr)

	inst_a = [parser.OFPInstructionActions(ofproto.OFPIT_APPLY_ACTIONS, [parser.OFPActionOutput(port_b)])]
	inst_b = [parser.OFPInstructionActions(ofproto.OFPIT_APPLY_ACTIONS, [parser.OFPActionOutput(port_a)])]

	mod_a = parser.OFPFlowMod(datapath=datapath, priority=priority, match=match_a, instructions=inst_a)
	mod_b = parser.OFPFlowMod(datapath=datapath, priority=priority, match=match_b, instructions=inst_b)

	datapath.send_msg(mod_a)
	datapath.send_msg(mod_b)

"""
 IPアドレスのパッチパネル操作
"""
def add_ip_patch(datapath, port_a, port_b, ip_addr, priority=0):
	ofproto     = datapath.ofproto
	parser      = datapath.ofproto_parser
 
	match_a = parser.OFPMatch(in_port=port_a, eth_type=0x800, ipv4_src=ip_addr)
	match_b = parser.OFPMatch(in_port=port_b, eth_type=0x800, ipv4_dst=ip_addr)

	inst_a = [parser.OFPInstructionActions(ofproto.OFPIT_APPLY_ACTIONS, [parser.OFPActionOutput(port_b)])]
	inst_b = [parser.OFPInstructionActions(ofproto.OFPIT_APPLY_ACTIONS, [parser.OFPActionOutput(port_a)])]

	mod_a = parser.OFPFlowMod(datapath=datapath, priority=priority, match=match_a, instructions=inst_a)
	mod_b = parser.OFPFlowMod(datapath=datapath, priority=priority, match=match_b, instructions=inst_b)

	datapath.send_msg(mod_a)
	datapath.send_msg(mod_b)

