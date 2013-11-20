# -*- coding: utf-8 -*-

class Datapath:
	# コンストラクタ
	def __init__(self, datapath):
		# 初期化
		self.port_no_set = dict()
		self.port_mac_set = dict()

		# データパスIDの設定及び、ポートの設定
		self.dp = datapath
		self.id = datapath.id
		for no, port in datapath.ports.items():
			self.set_port_no(port.name, no)
			self.set_port_no(port.hw_addr, no)

	# 生のデータパスを返す
	def get_raw_datapath(self):
		return self.dp

	# ポート名:ポート番号で登録
	def set_port_no(self, name, port_no):
		self.port_no_set[name] = port_no

	# ポート名からポート番号を返す
	def get_port_no(self, name):
		if name in self.port_no_set:
			return self.port_no_set[name]
		return False

	# MAC ADDRESS:ポート番号で登録
	def set_port_mac_addr(self, name, mac_addr):
		self.port_mac_set[name] = mac_addr

	# ポート名からMACアドレスを返す
	def get_port_mac_addr(self, name):
		if name in self.port_mac_set:
			return self.port_mac_set[name]

	# データパスのポートを列挙
	def show(self):
		for name in self.port_no_set:
			print name, self.port_no_set[name]

