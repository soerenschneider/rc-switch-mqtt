import re
import json
import time
import logging

import backoff
import paho.mqtt.client as mqtt

from configuration import ON, OFF
from metrics import prom_msg_error_cnt, prom_reconnects, prom_switch_operations

class MqttListener:
    def __init__(self, host, location, topic, transmitter, port=None):
        logging.info("Initializing MQTT backend...")
        if not host or not location or not topic or not transmitter:
            raise ValueError("host, location, topic and sender must be set.")

        self._host = host
        self._location = location
        if port is None:
            port = 1883
        self._port = port
        self._quit = False

        self._topic = topic
        self.topic_regex = topic.replace('+', '(\w+)')

        if not transmitter:
            raise ValueError("No sender supplied")

        self._sender = transmitter

    def on_connect(self, client, userdata, flags, rc):
        prom_reconnects.labels(self._location).inc()
        logging.info("Connected to %s with result code %s", self._topic, str(rc))
        client.subscribe(self._topic, 0)

    def extract_plug_name(self, topic):
        # extract the appropriate plug from the topic the message was received on
        plugs = re.findall(self.topic_regex, topic)
        if not plugs:
            return None

        return plugs[0]

    def switch(self, payload, topic):
        if payload not in [ON, OFF]:
            cause = 'Invalid payload'
            prom_msg_error_cnt.labels(location=self._location, cause=cause).inc()
            logging.warn('Invalid payload')
            return

        try:
            plug_name = self.extract_plug_name(topic)
            if not plug_name:
                cause = 'Could not extract plug name from topic'
                prom_msg_error_cnt.labels(location=self._location, cause=cause).inc()
                logging.error(cause)
                return

            self._sender.send_signal(plug_name, payload)
            prom_switch_operations.labels(location=self._location, operation=payload)
        except ValueError as e:
            logging.error("Invalid message format: %s", e)
        except Exception as e:
            logging.error(e)

    def on_message(self, client, userdata, msg):
        logging.debug("Message received in topic %s -> %s", msg.topic, msg.payload)
        payload = msg.payload.decode('utf-8').lower()
        self.switch(payload, msg.topic)

    def quit(self):
        self._quit = True

    def publish(self, data):
        logging.debug("Publishing '%s' to %s", data, self._topic)
        try:
            self._client.publish(self._topic, data)
        except Exception as e:
            logging.error("Error while publishing message to topic", self._topic)
            self._prom_msg_error_cnt.labels(self._location).inc()

    @backoff.on_exception(backoff.expo,
                      (ConnectionRefusedError),
                      max_time=5)
    def connect(self):
        self._client = mqtt.Client()
        self._client.on_connect = self.on_connect
        self._client.on_message = self.on_message

        logging.info("Async connecting to %s:%d", self._host, self._port)
        self._client.connect_async(self._host, self._port, 60)
        self._client.loop_start()
        try:
            while not self._quit:
                time.sleep(10)
            logging.info("Quitting, bye!")
        except KeyboardInterrupt:
            logging.info("Received signal, quitting. Bye!")

