#!/bin/bash

# pip, virtualenv, fabricのインストール
${SUDO} apt-get install -y python-pip python-virtualenv fabric
${SUDO} install python-dev libmysqlclient-dev

# OpenSSHのインストール
${SUDO} apt-get install -y openssh-server

# OpenFlow Switchのインストール
${SUDO} apt-get install -y openvswitch-switch

# Python-virtualenvを用いて仮想環境の作成
virtualenv --no-site-packages --clear .
source bin/activate

# Pythonライブラリの依存関係解決
pip install -r etc/requirements.txt

# Ryuの設定ファイルにシンボリックリンクを張る
if [ ! -e ./etc/default.conf ]; then
	pushd ./etc
		ln -s ./ryu/ryu.conf default.conf
	popd
fi

# vim: set nu ts=2 autoindent : #

