#!/bin/bash

SUDO=sudo

# root ユーザーの場合 sudo コマンドを抜かす
if [ $EUID -eq 0 ]; then
	SUDO=""
fi

# DevelopmentToolsのインストール
${SUDO} yum -y groupinstall "Development Tools"

# pip, virtualenv, fabricのインストール
${SUDO} yum -y install python-pip python-virtualenv fabric
${SUDO} yum -y install python-devel

# OpenFlow Switchのインストール
${SUDO} yum -y install openvswitch

# Open vSwitchの起動と自動起動設定
systemctl restart openvswitch.service
systemctl enable openvswitch.service

# Python-virtualenvを用いて仮想環境の作成
virtualenv --no-site-packages --clear .
source bin/activate

# Pythonライブラリの依存関係解決
pip install -r etc/requirements.txt

# vim: set nu ts=2 autoindent : #

