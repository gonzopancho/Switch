#!/usr/bin/env python
# -*- coding: utf-8 -*-
from webob.response import Response
from ryu.app.wsgi import ControllerBase, route
import json

#
# HttpController
# ユーザー認証及びMACアドレスの登録を行う
#
class HttpController(ControllerBase):
	def __init__(self, body, link, data, **config):
		super(HttpController, self).__init__(body, link, data, **config)

		# アプリケーションから渡されたコンテキストの取得
		self.controller = data['controller']
		self.dpset = data['dpset']

	#
	# HTTP のルーティングは @route デコレータで行う
	#
	@route('dp', '/add/{l2addr}', methods=['GET'], requirements={'l2addr': r'([a-fA-F0-9]{2}[:|\-]?){6}'})
	def index(self, req, l2addr, **_kwargs):
		value = self.controller.add_mac_flow(l2addr)
		json_str = json.dumps({"result" : value})

		return Response(status=200, body=json_str)

