# -*- coding: utf-8 -*-
import sys
from datastore.mysql import Terminal
from datastore.mysql import getMySQLSession

"""
 Configulation File Setting
"""
from os.path import abspath, dirname
from ConfigParser import SafeConfigParser
config = SafeConfigParser()
config_file = abspath(dirname(abspath(__file__)) + '../../etc/authhub.conf')
config.read(config_file)

"""
 OpenFlow Ryu COntroller
"""
from ryu.base import app_manager
from ryu.controller import dpset
from ryu.controller.handler import CONFIG_DISPATCHER
from ryu.controller.handler import set_ev_cls
from ryu.controller import ofp_event
from ryu.ofproto import ofproto_v1_3
from ryu.app.wsgi import WSGIApplication
from interface.http import HttpController

"""
 Tuntunkun Utility
"""
from util.datapath import Datapath
from lib.switch import patch, rewrite_gw_patch, add_ip_patch
from lib.switch import add_mac_patch, remove_mac_patch
from lib.l2fw import arp
from lib.l3fw import dns, dhcp
from lib.net import interface

class AuthHub(app_manager.RyuApp):
	# Open flow version configuration
	OFP_VERSIONS = [ofproto_v1_3.OFP_VERSION]

	# このアプリケーションが必要とするコンテキストのクラス
        # 実際に使うインスタンスはコンストラクタにインジェクトされる
	_CONTEXTS = {
		'dpset'	: dpset.DPSet,
		'wsgi'	: WSGIApplication,
	}

	# コンストラクタ
	def __init__(self, *args, **kwargs):
		# AuthHub初期化
		super(AuthHub, self).__init__(*args, **kwargs)
		self.datapath = None

		# MySQL
		self.mysql_username = config.get('MySQL', 'username', False)
		self.mysql_hostname = config.get('MySQL', 'hostname', False)
		self.mysql_password = config.get('MySQL', 'password', False)
		self.mysql_database = config.get('MySQL', 'database', False)

		# ネットワークの設定を取得
		self.net_lan	= config.get('DEFAULT', 'net_lan', False)
		self.net_auth	= config.get('DEFAULT', 'net_auth', False)
		self.net_guest	= config.get('DEFAULT', 'net_guest', False)

		# 認証サーバのMACアドレス, IPアドレス取得
		self.net_auth_ip = interface.InterfaceIPAddressLookUp(self.net_auth)
		self.net_auth_mac = interface.InterfaceMACAddressLookUp(self.net_auth)

		# 認証サーバのMACアドレス, IPアドレス取得
		self.net_gw_ip = config.get('DEFAULT', 'netgw_l3_addr', False)
		self.net_gw_mac = config.get('DEFAULT', 'netgw_l2_addr', False)

		# -HTTPインターフェイス-
		#
		# API を実装したコントローラを WSGIApplication に登録する
		# ここでいうコントローラは OpenFlow コントローラのそれではなく
		# MVC モデルでいうところのコントローラ
		wsgi = kwargs['wsgi']
		wsgi.register(HttpController)

		# コントローラのコンテキストを設定する
		# コントローラは API の呼び出し毎にインスタンス化されるので
		# 永続化が必要な情報はコンテキストとして渡す必要がある
		controller_context = {
			'controller'	: self,
			'dpset'		: kwargs['dpset'],
			'net_lan'	: self.net_lan,
			'net_auth'	: self.net_auth,
		}
		wsgi.registory[HttpController.__name__] = controller_context

	@set_ev_cls(ofp_event.EventOFPPortDescStatsReply, CONFIG_DISPATCHER)
	def multipart_reply_handler(self, ev):
		#
		#  今回のコントローラではデータパス一つにしか対応しないため
		# 接続可能なOpenFlow Switchは一台まで
		#
		if self.datapath == None:
			# データパスの設定
			self.datapath = Datapath(ev.msg.datapath)

			# インタフェイス名からポート番号の取得
			lan_port	= self.datapath.get_port_no(self.net_lan)
			auth_port	= self.datapath.get_port_no(self.net_auth)
			guest_port	= self.datapath.get_port_no(self.net_guest)

			# IPアドレスによる仮想的な結線を行う
			add_ip_patch(ev.msg.datapath, auth_port, guest_port, self.net_auth_ip, priority=200)

			# ゲートウェイのすり替えを行う
			rewrite_gw_patch(
				ev.msg.datapath, auth_port, guest_port,
				self.net_auth_mac, self.net_gw_mac,
				priority=1)

			# 仮想的に結線を行う
			patch(ev.msg.datapath, auth_port, guest_port, priority=0)

			# ARPを通す
			arp.allow_request(ev.msg.datapath, lan_port, auth_port, guest_port, priority=200)

			# DNSとDHCPリクエストのみを通す
			dns.allow_request(ev.msg.datapath, lan_port, guest_port, priority=10)
			dhcp.allow_request(ev.msg.datapath, lan_port, guest_port, priority=10)

			# Show Switch Connection Message
			print "SWITCH JOINED"

			# Get MySQL Session
			session = getMySQLSession(
				self.mysql_username, self.mysql_hostname,
				self.mysql_password, self.mysql_database)
			for terminal in session.query(Terminal).filter_by(enabled=True):
				print "ACCEPT %s: %s" %(terminal.name, terminal.l2addr)
				self.add_mac_flow(terminal.l2addr)

	#
	# MACアドレスの登録処理(HTTPDインターフェイスから呼び出される)
	#
	def add_mac_flow(self, mac_addr):
		# データパスが存在しない場合は、何もしない
		if self.datapath == None:
			return False

		# 生のデータパス取得
		datapath	= self.datapath.get_raw_datapath()

		# インタフェイス名からポート番号の取得
		lan_port	= self.datapath.get_port_no(self.net_lan)
		auth_port	= self.datapath.get_port_no(self.net_auth)
		guest_port	= self.datapath.get_port_no(self.net_guest)

		# MACアドレスによる仮想的な結線を行う
		add_mac_patch(datapath, lan_port, guest_port, mac_addr, priority=100)
		return True

	#
	# MACアドレスの消去処理(HTTPDインターフェイスから呼び出される)
	#
	def remove_mac_flow(self, mac_addr):
		# データパスが存在しない場合は、何もしない
		if self.datapath == None:
			return False

		# 生のデータパス取得
		datapath	= self.datapath.get_raw_datapath()

		# インタフェイス名からポート番号の取得
		lan_port	= self.datapath.get_port_no(self.net_lan)
		auth_port	= self.datapath.get_port_no(self.net_auth)
		guest_port	= self.datapath.get_port_no(self.net_guest)

		# MACアドレスによる仮想的な結線を消去
		remove_mac_patch(datapath, lan_port, guest_port, mac_addr, priority=100)
		return True

if __name__ == '__main__':
	import sys
	from ryu.cmd import manager

	sys.argv.append(__name__)
	manager.main()

