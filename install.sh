#!/bin/bash
SUDO=sudo

# root ユーザーの場合 sudo コマンドを抜かす
if [ $EUID -eq 0 ]; then
        SUDO=""
fi

# get linux distribution name
dist_name=`cat /etc/issue | awk '{print $1}'`
deploy_script="sbin/install/${dist_name,,}.sh"

# ディストリビューションのデプロイスクリプトの存在確認
if [ -f $deploy_script ]
then
	# get source
	source $deploy_script
else
	# error message
	echo "Deploy script($deploy_script) not found!!"
	exit
fi


