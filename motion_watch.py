import datetime
import json
import re
import sys
import time

import pygtail


def main():
    expression = r'Baby Cam] MotionEvent type:(\w+) event:(\d+)'
    regex = re.compile(expression)
    current_event = None

    alerted = False
    while True:
        for line in pygtail.Pygtail("/volume1/docker/unifi-video/logs/motion.log", offset_file='motion.offset', read_from_end=True):
            print(line)
            match = regex.search(line)

            if match and match.group(1) == 'start':
                current_event = match.group(2)
                start_time = datetime.datetime.now()
            elif match and match.group(1) == 'stop':
                current_event = None
                alerted = False
        
        print('current event {}'.format(current_event))
        if current_event and not alerted:
            time_diff = datetime.datetime.now() - start_time
            print('checking again {}'.format(time_diff.total_seconds()))
            if time_diff.total_seconds() > 20:
                print('Alert!')
                alerted = True

        time.sleep(1)

if __name__ == "__main__":
    main()
