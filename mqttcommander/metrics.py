import logging

from prometheus_client import Counter, Gauge, start_http_server

_prefix = 'mqtt_commander'

PROM_MQTT_IGNORED_MESSAGES = Counter(f'{_prefix}_mqtt_ignored_messages_total', 'Amount of ignored messages received', ['client_id', 'topic'])
PROM_MQTT_RECONNECTS = Counter(f'{_prefix}_mqtt_reconnects_total', 'Client reconnects', ['client_id'])
PROM_TRIGGERED_COMMANDS = Counter(f'{_prefix}_triggered_commands_total', 'Switch operations', ['client_id', 'topic', 'trigger'])
PROM_TRIGGERED_COMMANDS_ERRORS = Counter(f'{_prefix}_triggered_commands_errors_total', 'Switch operations', ['client_id', 'topic', 'trigger'])
PROM_CONF_TOPICS = Gauge(f'{_prefix}_topics_configured_total', 'Amount of configured plugs', ['client_id'])

def start_prometheus_server(port=0):
    """ Starts the prometheus http server. """
    if port < 1:
        logging.warning("Not starting prometheus http server (as port %d < 1)", port)
        return

    logging.info("Starting prometheus http server on port %d", port)
    start_http_server(port)
    logging.info("Successfully set up prometheus server!")