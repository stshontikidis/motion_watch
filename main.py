import json
import logging
from logging.handlers import RotatingFileHandler
import signal
import threading
import time

import paho.mqtt.client as mqtt

import motion_watch


def logging_setup(config):
    log_level = config.get('log_level')

    if log_level.lower() == 'debug':
        log_level = logging.DEBUG
    elif log_level.lower() == 'info':
        log_level = logging.INFO
    elif log_level.lower() == 'error':
        log_level = logging.ERROR
    else:
        log_level = logging.WARNING

    handler = RotatingFileHandler('motion_watch.log', mode='a', maxBytes=5*1024*1024,
                                                   backupCount=2, encoding=None, delay=0)
    handler.setFormatter(logging.Formatter('%(asctime)s %(levelname)s %(message)s'))
    handler.setLevel(log_level)

    app_log = logging.getLogger('root')
    app_log.setLevel(log_level)

    app_log.addHandler(handler)

    return app_log

def main():
    config = None
    with open('config.json') as file:
        config = json.load(file)

    logger = logging_setup(config)
    mqtt_client = mqtt.Client('motion_watch')

    watcher = motion_watch.Watcher(config['log_file'], config['offset_file'], mqtt_client, logger)
    watch_thread = threading.Thread(target=watcher.run)

    # The callback for when the client receives a CONNACK response from the server.
    def on_connect(client, userdata, flags, rc):
        logger.info("Connected with result code "+str(rc))

        # reconnect then subscriptions will be renewed.
        client.subscribe('switch/motion/baby_cam', 1)

    def on_message(client, userdata, msg):
        if msg.payload.decode('utf-8') == 'on':

            try:
                watcher.start()
                logger.info('Starting watcher on active thread')
            except Exception as e:
                logger.error(e)

        elif msg.payload.decode('utf-8') == 'off':
            logger.info('Stopping watcher')
            watcher.stop()

    def on_disconnect(client, userdata, rc):
        pass

    mqtt_client.on_connect = on_connect
    mqtt_client.on_message = on_message
    mqtt_client.username_pw_set(config['mqtt_user'], config['mqtt_password'])
    mqtt_client.will_set('status/scripts/motion_watch', payload='died')
    mqtt_client.enable_logger(logger=logger)

    mqtt_client.connect(config['mqtt_host'], config['mqtt_port'])

    watch_thread.start()

    def die_with_grace():
        watcher.stop()
        watcher.exit = True

        mqtt_client.loop_stop()
        mqtt_client.disconnect()

        logger.info('Program exiting')

    signal.signal(signal.SIGTERM, die_with_grace)

    mqtt_client.loop_start()
    watch_thread.join()


if __name__ == "__main__":
    main()