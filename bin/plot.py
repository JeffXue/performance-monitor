# -*- coding:utf-8 -*-
import os
import sys
import re
import time
import copy
import platform
import traceback

import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt

import util
import report

zhFont = matplotlib.font_manager.FontProperties(fname='../lib/ukai.ttc')

class ServerResource():
    """server resource base class"""

    def __init__(self, type_list, result_prefix, file_path, granularity=10):
        self.type = copy.copy(type_list)
        self.prefix = copy.copy(result_prefix)
        self.datafile = copy.copy(file_path)
        self.granularity = copy.copy(granularity)
        self.data = {}
        self.timestamp = []
        self.timestamp_ticks = {}
        self.calculate_data = {}
        for i in xrange(len(self.type)):
            self.data.setdefault(self.type[i], [])

    def read_data(self):
        """read raw data from file, generate timestamp into list
        and data into dictionary"""
        f = open(self.datafile, 'r')
        raw_data = []
        raw_timestamp = []
        try:
            #skip the useless line from the head
            skip_line = f.readline()
            while skip_line.find(":") == -1:
                skip_line = f.readline()

            #get the titles and skip the first timestamp
            titles = skip_line.split()[2:]

            #init raw data with titles as list structure
            for i in xrange(len(titles)):
                raw_data.append([])
                raw_data[i].append(titles[i])

            #skip the useless last line and get the raw data
            lines = f.readlines()

            for line in lines[:-1]:
                line = line.split()
                #generate raw timestamp
                raw_timestamp.append(line[0]+"_"+line[1])

                #generate raw data by filtering digital
                line = line[2:]

                for i in xrange(len(titles)):
                    value_flag = 1
                    for char in line[i]:
                        value_flag = util.is_value(char)
                        if not value_flag:
                            break
                    if value_flag:
                        raw_data[i].append(float(line[i]))

            #using the raw data to generate self data and timestamp
            for i in xrange(len(raw_data)):
                if raw_data[i][0] in self.type:
                    self.data[raw_data[i][0]] = raw_data[i][1:]
                    if len(raw_data[i][1:]) == len(raw_timestamp):
                        self.timestamp = raw_timestamp
                    else:
                        print "[ERROR]raw data error in generating timestamp"
        finally:
            f.close()

    def data_filter(self):
        """
        filtering data by granularity (Particle size in seconds)
        """
        #get the granularity from original data
        data_granularity = (int(self.timestamp[1].split("_")[0].split(":")[2]) -
                int(self.timestamp[0].split("_")[0].split(":")[2]))
        if self.granularity <= data_granularity:
            return

        #using the new granularity to filtering timestamp
        temp_timestamp = []
        for i in xrange(0, len(self.timestamp), self.granularity):
            temp_timestamp.append(self.timestamp[i])
        self.timestamp = temp_timestamp

        #using the new granularity to filtering data
        for i in xrange(len(self.type)):
            temp_data = []
            for j in xrange(0, len(self.timestamp), self.granularity):
                temp_data.append(self.data[self.type[i]][j])
            self.data[self.type[i]] = temp_data

    def adapter(self):
        """
        use this method to adapter the data to display
        example: changing KB into MB
        """
        pass

    def analyse_data(self):
        """
        get min, max, avg, p9 value of each type,
        restore into calculate data with dictionary structure
        """
        calculate_data = []
        for i in xrange(len(self.type)):
            calculate_data.append(util.get_min_value(self.data[self.type[i]]))
            calculate_data.append(util.get_max_value(self.data[self.type[i]]))
            calculate_data.append(util.get_avg_value(self.data[self.type[i]]))
            calculate_data.append(util.get_p9_value(self.data[self.type[i]]))
            self.calculate_data.setdefault(self.type[i], calculate_data)
            calculate_data = []

    def get_timestamp_ticks(self):
        """
        analyse timestamp to use in x ticks
        """
        temp_ticks = []

        #get hour for x ticks
        for i in xrange(len(self.timestamp)):
            temp_ticks.append(self.timestamp[i].split(":")[0])

        #if hour number is less than 1, get minute for x ticks
        if len(list(set(temp_ticks))) == 1:
            temp_ticks = []
            for i in xrange(len(self.timestamp)):
                temp_ticks.append(self.timestamp[i].split(":")[1])

        #uniq and sort
        ticks = list(set(temp_ticks))
        ticks.sort(key=temp_ticks.index)
        self.timestamp_ticks.setdefault("ticks", ticks)

        #get the ticks coordinate
        ticks_coordinate = []
        for i in xrange(len(ticks)):
            ticks_coordinate.append(temp_ticks.index(ticks[i]))
        self.timestamp_ticks.setdefault("coordinate", ticks_coordinate)

    def plot_data(self):
        """plot data of type, """

        for i in xrange(len(self.type)):
            plt.figure(i, figsize=(12.8, 8))
            plt.grid(True)

            #set max p9 avg min value as legend
            plt.plot([self.calculate_data[self.type[i]][1]] *
                    len(self.data[self.type[i]]), linewidth=1)
            plt.plot([self.calculate_data[self.type[i]][3]] *
                    len(self.data[self.type[i]]), linewidth=1)
            plt.plot([self.calculate_data[self.type[i]][2]] *
                    len(self.data[self.type[i]]), linewidth=1)
            plt.plot([self.calculate_data[self.type[i]][0]] *
                    len(self.data[self.type[i]]), linewidth=1)
            legend = []
            legend.append('max=%0.2f' % self.calculate_data[self.type[i]][1])
            legend.append('90%%<%0.2f' % self.calculate_data[self.type[i]][3])
            legend.append('avg=%0.2f' % self.calculate_data[self.type[i]][2])
            legend.append('Min=%0.2f' % self.calculate_data[self.type[i]][0])
            plt.legend(legend, loc="best")

            #plot the type data into stack and line
            plt.stackplot(xrange(len(self.data[self.type[i]])),
                    self.data[self.type[i]], colors=["g"])
            plt.plot(self.data[self.type[i]], color="k", linewidth=1)

            #set the x ticks label and limit
            plt.xticks(self.timestamp_ticks.get("coordinate"),
                    self.timestamp_ticks.get("ticks"))
            plt.xlabel(u"时间"+"("+self.timestamp[0]+"~"+
                    self.timestamp[len(self.timestamp)-1]+")",
                    fontproperties=zhFont, fontsize=15, fontstretch=500)
            plt.xlim(0, len(self.data[self.type[i]]))

            #set the y label and limit
            plt.ylabel(self.type[i], fontsize=15, fontstretch=500)
            if self.calculate_data[self.type[i]][1] > 100:
                plt.ylim(0, self.calculate_data[self.type[i]][1]*1.2)
            elif self.type[i].find("%") != -1:
                plt.ylim(0, 100)
            else:
                plt.ylim(0, self.calculate_data[self.type[i]][1]*1.2)

            #set the title
            temp = self.datafile.split("/")[-1].split(".")
            temp.pop(-1)
            title = ""
            for j in xrange(len(temp)):
                title += temp[j]
                title += "."
            title = title[:-1]
            title += "-" + self.type[i]
            plt.title(title, fontsize=15, fontstretch=500)

            #save graph into png
            png_name = (self.datafile.split(".txt")[0] + "-" +
                    self.type[i].replace(r"/s", "").replace("%", "")
                    + ".png")
            #print png_name
            plt.savefig(png_name)
            plt.close()

    def record(self):
        """
        record the calculate_data into report object
        which is used to generate HTML report
        """
        filename_decompose_list = self.datafile.split(r"/")[2].split("_")
        report.Report.datafile_prefix = filename_decompose_list[0]
        report.Report.start_time = filename_decompose_list[-1].split(".txt")[0]
        filename_decompose_list = filename_decompose_list[2:-1]

        resource_type = ""
        for i in xrange(len(filename_decompose_list)):
            if resource_type != "":
                resource_type += "_"+filename_decompose_list[i]
            else:
                resource_type = filename_decompose_list[i]
        report.Report.data_sum.setdefault(resource_type, self.calculate_data)

    def work(self):
        self.read_data()
        self.data_filter()
        self.adapter()
        self.analyse_data()
        self.get_timestamp_ticks()
        self.plot_data()
        self.record()


