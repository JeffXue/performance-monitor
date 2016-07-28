# -*- coding:utf-8 -*-

import sys
import time
import bmemcached

from util import get_parameter_lists


class MonitorMemcachedStat:

    def __init__(self, ip, port, interval, end_time, filename, user, passwd):
        if user != '' and passwd != '':
            self.client = bmemcached.Client(('%s:%s' % (ip, port),), user, passwd)
        else:
            self.client = bmemcached.Client(('%s:%s' % (ip, port),))
        self.ip = ip
        self.port = port
        self.interval = int(interval)
        self.end_time = float(end_time)
        self.filename = filename

    def work(self):
        while time.time() < self.end_time:
            stats = self.client.stats()['%s:%s' % (self.ip, self.port)]
            curr_connections = stats.get('curr_connections')
            cmd_get = stats.get('cmd_get')
            cmd_set = stats.get('cmd_set')
            cmd_flush = stats.get('cmd_flush')
            get_hits = stats.get('get_hits')
            get_misses = stats.get('get_misses')
            get_total = float(int(get_hits)+int(get_misses))
            if int(get_hits) != 0 or int(get_total) != 0:
                hit_rate = '%0.2f' % float(float(int(get_hits)*100)/get_total)
            else:
                hit_rate = 0
            bytes_read = stats.get('bytes_read')
            bytes_written = stats.get('bytes_written')
            limit_maxbytes = stats.get('limit_maxbytes')
            accepting_conns = stats.get('accepting_conns')
            threads = stats.get('threads')
            bytes = stats.get('bytes')
            curr_items = stats.get('curr_items')
            total_items = stats.get('total_items')
            evictions = stats.get('evictions')
            stats_time = time.strftime('%H:%M:%S %p', time.localtime(time.time()))
            stats_list = [stats_time, curr_connections, cmd_get, cmd_set, cmd_flush, get_hits,
                          get_misses, hit_rate, bytes_read, bytes_written, limit_maxbytes,
                          accepting_conns, threads, bytes, curr_items, total_items, evictions]
            with open(self.filename, 'a') as f:
                f.write(' '.join(stats_list)+'\n')
            time.sleep(self.interval)


def main():
    parameters = get_parameter_lists(sys.argv)
    if len(parameters) == 5:
        ip = parameters[0]
        port = parameters[1]
        interval = parameters[2]
        end_time = parameters[3]
        filename = parameters[4]
        user = ''
        passwd = ''
        monitor_memcached_stat = MonitorMemcachedStat(ip, port, interval, end_time, filename, user, passwd)
        monitor_memcached_stat.work()
    if len(parameters) == 7:
        ip = parameters[0]
        port = parameters[1]
        interval = parameters[2]
        end_time = parameters[3]
        filename = parameters[4]
        user = parameters[5]
        passwd = parameters[6]
        monitor_memcached_stat = MonitorMemcachedStat(ip, port, interval, end_time, filename, user, passwd)
        monitor_memcached_stat.work()

if __name__ == "__main__":
    main()
