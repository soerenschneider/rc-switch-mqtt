from prometheus_client import Counter

prom_msg_error_cnt = Counter('iot_switches_electronic_433mhz_msg_send_errors_total', 'Errors while publishing messages', ['location'])
prom_reconnects = Counter('iot_switches_electronic_433mhz_mqtt_reconnects_total', 'Client reconnects', ['location'])
