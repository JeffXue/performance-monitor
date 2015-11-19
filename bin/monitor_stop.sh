#!/bin/bash

#get the config
source ../conf/config.ini

systemType=`uname`
case $systemType in
Linux)
	PID=`cat $pidRecord`
	echo $PID
	PIDS=`ps -ef |grep $PID |grep -v grep |awk '{print $2}'`
	echo $PIDS
	PIDSNumber=`ps -ef |grep $PID |grep -v grep |awk '{print $2}'|wc -l`
	while [ $PIDSNumber -gt 0 ]
	do
		kill -9 $PIDS
		PIDSNumber=`ps -ef |grep $PID |grep -v grep |awk '{print $2}'|wc -l`
	done
	echo The performance monitor have stopped!
	exit 0
	;;
*)
	echo Unknow platform,please add this platform monitor into the script.
	exit 0
	;;
esac
exit 0
