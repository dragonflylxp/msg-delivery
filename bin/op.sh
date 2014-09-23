#!/bin/sh

function restart(){
    stop
    sleep 3
    path=`pwd`
    cd $path
    python26 main.py -c /home/www/lixiaopeng/github/msg-delivery/conf/delivery.conf  &
    #cd /home/www/lixiaopeng/ios-pushserver/bin
    #nohup python26 main.py -c ../conf/push.conf  > /dev/null &
}

function start(){
    restart    
}

function stop(){
    ps -ef |grep main.py|grep -v vim|grep -v grep|awk '{print $2}'|xargs kill > /dev/null 
}

function usage(){
    echo "[Usage:] sh op.sh start/stop/restart"
}

if [ $# -eq 0 ];then
    usage
elif [ $1 == "start" ];then
    echo "Starting..."
    start
    echo "Done"
elif [ $1 == "stop" ];then
    echo "Stopping..."
    stop
    echo "Done"
elif [ $1 == "restart" ];then
    echo "Restarting..."
    restart
    echo "Done"
else
    usage
fi