class CPUResource(ServerResource):

    def adapter(self):
        """
        change %idle to %used
        """
        #change the self type %idle to %used
        self.type[self.type.index("%idle")] = "%used"

        #pop the %idle data, and add %used data
        temp_data = self.data.pop("%idle")
        for i in xrange(len(temp_data)):
            temp_data[i] = float("%0.2f" % (100 - temp_data[i]))
        self.data.setdefault("%used", temp_data)


class MemoryResource(ServerResource):

    def adapter(self):
        """
        change KB --> MB
               %memused --> %(memused - cached - buffer)
        """
        #change %memused into %memused--
        temp_memused = self.data.get("kbmemused")
        temp_cached = self.data.get("kbcached")
        temp_buffers = self.data.get("kbbuffers")
        temp_memfree = self.data.get("kbmemfree")
        temp_memory_percent = []
        for i in xrange(len(self.data.get("%memused"))):
            temp_memory_percent.append(float("%0.2f" % (((temp_memused[i]
                                                   - temp_buffers[i]
                                                   - temp_cached[i]) * 100)
                                       / (temp_memused[i] + temp_memfree[i]))))
        self.data.setdefault("%memused--", temp_memory_percent)
        self.type.append("%memused--")

        #chang self data dictionary key with kb into MB
        for i in xrange(len(self.type)):
            if self.type[i].find("kb") != -1:
                temp_data = self.data.pop(self.type[i])
                for j in xrange(len(temp_data)):
                    temp_data[j] = float("%0.2f" % (temp_data[j] / 1024))
                self.data.setdefault(self.type[i].replace("kb", "") + "(MB)",
                                     temp_data)
        #change self type with kb into MB
        for i in xrange(len(self.type)):
            if self.type[i].find("kb") != -1:
                self.type[i] = self.type[i].replace("kb", "") + "(MB)"


