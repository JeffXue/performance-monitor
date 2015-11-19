# -*- coding:utf-8 -*-
import sys
import time
import requests

from util import get_parameter_lists


class MonitorNginx():

    def __init__(self, url, interval, end_time, filename):
        self.url = url
        self.interval = int(interval)
        self.end_time = float(end_time)
        self.filename = filename

    def work(self):
        while time.time() < self.end_time:
            r = requests.get(self.url)
            if r.status_code == 200:
                active_connections = r.text.split('Active connections:')[-1].split()[0]
                handled_connections = r.text.split('server accepts handled requests')[-1].split()[0]
                handled_handshake = r.text.split('server accepts handled requests')[-1].split()[1]
                handled_requests = r.text.split('server accepts handled requests')[-1].split()[2]
                reading = r.text.split('Reading:')[-1].split()[0]
                writing = r.text.split('Writing:')[-1].split()[0]
                waiting = r.text.split('Waiting:')[-1].split()[0]
                stats_time = time.strftime('%H:%M:%S %p', time.localtime(time.time()))
                stats_list = [stats_time, active_connections, handled_connections, handled_handshake, handled_requests,
                              reading, writing, waiting]
                with open(self.filename, 'a') as f:
                    f.write(' '.join(stats_list)+'\n')
            time.sleep(self.interval)


def main():
    parameters = get_parameter_lists(sys.argv)
    if len(parameters) == 4:
        url = parameters[0]
        interval = parameters[1]
        end_time = parameters[2]
        filename = parameters[3]

    monitor_nginx_status = MonitorNginx(url, interval, end_time, filename)
    monitor_nginx_status.work()

if __name__ == "__main__":
    main()