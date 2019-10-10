from prometheus_client import Counter, Gauge

_prefix = 'iot_switches_electronic_433mhz'
prom_msg_error_cnt = Counter('{prefix}_mqtt_invalid_messages_total'.format(prefix=_prefix), 'Amount of invalid messages received', ['location', 'cause'])
prom_reconnects = Counter('{prefix}_mqtt_reconnects_total'.format(prefix=_prefix), 'Client reconnects', ['location'])
prom_switch_operations = Counter('{prefix}_switch_operations_total'.format(prefix=_prefix), 'Switch operations', ['location', 'operation'])
prom_configured_plugs = Gauge('{prefix}_configured_plugs_total'.format(prefix=_prefix), 'Amount of configured plugs', ['location'])

