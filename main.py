import logging
import json
import configargparse

from prometheus_client import start_http_server
from mqttbackend import MqttListener
from transmitter import Transmitter
from configuration import SwitchConfiguration

from metrics import prom_configured_plugs

class Main:
    def __init__(self, args):
        self.args = args
        self.validate_topic(args.mqtt_topic)
        self.print_config()
        self.setup_prometheus()
        self.topic = self.args.mqtt_topic.format(self.args.id)

    def setup_prometheus(self):
        """ Starts the prometheus http server. """
        if self.args.prom_port < 1:
            logging.info("NOT starting prometheus http server (as prom_port < 1)")
            return

        logging.info("Starting prometheus http server on port %s", self.args.prom_port)
        start_http_server(self.args.prom_port)
        logging.info("Successfully set up prometheus server!")

    def print_config(self):
        logging.info("Started rc switch mqtt...")
        logging.info("Using id=%s", self.args.id)
        logging.info("Using binary=%s", self.args.binary)
        logging.info("Using binary-off=%s", self.args.binary_off)
        logging.info("Using plugconfig=%s", self.args.plug_config)
        logging.info("Using mqtt-host=%s", self.args.mqtt_host)
        logging.info("Using mqtt-topic=%s", self.args.mqtt_topic)
        logging.info("Using prom-port=%s", self.args.prom_port)
        logging.info("Using verbose=%s", self.args.verbose)

    def validate_topic(self, topic):
        if not topic or '+' not in topic:
            raise ValueError("No wildcard (+) found in topic.")

    def run(self):
        config = SwitchConfiguration(self.args.plug_config)
        prom_configured_plugs.labels(location=self.args.id).set(len(config.plugs))
        transmitter = Transmitter(configuration=config, binary=self.args.binary, binary_off=self.args.binary_off)
        mqtt = MqttListener(host=self.args.mqtt_host, location=self.args.id, topic=self.topic, transmitter=transmitter)
        mqtt.connect()

def setup_logging(args):
    """ Sets up the logging. """
    loglevel = logging.INFO
    if args.verbose:
        loglevel = logging.DEBUG
    logging.basicConfig(level=loglevel, format='%(levelname)s\t %(asctime)s %(message)s')

def parse_args():
    """ Parsing command line arguments """
    parser = configargparse.ArgumentParser(prog='tempsensor')

    parser.add_argument('--id', action="store", env_var="RC_ID", required=True, help='Unique identifier for this plug.')
    parser.add_argument('-c', '--plug-config', action='store', type=json.loads, env_var="RC_CONFIG", required=True, help='Valid JSON example: {"plugs":[{"identifier": "coffee_switch", "on":"binary arg to switch on", "off":"binary arg to switch off"}]}')

    parser.add_argument('--mqtt-host', action='store', env_var='RC_MQTT_HOST', required=True, help='The mqtt server to connect to')
    parser.add_argument('--mqtt-topic', action='store', env_var='RC_MQTT_TOPIC', default="iot/switch/{}/+/set", help='The topic to subscribe to')

    parser.add_argument('--binary', action='store', env_var='RC_BINARY', required=True, help='The binary to execute when a switch cmd has been received')
    parser.add_argument('--binary-off', action='store', env_var='RC_BINARY_OFF', help='The binary to execute when a switch OFF cmd has been received. If not specified, the same binary for switching off and on is used. ')

    parser.add_argument('--prom-port', action="store", env_var="RC_PROMPORT", type=int, default=9193, help='The port of the prometheus http server. If you do not want to run a prometheus server, supply a value < 1.')
    parser.add_argument('--verbose', action="store_true", help='Logs debug messages.')
    
    return parser.parse_args()

def main():
    args = parse_args()
    setup_logging(args)
    Main(args).run()

if __name__=="__main__":
    main()