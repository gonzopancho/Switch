#!/usr/bin/env python
# -*- coding: utf-8 -*-
import netifaces

#
# Linuxのみに対応(/proc/net/arp)
#
ARP_TABLE_PATH='/proc/net/arp'

#
# ARPキャッシュの取得
#
def getARPTable():
	arp_lines = open(ARP_TABLE_PATH).readlines()
	for arp_line in arp_lines[1:]:
		arp_split_line = arp_line.split()

		""" エラーチェック(もっと厳格に行うべき) """
		if (len(arp_split_line) != 6):
			continue

		""" IPアドレスとMACアドレスを返す """
		yield arp_split_line[0], arp_split_line[3]

#
# IPアドレスからMACアドレスを検索する
#
def MACAddressLookUp(ip_addr):
	#
	#  引数から取得したIPアドレスがARPテーブルのIPアドレスと同じであればMACアドレスを返す
	#
	for arp_ip, arp_mac in getARPTable():
		if arp_ip == ip_addr:
			return arp_mac
	return None

#
# インターフェイスからMACアドレスを検索する
#
def InterfaceMACAddressLookUp(interface_name):
	try:
		interface = netifaces.ifaddresses(interface_name)
		eth_frame = interface.get(netifaces.AF_LINK)[0]
		return eth_frame.get('addr')
	except:
		return False

#
# インターフェイスからMACアドレスを検索する
#
def InterfaceIPAddressLookUp(interface_name):
	try:
		interface = netifaces.ifaddresses(interface_name)
		eth_frame = interface.get(netifaces.AF_INET)[0]
		return eth_frame.get('addr')
	except:
		return False

#
# テストコード
#
if __name__ == "__main__":
	mac_addr = MACAddressLookUp("10.3.0.1")
	print mac_addr

	print InterfaceIPAddressLookUp('tap0')
	print InterfaceMACAddressLookUp('tap0')

