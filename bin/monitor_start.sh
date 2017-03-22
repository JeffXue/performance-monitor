#! /bin/bash

#导入配置参数
source ../conf/config.ini

#记录PID号
echo $$ > $pidRecord

function envError(){
	echo "---------------------Error------------------------"
	echo "--------------------------------------------------"
	echo "|performance_monitor can not start ...           |"
	echo "|make sure system has installed:                 |"
	echo "|1.sysstat                                       |"
	echo "|2.python                                        |"
	echo "|3.python-numpy                                  |"
	echo "|4.python-Matplotlib                             |"
	echo "|5.python-memcached                              |"
    echo "|6.python-requests                               |"
    echo "|7.MySQL-python                                  |"
	echo "--------------------------------------------------"
	exit 1
}

#判断是否已安装sar和python
if [ ! -f "/usr/bin/sar" ];then
	envError
elif [ ! -f "/usr/bin/python" ];then
	envError
fi

#操作记录
echo "`date`: $0 $@ "  >> $historyLog

function paraError(){
	echo "-----------------------------Error-----------------------------------"
	echo "---------------------------------------------------------------------"
	echo "Version: $version								                       "
	echo "parameter error                                                      "
	echo "./monitor_start.sh -i interval -c count [-t time] -f prefix_name     "
	echo "parameter:														   "
	echo "   -i    monitoring interval										   "
	echo "   -c    monitoring count          		    			           "
	echo "   -t    monitoring time(minute)							           "
	echo "         (If you set the -t ,the script ignore the -c parameter)     "
	echo "   -f    the prefix of the recording file					           "
	echo "         format: test-v1.0-dir (use '-' for separator, not '_' )     "
	echo "---------------------------------------------------------------------"
	exit 1
}

#解析输入参数
while getopts :i:c:t:f: args
do
    case $args in
    i)interval=$OPTARG
        ;;  
    c)count=$OPTARG
        ;;  
    t)monitorTime=$OPTARG
        ;;  
    f)prefix=$OPTARG
        ;;  
    \?)paraError
        exit;
    esac
done

#判断传入参数是否正确
if [ -z $interval ];then
    paraError
fi
if [ -z $prefix ];then
    paraError
fi
if [[ -z $count && -z $monitorTime ]];then
    paraError
fi

#-f 传入参数不能带下划线_
hostname=`hostname | sed 's/\//_/'`
fJudge=$(echo $prefix | grep "_")
if [[ "$fJudge" != "" ]];then
    paraError
else
    filename=$prefix"_"$hostname
fi

#若使用-t指定时长，将忽略-c参数
if [ ! -z $monitorTime ];then
    echo "using -t parameter, ignore -c parameter"
	count=$(($monitorTime*60/$interval))
fi

time=`date +%Y%m%d%H%M`
formatted_start_time=`date '+%Y-%m-%d %H:%M:%S'`

echo "--------------------------------------------------"
echo "|performance_monitor is going to start ...       |"
echo "--------------------------------------------------"
#################################################
#backup the old data 
#################################################
echo "--------------------------------------------------"
echo "|Auto Backup the old result                      |"
echo "--------------------------------------------------"
./monitor_clean.sh

echo $filename"_"$time > $startTimeRecord
startTime=`date +%s`
endTime=$(($startTime+($count*$interval)))

#监控进程时用于输出top监控菜单文件头
function monitorProcessTitle(){
    if [ $1 -eq 1 ];then
	    title=`top -n 1 -b | grep "PID USER"`
		echo `date +%H:%M:%S` `date +%P` $title Threads>> $resDir/$filename"_process_"$2"_"$time.txt
	else
		echo "[ERROR]Cat not monitor the $2, there are several pids of $2. monitor will exit"
		exit 0
	fi
}

#监控进程时用于输出监控数据，来源top数据和ps -mP
function monitorProcessData(){
    mpPsData=$(eval `eval echo '$'"processCommand$mpCount"`)
    mpPID=`echo $mpPsData |awk '{print $2}'`
    mpPIDNumber=`echo $mpPsData |awk '{print $2}' |wc -l`
    mpTopName=$(eval echo '$'"processTopName$mpCount")
    mpSelfName=$(eval echo '$'"processSelfName$mpCount")
    if [ $mpPIDNumber -eq 1 ];then
        processData=`top -p $mpPID -n 1 -b |grep -w $mpTopName `
        threadData=`ps -mP $mpPID |wc -l`
	    if [[ "$processData" != "" ]];then
	        echo `date +%H:%M:%S` `date +%P` $processData $threadData >> $resDir/$filename"_process_"$mpSelfName"_"$time.txt
	    fi
    else
        exit 0
    fi
}

