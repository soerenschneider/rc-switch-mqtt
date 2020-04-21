import logging
import json
import argparse

from typing import List, Dict

MQTTCOMMANDER = "mqttcommander"
TOPICS = "topics"

_CATCH_ALL = ""


class TopicConfig:
    def __init__(self, topic, cmd: dict):
        self.triggers = dict()
        self.topic = topic
        self.catch_all = False
        self._populate(cmd)
        
    def _populate(self, cmds: dict) -> None:
        for trigger in cmds:
            command_args = cmds[trigger]
            if len(command_args) < 1:
                raise ValueError("No command for topic %s, trigger %s defined", topic, trigger)

            trigger = TopicConfig.fix(trigger)
            self.catch_all = TopicConfig.catches_all(trigger)
            self.triggers[trigger] = command_args

    def __repr__(self) -> str:
        return f"{self.topic} -> {self.triggers}"

    @staticmethod
    def catches_all(trigger: str) -> bool:
        return trigger == _CATCH_ALL

    @staticmethod
    def fix(trigger: str) -> str:
        return trigger.strip().lower()

    def get_cmds(self, message_payload: str) -> List[str]:
        if self.catch_all:
            return self.triggers[_CATCH_ALL]

        message_payload = TopicConfig.fix(message_payload)
        try:
            return self.triggers[message_payload]
        except KeyError:
            return []


class ConfigBuilder:
    @staticmethod
    def build(config_path: str) -> Dict[str, TopicConfig]:
        if not config_path:
            raise ValueError("Supplied empty config path")

        logging.info("Trying to load config at %s", config_path)
        conf = ConfigBuilder._load_config(config_path)
        return ConfigBuilder._build_topic_configs(conf)

    @staticmethod
    def _load_config(path: str):
        with open(path, 'r') as f:
            read = json.load(f)
            return read

        return None

    @staticmethod
    def _build_topic_configs(conf) -> Dict[str, TopicConfig]:
        if not MQTTCOMMANDER in conf:
            raise ValueError("No root node '%s' defined", MQTTCOMMANDER)

        if not TOPICS in conf[MQTTCOMMANDER]:
            raise ValueError("No topics node '%s' defined", TOPICS)

        if len(conf[MQTTCOMMANDER]) < 1:
            raise ValueError("No topics defined")

        topics = dict()
        for topic in conf[MQTTCOMMANDER][TOPICS]:
            for topic_name in topic:
                command_args = topic[topic_name]
                if not command_args:
                    raise ValueError("No commands defined")

                topics[topic_name] = TopicConfig(topic_name, command_args)
        
        return topics


class MqttConfig:
    def __init__(self, args: argparse.Namespace):
        self.id = args.id
        self.host = args.mqtt_host
        self.port = args.mqtt_port