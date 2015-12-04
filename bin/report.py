# -*- coding:utf-8 -*-
import os
import copy
import commands
import ConfigParser
from ftplib import FTP

import util
from template import report_html_header
from template import report_resource_html_header
from template import report_resource_html_data_mult
from template import report_resource_html_data_single
from template import report_html_end


class Report():

    datafile_prefix = ""
    start_time = ""
    end_time = ""
    duration = ""
    data_sum = {}
    data_sum_list = []
    system_information = {}
    result_dir = ""
    report_file = ""
    package_file = ""
    ftp_ip = ""
    ftp_user = ""
    ftp_password = ""
    ftp_flag = 0

    def __init__(self, result_dir):
        self.result_dir = copy.copy(result_dir)

    def get_conf(self):
        config = ConfigParser.ConfigParser()
        with open("../conf/report.ini", "r") as cfg_file:
            config.readfp(cfg_file)
        self.ftp_flag = int(config.get("ftp", "flag"))
        self.ftp_ip = config.get("ftp", "ip")
        self.ftp_user = config.get("ftp", "user")
        self.ftp_password = config.get("ftp", "password")


    def get_system_information(self):
        """
        get base system information for xls report
        include hostname, kernel version, cpuinfo, meminfo, filesystem
        """
        system_command = [
            ["hostname", "hostname"],
            ["kernel", "cat /proc/version |cut -f1 -d'('"],
            ["cpuinfo", "cat /proc/cpuinfo |grep name |cut -f2 -d: \
            |uniq -c |sed -e 's/^[ \t]*//'"],
            ["meminfo",
             " cat /proc/meminfo |head -1|cut -f2- -d':'|sed -e 's/^[ \t]*//'"],
            ["filesystem", "df -h"]]
        for i in xrange(len(system_command)):
            status, output = commands.getstatusoutput(system_command[i][1])
            if not status:
                self.system_information.setdefault(system_command[i][0], output)

    def set_file_name(self):
        self.report_file = (self.result_dir + "/"
                            + self.datafile_prefix + "_" +
                            self.system_information.get("hostname") +
                            "_monitor_statistical_data_" +
                            self.start_time + ".html")

    def get_html_msg(self):
        system_information_table = report_html_header % (self.duration,
                self.system_information.get("hostname"),
                self.system_information.get("kernel"),
                self.system_information.get("cpuinfo"),
                self.system_information.get("meminfo"))

        statistical_data_table = report_resource_html_header  % self.datafile_prefix
        links = []
        for i in xrange(len(self.data_sum_list)):
            for j in xrange(len(self.data_sum_list[i][1])):
                hyper_link = (os.path.basename(self.report_file).split(".html")[0].replace("monitor_statistical_data", self.data_sum_list[i][0]) + 
                        "-" + self.data_sum_list[i][1][j][0].replace("/s", "") +".png").replace("%", "")
                links.append(hyper_link)
                if self.data_sum_list[i][1][j][0].find("%") != -1:
                    data_type = self.data_sum_list[i][1][j][0].replace("%", "")
                    data_type_unit = "(%)"
                else:
                    data_type = self.data_sum_list[i][1][j][0]
                    data_type_unit = ""
                if j == 0:
                    sub_row = report_resource_html_data_mult % (str(len(self.data_sum_list[i][1])),
                            self.data_sum_list[i][0],
                            hyper_link,
                            data_type,
                            data_type_unit,
                            self.data_sum_list[i][1][j][1][0],
                            self.data_sum_list[i][1][j][1][1],
                            self.data_sum_list[i][1][j][1][2],
                            self.data_sum_list[i][1][j][1][3])
                else:
                    sub_row = report_resource_html_data_single % (hyper_link,
                            data_type,
                            data_type_unit,
                            self.data_sum_list[i][1][j][1][0],
                            self.data_sum_list[i][1][j][1][1],
                            self.data_sum_list[i][1][j][1][2],
                            self.data_sum_list[i][1][j][1][3])
                statistical_data_table += sub_row
        statistical_data_table += report_html_end

        msg = system_information_table + statistical_data_table
        return msg

    def generate_html_report(self):
        """
        generate html sum report
        include system information and monitor sum data
        you should set the data_sum before using this method
        """
        #setting duration
        self.duration = (self.start_time[:4] + "-" +
                         self.start_time[4:6] + "-" +
                         self.start_time[6:8] + "_" +
                         self.start_time[8:10] + ":" +
                         self.start_time[10:12] + "~" +
                         self.end_time[:4] + "-" +
                         self.end_time[4:6] + "-" +
                         self.end_time[6:8] + "_" +
                         self.end_time[8:10] + ":" +
                         self.end_time[10:12])

        #sort the data
        data_sum = []
        for item, dic in self.data_sum.iteritems():
            dic_list = []
            for category, value in dic.iteritems():
                dic_list.append([])
                dic_list[len(dic_list)-1].append(category)
                dic_list[len(dic_list)-1].append(value)
            dic_list.sort()
            data_sum.append([])
            data_sum[len(data_sum)-1].append(item)
            data_sum[len(data_sum)-1].append(dic_list)
        data_sum.sort()
        self.data_sum_list = data_sum[:]

        html_report = self.get_html_msg()
        f = open(self.report_file, "a+")
        try:
            f.write(html_report)
        finally:
            f.close()

    def package_files(self):
        """
        package result dictionary into tar.gz file
        and move tar file into result dictionary
        """
        self.package_file = (self.report_file.split("/")[-1].split(".html")[0] +
                             ".zip")
        status, output = commands.getstatusoutput(
            "zip -jr {0} {1}".format(self.package_file, self.result_dir))
        if status:
            print "[ERROR]package up data file failed"
        else:
            status, output = commands.getstatusoutput(
                "mv {0} {1}".format(self.package_file, self.result_dir))
            if status:
                print "[ERROR]mv package failed"
            else:
                self.package_file = self.result_dir + "/" + self.package_file

    def ftp_upload(self):
        ftp = FTP()
        ftp.set_debuglevel(0)
        ftp.connect(self.ftp_ip, '21')
        ftp.login(self.ftp_user, self.ftp_password)
        try:
            ftp.mkd(self.datafile_prefix.split("-")[0])
        except Exception, e:
            print ("[INFO]ftp directory: %s existed" %
                    self.datafile_prefix.split("-")[0])
            print e
        ftp.cwd(self.datafile_prefix.split("-")[0])
        try:
            ftp.mkd(self.datafile_prefix.split("-")[2])
        except Exception, e:
            print ("[INFO]ftp directory: %s existed" %
                    self.datafile_prefix.split("-")[2])
            print e
        ftp.cwd(self.datafile_prefix.split("-")[2])
        try:
            ftp.mkd(self.datafile_prefix.split("-")[1])
        except Exception, e:
            print ("[INFO]ftp directory: %s existed" %
                    self.datafile_prefix.split("-")[1])
            print e
        ftp.cwd(self.datafile_prefix.split("-")[1])
        try:
            ftp.mkd("monitor")
        except Exception, e:
            print "[INFO]ftp directory: monitor existed"
            print e
        ftp.cwd("monitor")
        ftp.mkd(os.path.basename(self.report_file).split(".html")[0])
        ftp.cwd(os.path.basename(self.report_file).split(".html")[0])
        buffer_size = 1024
        for datafile in util.get_dir_files(self.result_dir):
            file_handler = open(self.result_dir + "/" + datafile, "rb")
            ftp.storbinary("STOR %s" % datafile, file_handler, buffer_size)
        ftp.set_debuglevel(0)
        file_handler.close()
        ftp.quit()

    def work(self):
        self.get_conf()
        self.get_system_information()
        self.set_file_name()
        self.generate_html_report()
        self.package_files()
        if self.ftp_flag:
            self.ftp_upload()