#监控进程占用资源函数
function monitorProcess(){
	processNumber=$(($processNumber+1))
	
	#check the pid whether correct and create the file to record
	mpCount=1
	while [ $mpCount -lt $processNumber ]
	do 
        mpPsData=$(eval `eval echo '$'"processCommand$mpCount"`)
        mpPID=`echo $mpPsData |awk '{print $2}'`
        mpPIDNumber=`echo $mpPsData |awk '{print $2}' |wc -l`
        mpTopName=$(eval echo '$'"processTopName$mpCount")
        mpSelfName=$(eval echo '$'"processSelfName$mpCount")
        monitorProcessTitle $mpPIDNumber $mpSelfName
		mpCount=$(($mpCount+1))
	done

	#monitor the pid
	nowTime=`date +%s`
	while [ $nowTime -lt $endTime ]
	do
		mpCount=1
		while [ $mpCount -lt $processNumber ]
		do
            monitorProcessData $mpCount &
			mpCount=$(($mpCount+1))
		done
		sleep $interval
		nowTime=`date +%s`
	done
}


function dumpMysqlSlowLog(){
    $mysqlPath -h $mysqlIP -P $mysqlPort -u$mysqlUser -p$mysqlPassword -e"select * from mysql.slow_log where start_time >= '%formatted_start_time'" > $resDir/$filename"_mysql_slow_log_"$time.txt
}

function dumpMysqlProcessList(){
    $mysqlPath -h $mysqlIP -P $mysqlPort -u$mysqlUser -p$mysqlPassword -e"SELECT * FROM  information_schema.processlist" > $resDir/$filename"_mysql_process_list_"$time.txt
}

function killMysqlProcessList(){
    killSql=`$mysqlPath -h $mysqlIP -P $mysqlPort -u$mysqlUser -p$mysqlPassword -e"SELECT CONCAT('KILL ',id,';') FROM  information_schema.processlist WHERE Command='Query'" | grep -v CONCAT`
    $mysqlPath -h $mysqlIP -P $mysqlPort -u$mysqlUser -p$mysqlPassword mysql -e"$killSql"
}

#监控mysql线程函数
function monitorMysql(){
	echo `date +%H:%M:%S` `date +%P` Threads_connected > $resDir/$filename"_mysql_threads_"$time.txt
	nowTime=`date +%s`
	while [ $nowTime -lt $endTime ]
	do
		threads=`$mysqlPath -h $mysqlIP -P $mysqlPort -u$mysqlUser -p$mysqlPassword $mysqlDatabase -e"show global status like 'Threads_connected';" | grep Threads_connected |awk '{print $2}'`
		if [ ! -z $threads ];then
		    echo `date +%H:%M:%S` `date +%P` $threads >> $resDir/$filename"_mysql_threads_"$time.txt
		fi
		sleep $interval
		nowTime=`date +%s`
	done
	dumpMysqlSlowLog
	dumpMysqlProcessList
	killMysqlProcessList
}



#监控端口稳定连接数函数
function monitorNetstat(){
	echo `date +%H:%M:%S` `date +%P` ESTABLISHED > $resDir/$filename"_TCPPort_"$netstatPort"_"$time.txt
	nowTime=`date +%s`
	while [ $nowTime -lt $endTime ]
	do
	    netstatData=`netstat -lan |grep  ":$netstatPort" |grep ESTABLISHED |wc -l`
		echo `date +%H:%M:%S` `date +%P` $netstatData >> $resDir/$filename"_TCPPort_"$netstatPort"_"$time.txt
		sleep $interval
		nowTime=`date +%s`
	done
}

