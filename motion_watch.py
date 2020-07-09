import datetime
import os
import re
import time

from paho.mqtt.client import Client
import pygtail

import constants


LOG_FILE = '/var/lib/unifi-video/logs/motion.log'
OFFSET_FILE = 'motion_watch.offset'

class Event:

    def __init__(self, _id):
        self.id = _id
        self.start_time = datetime.datetime.now()

    def __repr__(self):
        return '<Event ID {}>'.format(self.id)

class Watcher:

    def __init__(self, camera_name: str, mqtt_client: Client, logger, log_file=LOG_FILE, offset_file=OFFSET_FILE):
        self.monitor = False
        self.exit = False
        self.offset_file = offset_file
        self.camera_name = camera_name

        self.current_event = None

        self.mqtt_client = mqtt_client
        self.log_file = log_file

        expression = r'{}] MotionEvent type:(\w+) event:(\d+)'.format(camera_name)
        self.regex = re.compile(expression)

        self.logger = logger

    def watch(self):
        for line in pygtail.Pygtail(self.log_file, offset_file=self.offset_file, read_from_end=True):
            if line:
                self.logger.debug(line)

            match = self.regex.search(line)

            if match:
                self.logger.debug('Match found {}'.format(match.group(0)))

            if match and match.group(1) == 'start':
                self.current_event = Event(match.group(2))
            elif match and match.group(1) == 'stop':
                self.current_event = None

        if self.current_event:
            self.logger.debug('current event {}'.format(self.current_event))

        if self.current_event:
            time_diff = datetime.datetime.now() - self.current_event.start_time
            self.logger.debug('checking event {} again {}'.format(self.current_event, time_diff.total_seconds()))

            if time_diff.total_seconds() > 20:
                alert_topic = '{}/{}'.format(constants.ALERT_TOPIC, self.camera_name.lower().replace(' ', '_'))
                self.mqtt_client.publish(alert_topic, payload='on')

                self.logger.info('Alert threshold hit for event {}'.format(self.current_event.id))
                self.current_event = None

    def run(self):
        self.monitor = True
        self.mqtt_client.publish(constants.STATUS_TOPIC, payload='on')

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
        self.current_event = None
        self.mqtt_client.publish(constants.STATUS_TOPIC, payload='on')

    def stop(self):
        try:
            os.remove(self.offset_file)
        except FileNotFoundError:
            pass

        self.monitor = False
        self.mqtt_client.publish('status/scripts/motion_watch', payload='off')


