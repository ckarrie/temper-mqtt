import paho.mqtt.client as mqtt
import uuid
import socket
import re
import json
from libs.temper.temper import Temper

MQTT_BROKER_HOST = '192.168.178.71'
hostname = socket.gethostname()
mac_address = ':'.join(re.findall('..', '%012x' % uuid.getnode()))

state_topic_temp = 'winden/{}/pcsensor_{}/temp'

client = mqtt.Client()
client.connect(MQTT_BROKER_HOST, 1883, 60)


def get_dev_temperatures():
    temps = []
    temper = Temper()
    results = temper.read()
    for dev in results:
        temp = dev.get('internal temperature')
        temps.append(temp)
    return temps


def publish_homeassistant_sensors():
    homeassistant_sensor_topic = "homeassistant/sensor/{}/tempdev{}/config"
    temps = get_dev_temperatures()
    for i, temp in enumerate(temps):
        sensor_topic = homeassistant_sensor_topic.format(hostname, i)
        sensor_payload = {
            'name': "{} PCSensor {}".format(hostname, i),
            'unique_id': '{}_pcsensor_temp_{}'.format(hostname, i),
            "state_topic": state_topic_temp.format(hostname, i),
            "icon": "mdi:temperature-celsius",
            "device_class": "temperature",
            "unit_of_measurement": "°C",
        }
        client.publish(sensor_topic, json.dumps(sensor_payload))


def publish_temps():
    temps = get_dev_temperatures()
    for i, temp in enumerate(temps):
        topic = state_topic_temp.format(hostname, i)
        client.publish(topic, temp)


publish_homeassistant_sensors()
publish_temps()

client.disconnect()