#监控socket不同状态数量函数
function monitorSocketStat(){
    echo `date +%H:%M:%S` `date +%P` LISTEN SYN-RECV ESTAB CLOSE-WAIT LAST_ACK FIN-WAIT-1 FIN-WAIT-2 CLOSING TIME_WAIT > $resDir/$filename"_SocketStat_"$time.txt
	nowTime=`date +%s`
	while [ $nowTime -lt $endTime ]
    do
	    ss -t -a |awk '{print $1}' |sort | uniq -c |sed 's/^[ \t]*//g' > socket_stat.txt
        listenNum=`grep LISTEN socket_stat.txt| awk '{print $1}'`
        synRecvNum=`grep SYN-RECV socket_stat.txt| awk '{print $1}'`
        estabNum=`grep ESTAB socket_stat.txt| awk '{print $1}'`
        closeWaitNum=`grep CLOSE-WAIT socket_stat.txt| awk '{print $1}'`
        lastAckNum=`grep LAST_ACK socket_stat.txt| awk '{print $1}'`
        finWait1Num=`grep FIN-WAIT-1 socket_stat.txt| awk '{print $1}'`
        finWait2Num=`grep FIN-WAIT-2 socket_stat.txt| awk '{print $1}'`
        closingNum=`grep CLOSING socket_stat.txt| awk '{print $1}'`
        timeWaitNum=`grep TIME_WAIT socket_stat.txt| awk '{print $1}'`

        if [ -z $listenNum ];then
            listenNum=0
        fi
        if [ -z $synRecvNum ];then
            synRecvNum=0
        fi
        if [ -z $estabNum ];then
            estabNum=0
        fi
        if [ -z $closeWaitNum ];then
            closeWaitNum=0
        fi
        if [ -z $lastAckNum ];then
            lastAckNum=0
        fi
        if [ -z $finWait1Num ];then
            finWait1Num=0
        fi
        if [ -z $finWait2Num ];then
            finWait2Num=0
        fi
        if [ -z $closingNum ];then
            closingNum=0
        fi
        if [ -z $timeWaitNum ];then
            timeWaitNum=0
        fi

		echo `date +%H:%M:%S` `date +%P` $listenNum $synRecvNum $estabNum $closeWaitNum $lastAckNum $finWait1Num $finWait2Num $closingNum $timeWaitNum >> $resDir/$filename"_SocketStat_"$time.txt
		sleep $interval
		nowTime=`date +%s`
	done
    rm -rf socket_stat.txt
}


#监控redis info函数
function monitorRedis(){
	echo `date +%H:%M:%S` `date +%P` connected_clients used_memory used_memory_peak total_commands_processed keyspace_hits keyspace_misses hit_rate instantaneous_ops_per_sec  > $resDir/$filename"_redis_"$time.txt
	nowTime=`date +%s`
	while [ $nowTime -lt $endTime ]
	do
        if [ -z $redisPassword ];then
	        $redisPath/redis-cli -h $redisIP -p $redisPort info > redis_info.txt
        else
            $redisPath/redis-cli -h $redisIP -p $redisPort -a $redisPassword info > redis_info.txt
        fi
	    connectedClients=`grep connected_clients redis_info.txt|cut -f2 -d':'|sed 's/\r//g'`
        usedMemory=`grep used_memory: redis_info.txt|cut -f2 -d":" |sed 's/\r//g'`
        usedMemoryPeak=`grep used_memory_peak: redis_info.txt|cut -f2 -d":" |sed 's/\r//g'`
        totalCommandsProcessed=`grep total_commands_processed redis_info.txt|cut -f2 -d":" |sed 's/\r//g'`
        keyspaceHits=`grep keyspace_hits redis_info.txt|cut -f2 -d":" |sed 's/\r//g'`
        keyspaceMisses=`grep keyspace_misses redis_info.txt|cut -f2 -d":" |sed 's/\r//g'`
        instantaneousOpsPerSec=`grep instantaneous_ops_per_sec redis_info.txt|cut -f2 -d":" |sed 's/\r//g'`

        oldRecord=`tail -1 $resDir/$filename"_redis_"$time.txt |grep -v connected`
        if [ ! -z "$oldRecord" ];then
            oldKeyspaceHits=`echo $oldRecord |cut -f7 -d" "`
            oldKeyspaceMisses=`echo $oldRecord |cut -f8 -d" "`
            realKeyspaceHits=$(($keyspaceHits-$oldKeyspaceHits))
            realKeyspaceMisses=$(($keyspaceMisses-$oldKeyspaceMisses))
        else
            realKeyspaceHits=$keyspaceHits
            realKeyspaceMisses=$keyspaceMisses
        fi
        keyspace=$(($realKeyspaceHits+$realKeyspaceMisses))
        if [ $realKeyspaceHits -eq 0 -o $keyspace -eq 0 ];then
            hitRate=0
        else
            hitRate=$(($realKeyspaceHits*100/$keyspace))
        fi
		echo `date +%H:%M:%S` `date +%P` $connectedClients $usedMemory $usedMemoryPeak $totalCommandsProcessed $keyspaceHits $keyspaceMisses $hitRate $instantaneousOpsPerSec >> $resDir/$filename"_redis_"$time.txt
		sleep $interval
		nowTime=`date +%s`
	done
	rm -rf redis_info.txt
}

