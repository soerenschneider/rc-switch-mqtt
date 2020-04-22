import configargparse
import json
import logging
import sys

from mqttcommander.metrics import start_prometheus_server

from mqttcommander.config import ConfigBuilder, MqttConfig
from mqttcommander.app import MqttCommander 


def _setup_logging(verbose=False) -> None:
    """ Sets up the logging. """
    loglevel = logging.INFO
    if verbose:
        loglevel = logging.DEBUG
    logging.basicConfig(level=loglevel, format='%(levelname)s\t %(asctime)s %(message)s')


def _print_config(args: configargparse.Namespace) -> None:
    logging.info("Started mqttcommander")
    logging.info("Using id=%s", args.id)
    logging.info("Using config=%s", args.config)
    logging.info("Using mqtt-host=%s", args.mqtt_host)
    logging.info("Using prom-port=%s", args.prom_port)
    logging.info("Using verbose=%s", args.verbose)

def _parse_args() -> configargparse.Namespace:
    """ Parsing command line arguments """
    parser = configargparse.ArgumentParser(prog='mqttcommander')

    parser.add_argument('--id',             action="store",             env_var="MQTT_CMD_ID", required=True, help='Unique identifier for this plug.')
    parser.add_argument('-c', '--config',   action='store',   env_var="MQTT_CMD_CONFIG", required=True, help='Config file')
    
    parser.add_argument('--mqtt-host',      action='store',      env_var='MQTT_CMD_HOST', required=True, help='The mqtt server to connect to')
    parser.add_argument('--mqtt-port',      action='store',      env_var='MQTT_CMD_PORT', type=int, default=1883, help='The topic to subscribe to')

    parser.add_argument('--prom-port', action="store",      env_var="MQTT_CMD_PROMPORT", type=int, default=9199, help='The port of the prometheus http server. If you do not want to run a prometheus server, supply a value < 1.')
    parser.add_argument('--verbose', action="store_true",   env_var="MQTT_CMD_VERBOSE", help='Logs debug messages.')
    
    return parser.parse_args()

def start() -> None:
    args = _parse_args()
    _setup_logging(args.verbose)
    _print_config(args)
    start_prometheus_server(args.prom_port)

    try:
        mqtt_conf = MqttConfig(args)
    except Exception as error:
        logging.error("Could not build mqtt configuration: %s", error)

    try:
        conf = ConfigBuilder.build(args.config)
    except Exception as error:
        logging.error("Could not build configuration: %s", error)
        sys.exit(1)

    MqttCommander(mqtt_conf, conf)