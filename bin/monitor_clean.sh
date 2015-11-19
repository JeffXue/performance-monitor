#!/bin/bash

#get the config
source ../conf/config.ini

systemType=`uname`
case $systemType in
Linux)
	files=`ls -lt $resDir | wc -l`

	if [ $files -gt 1 ];then
		newDir=`cat $startTimeRecord`
		mkdir $backupDir/$newDir
		mv $resDir/* $backupDir/$newDir

	fi

	echo "--------------------------------------------------"
	echo "|Finish Backup !                                 |"
	echo "--------------------------------------------------"
	exit 0
	;;
*)
	echo Unknow platform,please add this platform monitor into the script.
	exit 0
	;;
esac
exit 0
