# -*- coding:utf-8 -*-
import sys
import time
import requests

from util import get_parameter_lists


class MonitorTomcat():

    def __init__(self, url, interval, end_time, filename, monitor_sign, tomcat_type, tomcat_self_name, user, password):
        self.url = url
        self.interval = int(interval)
        self.end_time = float(end_time)
        self.filename = filename
        self.monitor_sign = monitor_sign
        self.tomcat_type = tomcat_type
        self.tomcat_self_name = tomcat_self_name
        self.user = user
        self.password = password

    def work(self):
        while time.time() < self.end_time:
            if self.user and self.password:
                r = requests.get(self.url, auth=(self.user, self.password))
            else:
                r = requests.get(self.url)
            if r.status_code == 200:
                free_memory = r.text.split('Free memory:')[-1].split('Total memory:')[0].strip().replace(' ', '')
                total_memory = r.text.split('Total memory:')[-1].split('Max memory:')[0].strip().replace(' ', '')
                if self.tomcat_type == 'tomcat6':
                    pass
                elif self.tomcat_type == 'tomcat7':
                    ps_eden_space = r.text.split('PS Eden Space')[-1].split(r'%')[0].split('(')[-1]
                    ps_old_gen = r.text.split('PS Old Gen')[-1].split(r'%')[0].split('(')[-1]
                    ps_survivor_space = r.text.split('PS Survivor Space')[-1].split(r'%')[0].split('(')[-1]
                split_sign = self.monitor_sign
                max_threads = r.text.split(split_sign)[-1].split('Max threads:')[1].split('Current thread count:')[0].strip()
                current_thread_count = r.text.split(split_sign)[-1].split('Current thread count:')[1].split('Current thread busy:')[0].strip()
                current_thread_busy = r.text.split(split_sign)[-1].split('Current thread busy:')[1].split('<br>')[0].split()[0].strip()
                max_processing_time = r.text.split(split_sign)[-1].split('Max processing time:')[1].split('Processing time:')[0].strip().replace(' ', '')
                processing_time = r.text.split(split_sign)[-1].split('Processing time:')[1].split('Request count:')[0].strip().replace(' ', '')

                stats_time = time.strftime('%H:%M:%S %p', time.localtime(time.time()))
                if self.tomcat_type == 'tomcat6':
                    stats_list = [stats_time, free_memory, total_memory, max_threads, current_thread_count,
                            current_thread_busy, max_processing_time, processing_time]
                elif self.tomcat_type == 'tomcat7':
                    stats_list = [stats_time, free_memory, total_memory, ps_eden_space, ps_old_gen, ps_survivor_space,
                            max_threads, current_thread_count, current_thread_busy, max_processing_time, processing_time]
                with open(self.filename, 'a') as f:
                    f.write(' '.join(stats_list)+'\n')
            time.sleep(self.interval)


def main():
    parameters = get_parameter_lists(sys.argv)
    if len(parameters) == 7:
        url = parameters[0]
        interval = parameters[1]
        end_time = parameters[2]
        filename = parameters[3]
        monitor_sign = parameters[4]
        tomcat_type = parameters[5]
        tomcat_self_name = parameters[6]
        user = None
        password = None
    if len(parameters) == 9:
        url = parameters[0]
        interval = parameters[1]
        end_time = parameters[2]
        filename = parameters[3]
        monitor_sign = parameters[4]
        tomcat_type = parameters[5]
        tomcat_self_name = parameters[6]
        user = parameters[7]
        password = parameters[8]
    monitor_apache_status = MonitorTomcat(url, interval, end_time, filename, monitor_sign, tomcat_type, tomcat_self_name, user, password)
    monitor_apache_status.work()

if __name__ == "__main__":
    main()
