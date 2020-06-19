import datetime
import os
import re
import time

import pygtail

class Watcher:

    def __init__(self, log_file, offset_file):
        self.alert = False
        self.has_alerted = False
        self.monitor = True
        self.exit = False
        self.offset_file = offset_file

        self.log_file = log_file

        expression = r'Baby Cam] MotionEvent type:(\w+) event:(\d+)'
        self.regex = re.compile(expression)

        self.current_event = None
        self.start_time = None

    def watch(self):
        for line in pygtail.Pygtail(self.log_file, offset_file=self.offset_file, read_from_end=True):
            print(line)
            match = self.regex.search(line)

            if match and match.group(1) == 'start':
                self.current_event = match.group(2)
                self.start_time = datetime.datetime.now()

                self.has_alerted = False
                self.alert = False
            elif match and match.group(1) == 'stop':
                self.current_event = None
                self.start_time = None

        # print('current event {}'.format(current_event))
        if self.current_event and not self.alert and not self.has_alerted:
            time_diff = datetime.datetime.now() - self.start_time
            # print('checking again {}'.format(time_diff.total_seconds()))
            if time_diff.total_seconds() > 10:
                self.alert = True

    def run(self):
        self.monitor = True

        while not self.exit:
            if self.monitor:
                self.watch()
            time.sleep(1)

    def start(self):
        try:
            os.remove(self.offset_file)
        except FileNotFoundError:
            pass

        self.monitor = True
        self.alert = False
        self.has_alerted = False


    def stop(self):
        self.monitor = False

        try:
            os.remove(self.offset_file)
        except FileNotFoundError:
            pass

