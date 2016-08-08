# -*- coding:utf-8 -*-
import os
import time
import copy
import json
import commands
import ConfigParser
import requests
from ftplib import FTP

import util
from jinja2 import Environment, FileSystemLoader

env = Environment(loader=FileSystemLoader('./templates'))
template = env.get_template('report.html')


class Report:

    datafile_prefix = ""
    start_time = ""
    end_time = ""
    data_sum = {}
    system_information = {}
    result_dir = ""
    report_file = ""
    package_file = ""
    ftp_ip = ""
    ftp_user = ""
    ftp_password = ""
    ftp_flag = 0

    # 用于上传数据
    api_url = ""
    api_flag = 0
    api_monitor_type = ""
    summary_data = {}
    lina_data = {}

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

        self.api_url = config.get("api", "url")
        self.api_flag = int(config.get("api", "flag"))
        self.api_monitor_type = config.get('api', 'type')

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
        self.report_file = (self.result_dir + "/" + self.datafile_prefix +
                            "_" + self.system_information.get("hostname") +
                            "_monitor_" + self.start_time + ".html")

    def generate_html_report(self):
        """
        generate html sum report
        include system information and monitor sum data
        you should set the data_sum before using this method
        """
        start_time = time.strftime("%Y-%m-%d %H:%M",
                                   time.strptime(self.start_time, "%Y%m%d%H%M"))
        end_time = time.strftime("%Y-%m-%d %H:%M",
                                 time.strptime(self.end_time, "%Y%m%d%H%M"))
        duration = start_time + ' ~ ' + end_time

        data_sum = copy.deepcopy(self.data_sum)
        for item, sub_type_dict in data_sum.iteritems():
            for sub_type, sum_value in sub_type_dict.iteritems():
                hyper_link = (os.path.basename(self.report_file).split(".html")[0].replace("monitor", item) +
                              "-" + sub_type.replace("/s", "") + ".png").replace("%", "")
                # add hyper link
                self.data_sum[item][sub_type].append(hyper_link)
                # add len data
                self.data_sum[item][sub_type].append(len(sub_type_dict))
                if sub_type.find("%") != -1:
                    self.data_sum[item].setdefault(sub_type.replace('%', '')+'(%)', self.data_sum[item][sub_type])
                    self.data_sum[item].pop(sub_type)

        html_report = template.render(data_sum=self.data_sum,
                                      system_information=self.system_information,
                                      duration=duration,
                                      datafile_prefix=self.datafile_prefix)
        self.summary_data.update(self.data_sum)
        self.summary_data.update(self.system_information)
        self.summary_data['duration'] = duration
        self.summary_data['module'] = self.datafile_prefix.split('-')[0]
        self.summary_data['version'] = self.datafile_prefix.split('-')[1]
        self.summary_data['scenario_name'] = self.datafile_prefix.split('-')[2]
        self.summary_data['monitor_type'] = self.api_monitor_type

        f = open(self.report_file, "a+")
        try:
            f.write(html_report.encode('utf-8'))
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

    def api_upload(self):
        self.summary_data['line_data'] = self.line_data
        r = requests.post(self.api_url, json=json.dumps(self.summary_data))
        if r.text == "200":
            print "[INFO]api upload success"
        else:
            print "[ERROR]api upload failed"

    def work(self):
        self.get_conf()
        self.get_system_information()
        self.set_file_name()
        self.generate_html_report()
        if self.api_flag:
            self.api_upload()
        self.package_files()
        if self.ftp_flag:
            self.ftp_upload()

