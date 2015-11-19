# -*- coding:utf-8 -*-
import sys
import time
import requests

from util import get_parameter_lists


class MonitorApache():

    def __init__(self, url, interval, end_time, filename, user, password):
        self.url = url
        self.interval = int(interval)
        self.end_time = float(end_time)
        self.filename = filename
        self.user = user
        self.password = password

    def work(self):
        while time.time() < self.end_time:
            if self.user and self.password:
                r = requests.get(self.url, auth=(self.user, self.password))
            else:
                r = requests.get(self.url)
            if r.status_code == 200:
                currently_processed = r.text.split('requests currently being processed')[0].split('<dt>')[-1].replace(' ', '')
                idle_worker = r.text.split('requests currently being processed')[-1].split('idle workers')[0].replace(',', '').replace(' ', '')
                key = r.text.split('<pre>')[1].split('</pre>')[0].replace('\n', '')
                waiting_for_connection = str(key.count('_'))
                starting_up = str(key.count('S'))
                reading_request = str(key.count('R'))
                sending_reply = str(key.count('W'))
                keepalive_read = str(key.count('K'))
                dns_lookup = str(key.count('D'))
                closing_connection = str(key.count('C'))
                logging = str(key.count('L'))
                gracefully_finishing = str(key.count('G'))
                idle_cleanup_of_worker = str(key.count('I'))
                open_slot_with_no_current_process = str(key.count('.'))
                stats_time = time.strftime('%H:%M:%S %p', time.localtime(time.time()))
                stats_list = [stats_time, currently_processed, idle_worker, waiting_for_connection, starting_up,
                              reading_request, sending_reply, keepalive_read, dns_lookup, closing_connection,
                              logging, gracefully_finishing, idle_cleanup_of_worker, open_slot_with_no_current_process]
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
        user = None
        password = None
    if len(parameters) == 6:
        url = parameters[0]
        interval = parameters[1]
        end_time = parameters[2]
        filename = parameters[3]
        user = parameters[4]
        password = parameters[5]
    monitor_apache_status = MonitorApache(url, interval, end_time, filename, user, password)
    monitor_apache_status.work()

if __name__ == "__main__":
    main()