class IOResource(ServerResource):

    def adapter(self):
        """
        change bread/s, bwitn/s into MBread/s, MBwitn/s
        """
        #chang self data dictionary key with bxxxx/s into MBxxxx/s
        for i in xrange(len(self.type)):
            if self.type[i].find("b") != -1:
                temp_data = self.data.pop(self.type[i])
                for j in xrange(len(temp_data)):
                    temp_data[j] = float("%0.2f" % (temp_data[j] / 2048))
                self.data.setdefault(self.type[i].replace("b", "") + "(MB)",
                                     temp_data)

        #change self type with bxxxx/s into MBxxxx/s
        for i in xrange(len(self.type)):
            if self.type[i].find("b") != -1:
                self.type[i] = self.type[i].replace("b", "") + "(MB)"


class EthResource(ServerResource):

    def adapter(self):
        """
        change byte into MB or KB into MB
        """
        #according system type to decide the keyword
        if platform.platform().find("Ubuntu") != -1:
            keyword = "kB"
        if platform.platform().find("debian") != -1:
            keyword = "kB"
        elif platform.platform().find("centos") != -1:
            keyword = "kB"
        elif platform.platform().find("redhat") != -1:
            keyword = "byt"
        else:
            print "[ERROR]unknow platform"

        #change self data dictionary key with byte/kb into MB
        for i in xrange(len(self.type)):
            if self.type[i].find(keyword) != -1:
                temp_data = self.data.pop(self.type[i])
                for j in xrange(len(temp_data)):
                    if keyword == "kB":
                        temp_data[j] = float("%0.2f" % (temp_data[j] / 1024))
                    if keyword == "byt":
                        temp_data[j] = float("%0.2f" % (temp_data[j] / 1048576))
                self.data.setdefault(self.type[i].replace(keyword, "") + "(MB)",
                                     temp_data)
        #change self type with byte/kb into MB
        for i in xrange(len(self.type)):
            if self.type[i].find(keyword) != -1:
                self.type[i] = self.type[i].replace(keyword, "") + "(MB)"


