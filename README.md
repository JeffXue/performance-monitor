##Performance Monitor##
performance monitor用于监控linux服务器中的资源情况，包括：
* server_cpu    --  服务器CPU资源情况（sar）
    * `iowait(%) --  iowait占用CPU百分比，一般不应该超过30% `
    * `system(%) --  内核空间占用CPU百分比`
    * `used(%)   --  100%-idle(%)`
    * `user(%)   --  用户空间占用CPU百分比`
* server_eth0   --  服务器网卡eth0资源情况（sar -n DEV）
    * `rx/s(MB/s)    --  接收速度`
    * `tx/s(MB/s)    --  发送速度`
* server_eth1   --  服务器网卡eth1资源情况（sar -n DEV）
    * `rx/s(MB/s)    --  接收速度`
    * `tx/s(MB/s)    --  发送速度`
* server_io_rate    --  服务器IO资源情况（sar -b）
    * `read/s(MB)    --  每秒物理设备读取数据总量`
    * `wrtn/s(MB)    --  每秒物理设备写入数据总量`
    * `tps           --  每秒物理设备IO操作次数(Total number of transfers per second that were issued to physical devices)`
* server_memory --  服务器内存资源情况（sar -r）
    * `buffers(MB)   --  内核缓冲区占用内存大小`
    * `cached(MB)    --  内核高速缓存数据占用内存大小`
    * `memfree(MB)   --  空闲内存大小`
    * `memused(MB)   --  已使用内存大小`
    * `memused(%)    --  已使用内存百分比`
    * `memused--(%)  --  (memused-cached-buffers)*100%/(memfree+memused)`
* server_queue_load --  服务器CPU负载情况（sar -q）
    * `ldavg-1       --  1分钟load平均值`
    * `ldavg-5       --  5分钟load平均值`
    * `ldavg-15      --  15分钟load平均值`
    * `plist-ze      --  队列中的进程和线程数量`
* server_socket --  服务器socket资源情况（sar -n SOCK）
    * `totsck        --  总的socket数量`
    * `tcpsck        --  tcp连接socket数量`
    * `udpsck        --  udp连接socket数量`
* process_xxx  --  进程占用资源情况（top, ps -mP）
    * `CPU(%)        --  占用CPU百分比（每个核占用百分比之和）`
    * `MEM(%)        --  占用物理内存百分比`
    * `Threads       --  进程对应线程数`
* mysql --  mysql数据库连接数（show global status like 'Threads_connected';）
    * `Threads_connected `
* redis --  redis信息（redis info）
    * `connected_clients         --  客户端连接数`
    * `hit_rate                  --  命中率（keyspace_hits*100%/(keyspace_hits+keyspace_misses)）`
    * `instantaneous_ops_per_sec --  每秒处理请求数量`
    * `keyspace_hits             --  总命中数量`
    * `keyspace_misses           --  总不命中数量`
    * `total_commands_processed  --  总的请求数量`
    * `use_memory(MB)            --  使用内存大小`
    * `use_memory_peak(MB)       --  使用的最大内存大小`
* memcached --memcached状态（client.get_stats()）
    * `accepting_conns   --  接收的请求数`
    * `bytes             --  处理的字节数量`
    * `bytes_read        --  读操作的字节数量`
    * `bytes_written     --  写操作的字节数量`
    * `cmd_flush         --  flush命令总请求数量`
    * `cmd_get           --  get命令总请求数量`
    * `cmd_set           --  set命令总请求数量`
    * `curr_connections  --  当前打开这的连接数`
    * `curr_items        --  当前存储的items数量`
    * `evictions         --  为了获取空闲内存而删除的items数`
    * `get_hits          --  总命中次数`
    * `get_misses        --  总不命中次数`
    * `hit_rate          --  命中率（get_hits*100%/（get_hits+get_misses））`
    * `limit_maxbytes    --  分配给memcached内存大小`
    * `threads           --  当前线程数`
    * `total_items       --  从服务启动以后存储的items总数量`
* mongodb   --  mongodb信息（mongostat）
    * `conn            --  当前连接数`
    * `delete          --  每秒删除次数`
    * `faults          --  每秒访问失败数`
    * `flushes         --  每秒执行fsync将数据写入硬盘的次数`
    * `getmore         --  每秒执行getmore次数`
    * `insert          --  每秒插入次数`
    * `mapped(MB)      --  所有的被mmap的数据量`
    * `non-mapped(MB)  --  MongoDB's internal data structures and threads'stacks, essentially anything not backed by files on disk`
    * `query           --  每秒查询数量`
    * `res(MB)         --  物理内存使用量`
    * `update          --  每秒更新次数`
    * `vsize(MB)       --  虚拟内存使用量`
* apache    --apache状态（status页面）
    * `closing_connection                  --  关闭连接状态（C）`
    * `currently_processed                 --  近期处理的请求数量`
    * `dns_lookup                          --  正在查找DNS状态（D）`
    * `gracefully_finishing                --  进入正常结束程序中状态（G）`
    * `idle_cleanup_of_worker              --  处理闲置状态（I）`
    * `idle_worker                         --  空闲线程`
    * `keepalive_read                      --  处于保持联机的状态（K）`
    * `logging                             --  正在写入日志文件`
    * `open_slot_with_no_current_process`
    * `reading_request                     --  正在读取请求状态（R）`
    * `sending_reply                       --  正在发送回应（W）`
    * `starting_up                         --  启动中（S）`
    * `waiting_for_connection              --  等待连接中（_）`
