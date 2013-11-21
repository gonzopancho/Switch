# -*- coding: utf-8 -*-

"""
 VLAN設定
"""
def allow_request(datapath, port_a, port_b, port_c, priority=0):
	ofproto     = datapath.ofproto
	parser      = datapath.ofproto_parser