#监控memcached stat函数
function monitorMemcached(){
    echo `date +%H:%M:%S` `date +%P` curr_connections cmd_get cmd_set cmd_flush get_hits get_misses hit_rate bytes_read bytes_written limit_maxbytes accepting_conns threads bytes curr_items total_items evictions > $resDir/$filename"_memcached_"$time.txt
	python monitor_memcached.py $memcachedIP $memcachedPort $interval $endTime $resDir/$filename"_memcached_"$time.txt $memcachedUser $memcachedPasswd
}

#监控mongodb stat函数
function monitorMongoDB(){
    echo `date +%H:%M:%S` `date +%P` `$mongodbPath/mongostat -h $mongodbIP --port $mongodbPort -u $mongodbUser -p $mongodbPassword --authenticationDatabase $authenticationDatabase --all -n 1 1  |grep -w insert |grep -v connected` > $resDir/$filename"_mongodb_"$time.txt
	nowTime=`date +%s`
	while [ $nowTime -lt $endTime ]
	do
        echo `date +%H:%M:%S` `date +%P` `$mongodbPath/mongostat -h $mongodbIP --port $mongodbPort -u $mongodbUser -p $mongodbPassword --authenticationDatabase $authenticationDatabase --noheaders --all -n 1 |grep -v connected`   >> $resDir/$filename"_mongodb_"$time.txt &
        sleep $interval
		nowTime=`date +%s`
    done
}

#监控apache状态页面函数
function monitorApache(){
    echo `date +%H:%M:%S` `date +%P` currently_processed idle_worker waiting_for_connection starting_up reading_request sending_reply keepalive_read dns_lookup closing_connection logging gracefully_finishing idle_cleanup_of_worker open_slot_with_no_current_process > $resDir/$filename"_apache_"$time.txt
	python monitor_apache.py $apacheURL $interval $endTime $resDir/$filename"_apache_"$time.txt $apacheUser $apachePassword
}

#监控tomcat状态页面函数
function monitorTomcat(){
    tomcatNumber=$(($tomcatNumber+1))
    mtCount=1
    while [ $mtCount -lt $tomcatNumber ]
    do
        tomcatType=$(eval echo '$'"tomcatType$mtCount")
        tomcatURL=$(eval echo '$'"tomcatURL$mtCount")
        tomcatMonitorSign=$(eval echo '$'"tomcatMonitorSign$mtCount")
        tomcatUser=$(eval echo '$'"tomcatUser$mtCount")
        tomcatPassword=$(eval echo '$'"tomcatPassword$mtCount")
        tomcatSelfName=$(eval echo '$'"tomcatSelfName$mtCount")
        if [[ "$tomcatType" == "tomcat6"  ]];then
            tomcatResFile=$resDir/$filename"_tomcat6_"$tomcatSelfName"_"$time.txt
            echo `date +%H:%M:%S` `date +%P` free_memory total_memory max_threads current_thread_count current_thread_busy max_processing_time processing_time  > $tomcatResFile
            python monitor_tomcat.py $tomcatURL $interval $endTime $tomcatResFile $tomcatMonitorSign $tomcatType $tomcatSelfName $tomcatUser $tomcatPassword &
        fi
        if [[ "$tomcatType" == "tomcat7"  ]];then
            tomcatResFile=$resDir/$filename"_tomcat7_"$tomcatSelfName"_"$time.txt
            echo `date +%H:%M:%S` `date +%P` free_memory total_memory %ps_eden_space %ps_old_gen %ps_survivor_space max_threads current_thread_count current_thread_busy max_processing_time processing_time  > $tomcatResFile
            python monitor_tomcat.py $tomcatURL  $interval $endTime $tomcatResFile $tomcatMonitorSign $tomcatType $tomcatSelfName $tomcatUser $tomcatPassword &
        fi
        mtCount=$(($mtCount+1))
    done
}