* tomcat    --tomcat状态（status页面）
    * `free_memory              --  空闲内存`
    * `total_memory             --  总的使用内存`
    * `%ps_eden_space           --  年轻代（Eden Space）使用百分比`
    * `%ps_old_gen              --  年老代使用百分比`
    * `%ps_survivor_space       --  年轻代(Suvivor Space)使用百分比`
    * `max_threads              --  最大线程数量`
    * `current_thread_count     --  近期线程数量`
    * `current_thread_busy      --  近期忙线程数量`
    * `max_processing_time      --  最大处理时间`
    * `processing_time          --  处理时间`
* nginx --  nginx状态（status页面）
    * `active_connections    --  激活的连接数`
    * `handled_connections   --  处理的连接数`
    * `handled_handshake     --  处理的握手数`
    * `handled_requests      --  处理的请求数`
    * `reading               --  读取操作`
    * `waiting               --  等待操作`
    * `writing               --  写入操作`


##安装步骤##
- 编译安装python2.7+，setuptools和pip
- apt-get install freetype*
- apt-get install libpng*
- apt-get install sysstat
- apt-get install mysql libmysqld-dev
- pip2.7 install virtualenv (可选，若需要在python虚拟环境中运行，则需安装）
- pip2.7 install -r requirements.txt


##使用方法##
   配置config目录下的config.ini和report.ini
   
   cd performance_monitor/bin 
   
   ./monitor_start.sh -i interval -c count [-t time] -f prefix_name
   
   参数说明:                                                         
      -i    采样间隔                                           
      -c    采样次数                                           
      -t    采样时长(如果你使用了-t设置时长 ,脚本将会忽略-c采样次数)     
      -f    数据文件名前缀 例子: test-v1.0-api (使用'-'作为分隔符，请勿使用'_' ) 
    结束后可到result目录中查看对应的输出表单和数据


##样例##

<html>
<meta http-equiv="Content-Type" content="text/html; charset=utf-8"/>
<body>
<div align="center">
<p><strong>服务器系统信息</strong></p>
    <table border="0" cellpadding="5" cellspacing="2"  width="50%" align="center">
        <tr>
            <th>监控时间段</th>
            <td>2015-11-19_20:06~2015-11-19_20:08</td>
        </tr>
        <tr>
            <th>主机名</th>
            <td>performanceTest</td>
        </tr>
        <tr>
            <th>内核版本</th>
            <td>Linux version 2.6.32-5-amd64 </td>
        </tr>
        <tr>
            <th>CPU</th>
            <td>2  Intel(R) Core(TM) i5-4590 CPU @ 3.30GHz</td>
        </tr>
        <tr>
            <th>内存</th>
            <td>4048224 kB</td>
        </tr>
        </table>
    <p></p>
    <p><strong>服务器资源使用情况汇总 (test-v1.0-api) </strong></p>
    <table border="0" cellpadding="5" cellspacing="2"  width="60%" align="center">
    <tr>
        <th>Item</th>
        <th>Type</th>
        <th>Min</th>
        <th>Max</th>
        <th>Avg</th>
        <th>90%小于</th>
    </tr>
    <tr>
        <th rowspan="4">server_cpu</th>
        <td><a href="sample/test-v1.0-api_performanceTest_server_cpu_201511192006-iowait.png" target="_png">iowait(%)</a></td>
        <td>0.0</td>
        <td>7.5</td>
        <td>0.07</td>
        <td>0.0</td>
    </tr>
    <tr>
        <td><a href="sample/test-v1.0-api_performanceTest_server_cpu_201511192006-system.png" target="_png">system(%)</a></td>
        <td>12.5</td>
        <td>21.11</td>
        <td>16.42</td>
        <td>18.09</td>
    </tr>
    <tr>
        <td><a href="sample/test-v1.0-api_performanceTest_server_cpu_201511192006-used.png" target="_png">used(%)</a></td>
        <td>13.43</td>
        <td>26.34</td>
        <td>17.34</td>
        <td>19.31</td>
    </tr>
    <tr>
        <td><a href="sample/test-v1.0-api_performanceTest_server_cpu_201511192006-user.png" target="_png">user(%)</a></td>
        <td>0.0</td>
        <td>8.06</td>
        <td>0.85</td>
        <td>1.98</td>
    </tr>
    <tr>
        <th rowspan="2">server_eth0</th>
        <td><a href="sample/test-v1.0-api_performanceTest_server_eth0_201511192006-rx(MB).png" target="_png">rx/s(MB)</a></td>
        <td>0.0</td>
        <td>0.0</td>
        <td>0.0</td>
        <td>0.0</td>
    </tr>
    <tr>
        <td><a href="sample/test-v1.0-api_performanceTest_server_eth0_201511192006-tx(MB).png" target="_png">tx/s(MB)</a></td>
        <td>0.0</td>
        <td>0.01</td>
        <td>0.0</td>
        <td>0.01</td>
    </tr>
    <tr>
        <th rowspan="3">server_io_rate</th>
        <td><a href="sample/test-v1.0-api_performanceTest_server_io_rate_201511192006-read(MB).png" target="_png">read/s(MB)</a></td>
        <td>0.0</td>
        <td>0.0</td>
        <td>0.0</td>
        <td>0.0</td>
    </tr>
    <tr>
        <td><a href="sample/test-v1.0-api_performanceTest_server_io_rate_201511192006-tps.png" target="_png">tps</a></td>
        <td>0.0</td>
        <td>43.0</td>
        <td>4.24</td>
        <td>15.0</td>
    </tr>
    <tr>
        <td><a href="sample/test-v1.0-api_performanceTest_server_io_rate_201511192006-wrtn(MB).png" target="_png">wrtn/s(MB)</a></td>
        <td>0.0</td>
        <td>0.2</td>
        <td>0.02</td>
        <td>0.09</td>
    </tr>
    <tr>
        <th rowspan="6">server_memory</th>
        <td><a href="sample/test-v1.0-api_performanceTest_server_memory_201511192006-memused.png" target="_png">memused(%)</a></td>
        <td>97.66</td>
        <td>97.69</td>
        <td>97.67</td>
        <td>97.68</td>
    </tr>
    <tr>
        <td><a href="sample/test-v1.0-api_performanceTest_server_memory_201511192006-memused--.png" target="_png">memused--(%)</a></td>
        <td>82.48</td>
        <td>82.5</td>
        <td>82.49</td>
        <td>82.5</td>
    </tr>
    <tr>
        <td><a href="sample/test-v1.0-api_performanceTest_server_memory_201511192006-buffers(MB).png" target="_png">buffers(MB)</a></td>
        <td>35.62</td>
        <td>35.82</td>
        <td>35.72</td>
        <td>35.81</td>
    </tr>
    <tr>
        <td><a href="sample/test-v1.0-api_performanceTest_server_memory_201511192006-cached(MB).png" target="_png">cached(MB)</a></td>
        <td>564.32</td>
        <td>564.43</td>
        <td>564.37</td>
        <td>564.41</td>
    </tr>
    <tr>
        <td><a href="sample/test-v1.0-api_performanceTest_server_memory_201511192006-memfree(MB).png" target="_png">memfree(MB)</a></td>
        <td>91.51</td>
        <td>92.48</td>
        <td>91.94</td>
        <td>92.18</td>
    </tr>
    <tr>
        <td><a href="sample/test-v1.0-api_performanceTest_server_memory_201511192006-memused(MB).png" target="_png">memused(MB)</a></td>
        <td>3860.86</td>
        <td>3861.84</td>
        <td>3861.4</td>
        <td>3861.74</td>
    </tr>
    <tr>
        <th rowspan="4">server_queue_load</th>
        <td><a href="sample/test-v1.0-api_performanceTest_server_queue_load_201511192006-ldavg-1.png" target="_png">ldavg-1</a></td>
        <td>0.02</td>
        <td>0.19</td>
        <td>0.08</td>
        <td>0.15</td>
    </tr>
    <tr>
        <td><a href="sample/test-v1.0-api_performanceTest_server_queue_load_201511192006-ldavg-15.png" target="_png">ldavg-15</a></td>
        <td>0.01</td>
        <td>0.02</td>
        <td>0.01</td>
        <td>0.02</td>
    </tr>
    <tr>
        <td><a href="sample/test-v1.0-api_performanceTest_server_queue_load_201511192006-ldavg-5.png" target="_png">ldavg-5</a></td>
        <td>0.03</td>
        <td>0.06</td>
        <td>0.05</td>
        <td>0.05</td>
    </tr>
    <tr>
        <td><a href="sample/test-v1.0-api_performanceTest_server_queue_load_201511192006-plist-sz.png" target="_png">plist-sz</a></td>
        <td>623.0</td>
        <td>633.0</td>
        <td>632.92</td>
        <td>633.0</td>
    </tr>
    <tr>
        <th rowspan="3">server_socket</th>
        <td><a href="sample/test-v1.0-api_performanceTest_server_socket_201511192006-tcpsck.png" target="_png">tcpsck</a></td>
        <td>38.0</td>
        <td>38.0</td>
        <td>38.0</td>
        <td>38.0</td>
    </tr>
    <tr>
        <td><a href="sample/test-v1.0-api_performanceTest_server_socket_201511192006-totsck.png" target="_png">totsck</a></td>
        <td>573.0</td>
        <td>579.0</td>
        <td>578.95</td>
        <td>579.0</td>
    </tr>
    <tr>
        <td><a href="sample/test-v1.0-api_performanceTest_server_socket_201511192006-udpsck.png" target="_png">udpsck</a></td>
        <td>6.0</td>
        <td>6.0</td>
        <td>6.0</td>
        <td>6.0</td>
    </tr>
    </table>
</div>
</body>
</html>