class LoadResource(ServerResource):
    """just inherit from ServerResource"""
    pass


class SockResource(ServerResource):
    """just inherit from ServerResource"""
    pass


class ProcessResource(ServerResource):
    """just inherit from ServerResource"""
    pass


class MySQLResource(ServerResource):
    """just inherit from ServerResource"""
    pass


class TCPPortResource(ServerResource):
    """just inherit from ServerResource"""
    pass


class ThreadsResource(ServerResource):
    """just inherit from ServerResource"""
    pass


class RedisResource(ServerResource):

    def adapter(self):
        for i in xrange(len(self.type)):
            if self.type[i].find("used_memory") != -1:
                temp_data = self.data.pop(self.type[i])
                for j in xrange(len(temp_data)):
                    temp_data[j] = float("%0.2f" % (temp_data[j] / 1048576))
                self.data.setdefault(self.type[i] + '(MB)', temp_data)

        for i in xrange(len(self.type)):
            if self.type[i].find("used_memory") != -1:
                self.type[i] += "(MB)"


class MemcachedResource(ServerResource):
    """just inherit from ServerResource"""
    pass


class MongodbResource(ServerResource):

    def read_data(self):
        """read raw data from file, generate timestamp into list
        and data into dictionary"""
        f = open(self.datafile, 'r')
        raw_data = []
        raw_timestamp = []
        try:
            #skip the useless line from the head
            skip_line = f.readline()
            while skip_line.find(":") == -1:
                skip_line = f.readline()

            #get the titles and skip the first timestamp
            titles = skip_line.split()[2:]

            #pop special title for mongodb stats
            if self.datafile.find('mongodb') != -1 and self.datafile.find('process') == -1 and self.datafile.find('thread') == -1:
                try:
                    titles.pop(titles.index('db'))
                    titles.pop(titles.index(r'%'))
                    titles.pop(titles.index('idx'))
                except Exception, e:
                    pass

            #init raw data with titles as list structure
            for i in xrange(len(titles)):
                raw_data.append([])
                raw_data[i].append(titles[i])

            #skip the useless last line and get the raw data
            lines = f.readlines()

            for line in lines:
                line = line.split()
                #generate raw timestamp
                raw_timestamp.append(line[0]+"_"+line[1])

                #generate raw data by filtering digital
                line = line[2:]

                for i in xrange(len(titles)):
                    raw_data[i].append(line[i])

            #using the raw data to generate self data and timestamp
            for i in xrange(len(raw_data)):
                if raw_data[i][0] in self.type:
                    self.data[raw_data[i][0]] = raw_data[i][1:]
                    if len(raw_data[i][1:]) == len(raw_timestamp):
                        self.timestamp = raw_timestamp
                    else:
                        print "[ERROR]raw data error in generating timestamp"
        finally:
            f.close()

    def adapter(self):
        for i in xrange(len(self.type)):
            temp_type = self.type[i]
            temp_data = self.data.pop(temp_type)
            if temp_type.find('mapped') != -1 or temp_type.find('vsize') != -1 or temp_type.find('res') != -1 or temp_type.find('non-mapped') != -1:
                self.type[i] = temp_type+'(MB)'
                for j in xrange(len(temp_data)):
                    data = temp_data[j]
                    if data.find('g') != -1 or data.find('G') != -1:
                        temp_data[j] = int(float(data[:-1])*1024)
                    elif data.find('m') != -1 or data.find('M') != -1:
                        temp_data[j] = int(float(data[:-1]))
                    elif data.find('k') != -1 or data.find('K') != -1:
                        temp_data[j] = int(float(data[:-1])/1024)
                    else:
                        temp_data[j] = int(float(data)/1048576)
                self.data.setdefault(self.type[i], temp_data)
            if temp_type.find('insert') != -1 or temp_type.find('query') != -1 or temp_type.find('update') != -1 or temp_type.find('delete') != -1:
                for j in xrange(len(temp_data)):
                    if temp_data[j].find('*') != -1:
                        temp_data[j] = int(temp_data[j].replace('*', ''))
                    else:
                        temp_data[j] = int(temp_data[j])
                self.data.setdefault(self.type[i], temp_data)
            if temp_type.find('getmore') != -1 or temp_type.find('flushes') != -1 or temp_type.find('faults') != -1 or temp_type.find('conn') != -1:
                for j in xrange(len(temp_data)):
                    temp_data[j] = int(temp_data[j])
                self.data.setdefault(self.type[i], temp_data)


