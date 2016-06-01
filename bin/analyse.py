# -*- coding:utf-8 -*-
import sys
import platform
import ConfigParser
import util
import plot
import report


class MonitorConfig():
    """get config from the ini file"""

    def __init__(self, config_ini):
        self.config_file = config_ini
        config = ConfigParser.ConfigParser()
        with open(self.config_file, "r") as cfg_file:
            config.readfp(cfg_file)
        self.res_dir = config.get("common", "resDir")
        self.granularity = int(config.get("plot", "granularity"))
        self.server_cpu_types = config.get("plot", "serverCPU").split(",")
        self.server_memory_types = config.get("plot", "serverMemory").split(",")
        self.server_io_rate_types = config.get("plot", "serverIORate").split(",")
        self.server_load_types = config.get("plot", "serverQueueLoad").split(",")
        self.server_sock_types = config.get("plot", "serverSock").split(",")
        server_platform = platform.platform()
        if server_platform.find("Ubuntu") != -1:
            self.server_eth_types = config.get("plot", "ubuntuEth").split(",")
        if server_platform.find("debian") != -1:
            self.server_eth_types = config.get("plot", "ubuntuEth").split(",")
        if server_platform.find("centos") != -1:
            self.server_eth_types = config.get("plot", "ubuntuEth").split(",")
        if server_platform.find("redhat") != -1:
            self.server_eth_types = config.get("plot", "redhatEth").split(",")
        self.mysql_connections_types = config.get("plot", "mysql").split(",")
        self.tcp_port_types = config.get("plot", "TCPPort").split(",")
        self.process_types = config.get("plot", "processStatus").split(",")
        self.redis_types = config.get("plot", "redisStatus").split(",")
        self.memcached_types = config.get("plot", "memcachedStatus").split(",")
        self.mongodb_types = config.get("plot", "mongodbStatus").split(",")
        self.apache_types = config.get("plot", 'apacheStatus').split(",")
        self.tomcat7_types = config.get("plot", 'tomcat7Status').split(",")
        self.tomcat6_types = config.get("plot", 'tomcat6Status').split(",")
        self.nginx_types = config.get("plot", 'nginxStatus').split(",")


def main():
    # get the avg
    parameter_lists = util.get_parameter_lists(sys.argv)
    if len(parameter_lists):
        result_prefix = parameter_lists[0]
    else:
        result_prefix = "test"
    if len(parameter_lists) > 1:
        end_time = parameter_lists[1]
    else:
        end_time = "N/A"

    # read the monitor config
    config = MonitorConfig("../conf/report.ini")

    # analyse file
    files = util.get_dir_files(config.res_dir)
    for datafile in files:
        if datafile.find("txt") != -1:
            if datafile.find("server_cpu") != -1:
                cpu_resource = plot.CPUResource(config.server_cpu_types, result_prefix, config.res_dir+"/"+datafile, config.granularity)
                cpu_resource.work()
            if datafile.find("server_memory") != -1:
                memory_resource = plot.MemoryResource(config.server_memory_types, result_prefix, config.res_dir+"/"+datafile, config.granularity)
                memory_resource.work()
            if datafile.find("server_io_rate") != -1:
                io_rate_resource = plot.IOResource(config.server_io_rate_types, result_prefix, config.res_dir+"/"+datafile, config.granularity)
                io_rate_resource.work()
            if datafile.find("server_eth0") != -1:
                eth0_resource = plot.EthResource(config.server_eth_types, result_prefix, config.res_dir+"/"+datafile, config.granularity)
                eth0_resource.work()
            if datafile.find("server_eth1") != -1:
                eth1_resource = plot.EthResource(config.server_eth_types, result_prefix, config.res_dir+"/"+datafile, config.granularity)
                eth1_resource.work()
            if datafile.find("server_queue_load") != -1:
                load_resource = plot.LoadResource(config.server_load_types, result_prefix, config.res_dir+"/"+datafile, config.granularity)
                load_resource.work()
            if datafile.find("server_socket") != -1:
                sock_resource = plot.SockResource(config.server_sock_types, result_prefix, config.res_dir+"/"+datafile, config.granularity)
                sock_resource.work()
            if datafile.find("mysql") != -1:
                mysql_resource = plot.MySQLResource(config.mysql_connections_types, result_prefix, config.res_dir+"/"+datafile, config.granularity)
                mysql_resource.work()
            if datafile.find("TCPPort") != -1:
                tcp_port_resource = plot.TCPPortResource(config.tcp_port_types, result_prefix, config.res_dir+"/"+datafile, config.granularity)
                tcp_port_resource.work()
            if datafile.find("process") != -1:
                process_resource = plot.ProcessResource(config.process_types, result_prefix, config.res_dir+"/"+datafile, config.granularity)
                process_resource.work()
            if datafile.find("redis") != -1:
                if datafile.find('process') == -1 and datafile.find('thread') == -1:
                    redis_resource = plot.RedisResource(config.redis_types, result_prefix, config.res_dir+"/"+datafile, config.granularity)
                    redis_resource.work()
            if datafile.find('memcached') != -1:
                if datafile.find('process') == -1 and datafile.find('thread') == -1:
                    memcached_resource = plot.MemcachedResource(config.memcached_types, result_prefix, config.res_dir+"/"+datafile, config.granularity)
                    memcached_resource.work()
            if datafile.find('mongodb') != -1:
                if datafile.find('process') == -1 and datafile.find('thread') == -1:
                    mongodb_resource = plot.MongodbResource(config.mongodb_types, result_prefix, config.res_dir+"/"+datafile, config.granularity)
                    mongodb_resource.work()
            if datafile.find('apache') != -1:
                if datafile.find('process') == -1 and datafile.find('thread') == -1:
                    apache_resource = plot.ApacheResource(config.apache_types, result_prefix, config.res_dir+"/"+datafile, config.granularity)
                    apache_resource.work()
            if datafile.find('tomcat6') != -1:
                if datafile.find('process') == -1 and datafile.find('thread') == -1:
                    tomcat_resource = plot.TomcatResource(config.tomcat6_types, result_prefix, config.res_dir+"/"+datafile, config.granularity)
                    tomcat_resource.work()
            if datafile.find('tomcat7') != -1:
                if datafile.find('process') == -1 and datafile.find('thread') == -1:
                    tomcat_resource = plot.TomcatResource(config.tomcat7_types, result_prefix, config.res_dir+"/"+datafile, config.granularity)
                    tomcat_resource.work()
            if datafile.find('nginx') != -1:
                if datafile.find('process') == -1 and datafile.find('thread') == -1:
                    nginx_resource = plot.TomcatResource(config.nginx_types, result_prefix, config.res_dir+"/"+datafile, config.granularity)
                    nginx_resource.work()

    #generate sum report
    report.Report.end_time = end_time
    resource_sum_report = report.Report(config.res_dir)
    resource_sum_report.work()

if __name__ == "__main__":
    main()




