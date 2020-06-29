# Motion Watch

Motion Watch is a script that scrapes Unifi Video motion log for motion events and then publishes notification via MQTT.
Currently it is pretty rigid, the camera name it looks for is currently hardcoded, but I hope to make it more dynamic
and take camera names via the config and possibly support multiple cameras.  My reason for doing this is to get
more real time notifications not via email and also not reliant on having the cloud integrated.  The development of
this was also heavily influenced to be used in conjunction with other home automation platforms, mine being Home Assistant
, Node Red and MQTT.  While the script will continuously run you can turn the log watching on/off via an MQTT topic.
I do this because I only want to monitor some times, in my case when I know the baby needs to be monitored

## Installation

Checkout/fork the code and build a venv and you can use the requierments to install needed packages

```bash
pip install -r requierments.txt
```

## Usage

```bash
python main.py &
```

Once the script is started you can start the log watching to publshing to the MQTT topic `switch/motion/baby_cam`
with payload of `on`

## Contributing
Pull requests are welcome. For major changes, please open an issue first to discuss what you would like to change.

Please make sure to update tests as appropriate.

## License
[MIT](https://choosealicense.com/licenses/mit/)