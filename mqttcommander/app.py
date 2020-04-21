#import backoff
import logging
import paho.mqtt.client as mqtt
import subprocess
import time

from threading import Lock
from typing import Dict, List

from mqttcommander.config import TopicConfig, MqttConfig
from mqttcommander.metrics import PROM_MQTT_RECONNECTS, PROM_CONF_TOPICS, PROM_TRIGGERED_COMMANDS, PROM_TRIGGERED_COMMANDS_ERRORS, PROM_MQTT_IGNORED_MESSAGES

_COMMAND_TIMEOUT_SECS=15

class MqttCommander:
    def __init__(self, mqtt_conf: MqttConfig, topic_conf: Dict[str, TopicConfig]):
        if not mqtt_conf:
            raise ValueError("No mqtt config provided")
        self._mqtt_config = mqtt_conf

        if not topic_conf:
            raise ValueError("No topic config provided")
        
        PROM_CONF_TOPICS.labels(self._mqtt_config.id).set(len(topic_conf))
        self._topic_conf = topic_conf
        self._locks = dict()
        self._quit = False
        self.connect()

    def _on_connect(self, client, userdata, flags, rc):
        PROM_MQTT_RECONNECTS.labels(self._mqtt_config.id).inc()
        logging.info("Connected to %s with result code %s", self._mqtt_config.host, str(rc))

        for topic in self._topic_conf:
            logging.info("Subscribing to %s", topic)
            client.subscribe(topic, 0)

    def _on_message(self, client, userdata, msg):
        payload = msg.payload.decode('utf-8').lower()        
        topic = msg.topic
        topic_config = self._topic_conf[topic]
        self._trigger(topic_config, payload)

    def _trigger(self, topic_config: TopicConfig, trigger: str) -> None:
        topic = topic_config.topic
        cmd_args = topic_config.get_cmds(trigger)

        if topic_config.catches_all:
            trigger = ""
        
        if not cmd_args:
            PROM_MQTT_IGNORED_MESSAGES.labels(self._mqtt_config.id, topic).inc()
            return

        logging.debug("Received trigger %s on topic %s, invoking cmd: %s", trigger, topic, cmd_args)
        with self._get_lock(topic):
            try:
                PROM_TRIGGERED_COMMANDS.labels(self._mqtt_config.id, topic, trigger).inc()
                proc = subprocess.run(cmd_args, timeout=_COMMAND_TIMEOUT_SECS, check=True)
            except subprocess.CalledProcessError as e:
                PROM_TRIGGERED_COMMANDS_ERRORS.labels(self._mqtt_config.id, topic, trigger).inc()
                logging.error(e)

    def _get_lock(self, topic: str) -> Lock:
        if topic not in self._locks:
            self._locks[topic] = Lock()

        return self._locks[topic]

    def connect(self) -> None:
        self._client = mqtt.Client()
        self._client._on_connect = self._on_connect
        self._client._on_message = self._on_message
        self._client.enable_logger()

        logging.info("Async connecting to host %s:%d", self._mqtt_config.host, self._mqtt_config.port)
        self._client.reconnect_delay_set(min_delay=3, max_delay=120)
        self._client.connect_async(self._mqtt_config.host, self._mqtt_config.port, 60)
        self._client.loop_start()

        try:
            while not self._quit:
                time.sleep(5)
            logging.info("Quitting, bye!")
        except KeyboardInterrupt:
            logging.info("Received signal, quitting. Bye!")