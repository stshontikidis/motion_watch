import json
import time
import threading

import motion_watch
import paho.mqtt.client as mqtt

def main():

    with open('config.json') as file:
        config = json.load(file)

    watcher = motion_watch.Watcher(config['log_file'], config['offset_file'])
    watch_thread = threading.Thread(target=watcher.run)

    # The callback for when the client receives a CONNACK response from the server.
    def on_connect(client, userdata, flags, rc):
        print("Connected with result code "+str(rc))

        # reconnect then subscriptions will be renewed.
        client.subscribe('switch/motion/baby_cam', 1)

    def on_message(client, userdata, msg):
        if msg.payload.decode('utf-8') == 'on':
            if watch_thread.is_alive():
                watcher.start()
            else:
                # need to find out how to handle excptions in that thread
                try:
                    watch_thread.start()
                except:
                    pass

        elif msg.payload.decode('utf-8') == 'off' and watch_thread.is_alive():
            watcher.stop()

    def on_disconnect(client, userdata, rc):
        pass

    mqtt_client = mqtt.Client('motion_watch')
    mqtt_client.on_connect = on_connect
    mqtt_client.on_message = on_message
    mqtt_client.username_pw_set(config['mqtt_user'], config['mqtt_password'])

    mqtt_client.enable_logger()

    mqtt_client.connect(config['mqtt_host'], config['mqtt_port'])
    mqtt_client.loop_start()

    try:
        while True:
            if watcher.alert and not watcher.has_alerted:
                mqtt_client.publish('alert/motion/baby_cam', payload='on')
                watcher.has_alerted = True

            time.sleep(0.5)
    except KeyboardInterrupt:
        mqtt_client.loop_stop()
        mqtt_client.disconnect()
        watcher.stop()
        watcher.exit = True

    print('Exited gracefully!')
if __name__ == "__main__":
    main()