#监控nginx状态页面函数
function monitorNginx(){
    echo `date +%H:%M:%S` `date +%P` active_connections handled_connections handled_handshake handled_requests reading writing waiting > $resDir/$filename"_nginx_"$time.txt
    python monitor_nginx.py $nginxURL $interval $endTime $resDir/$filename"_nginx_"$time.txt
}

systemType=`uname`
case $systemType in
Linux)
	echo "--------------------------------------------------"
	echo "|Starting Linux monitor......                    |"
	echo "--------------------------------------------------"
	echo "please don't kill the monitor process which running in the background"

	#############################################
	#monitor common resource
	#############################################
	if [ $serverSourceFlag -eq 1 ];then
		sar $interval $count > $resDir/$filename"_server_cpu_"$time.txt &
		sar $interval $count -r > $resDir/$filename"_server_memory_"$time.txt &
		sar -B $interval $count > $resDir/$filename"_server_paging_"$time.txt &
		sar -dp $interval $count > $resDir/$filename"_server_block_"$time.txt &
		sar -n DEV $interval $count > $resDir/$filename"_server_network_"$time.txt &
		sar -n SOCK $interval $count > $resDir/$filename"_server_socket_"$time.txt &
		sar -W $interval $count > $resDir/$filename"_server_swapping_"$time.txt &
		sar -b $interval $count > $resDir/$filename"_server_io_rate_"$time.txt &
		sar -v $interval $count > $resDir/$filename"_server_inode_"$time.txt &
		sar -q $interval $count > $resDir/$filename"_server_queue_load_"$time.txt &
	fi

	if [ $netstatFlag -eq 1 ];then
		monitorNetstat &
	fi

	if [ $socketFlag -eq 1 ];then
		monitorSocketStat &
	fi
	
	if [ $processFlag -eq 1 ];then
		monitorProcess &
	fi
	
	if [ $mysqlFlag -eq 1 ];then
		monitorMysql &
	fi

    if [ $redisFlag -eq 1 ];then
        monitorRedis &
    fi

    if [ $memcachedFlag -eq 1 ];then
        monitorMemcached &
    fi

    if [ $mongodbFlag -eq 1 ];then
        monitorMongoDB &
    fi

    if [ $apacheFlag -eq 1 ];then
        monitorApache &
    fi

    if [ $tomcatFlag -eq 1 ];then
        monitorTomcat &
    fi

    if [ $nginxFlag -eq 1 ];then
        monitorNginx &
    fi
	#############################################
	#wait for monitor finish
	#############################################
	delay=$(($interval*$count))
	sleep $delay
	runFlag=1
	while [ $runFlag -eq 1 ]
	do
		sleep $interval
		checkFlag=`ps -ef |grep -w $$ |grep -v grep |wc -l`
		if [ $checkFlag -lt 3 ];then
			runFlag=0
		else
			runFlag=1
		fi
	done


	#############################################
	#split the network information into eth0/1
	#############################################
	if [ $serverSourceFlag -eq 1 ];then
		if [ ! -f $interface1 ];then
			cat $resDir/$filename"_server_network_"$time.txt | head -3 > $resDir/$interface1.txt
			cat $resDir/$filename"_server_network_"$time.txt | grep $interface1 >> $resDir/$interface1.txt
			mv $resDir/$interface1.txt $resDir/$filename"_server_"$interface1"_"$time.txt
		fi

		if [ ! -f $interface2 ];then
			cat $resDir/$filename"_server_network_"$time.txt | head -3 > $resDir/$interface2.txt
			cat $resDir/$filename"_server_network_"$time.txt | grep $interface2 >> $resDir/$interface2.txt
			mv $resDir/$interface2.txt $resDir/$filename"_server_"$interface2"_"$time.txt
		fi
	fi


	#############################################
	#analyse data
	#############################################
	echo "Start analyse the data"
	endTime=`date +%Y%m%d%H%M`
	python analyse.py $filename $endTime

	echo "Finish analyse the data"
	echo "Check the data and graph in result directory"
	echo "Finish monitor at `date`"  >> $historyLog
	exit 0
	;;
*)
	echo Unknow platform,please add this platform monitor into the script.
	exit 0
	;;

esac
exit 0