class ApacheResource(ServerResource):
    """just inherit from ServerResource"""
    pass


class TomcatResource(ServerResource):

    def read_data(self):
        """read raw data from file, generate timestamp into list
        and data into dictionary"""
        f = open(self.datafile, 'r')
        raw_data = []
        raw_timestamp = []
        try:
            #skip the useless line from the head
            skip_line = f.readline()
            while skip_line.find(":") == -1:
                skip_line = f.readline()

            #get the titles and skip the first timestamp
            titles = skip_line.split()[2:]

            #init raw data with titles as list structure
            for i in xrange(len(titles)):
                raw_data.append([])
                raw_data[i].append(titles[i])

            #skip the useless last line and get the raw data
            lines = f.readlines()

            for line in lines:
                line = line.split()
                #generate raw timestamp
                raw_timestamp.append(line[0]+"_"+line[1])

                #generate raw data by filtering digital
                line = line[2:]

                for i in xrange(len(titles)):
                    raw_data[i].append(line[i])

            #using the raw data to generate self data and timestamp
            for i in xrange(len(raw_data)):
                if raw_data[i][0] in self.type:
                    self.data[raw_data[i][0]] = raw_data[i][1:]
                    if len(raw_data[i][1:]) == len(raw_timestamp):
                        self.timestamp = raw_timestamp
                    else:
                        print "[ERROR]raw data error in generating timestamp"
        finally:
            f.close()

    def adapter(self):
        for i in xrange(len(self.type)):
            temp_type = self.type[i]
            temp_data = self.data.pop(temp_type)
            if temp_type.find('free_memory') != -1 or temp_type.find('total_memory') != -1:
                self.type[i] = temp_type+'(MB)'
                for j in xrange(len(temp_data)):
                    data = temp_data[j]
                    if data.find('G') != -1 or data.find('g') != -1:
                        temp_data[j] = int(float(data[:-1])*1024)
                    elif data.find('MB') != -1 or data.find('mb') != -1:
                        temp_data[j] = float(data[:-2])
                    elif data.find('KB') != -1 or data.find('kb') != -1:
                        temp_data[j] = int(float(data[:-2])/1024)
                    else:
                        temp_data[j] = int(float(data)/1048576)
                self.data.setdefault(self.type[i], temp_data)
            elif temp_type.find('max_processing_time') != -1 or temp_type.find('processing_time') != -1:
                self.type[i] = temp_type + '(s)'
                for j in xrange(len(temp_data)):
                    data = temp_data[j]
                    if data.find('ms') != -1 or data.find('MS') != -1:
                        temp_data[j] = float("%0.3f" % float(float(data[:-2])/1024))
                    elif data.find('s') != -1 or data.find('S') != -1:
                        temp_data[j] = float(data[:-1])
                self.data.setdefault(self.type[i], temp_data)
            else:
                for j in xrange(len(temp_data)):
                    temp_data[j] = int(temp_data[j])
                self.data.setdefault(self.type[i], temp_data)


class NginxResource(ServerResource):
    """just inherit from ServerResource"""
    pass


class SocketStatResource(ServerResource):
    pass
