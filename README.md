# rc-switch-mqtt

Provides an mqtt interface to interact with a 433mhz electric outlet. Easily integrable with [home assistant](https://www.home-assistant.io). Currently a suitable binary on the host is needed that emits the signals, such as [433utils](https://github.com/ninjablocks/433Utils). However, it's planned to use provide drop-in support for a python library, without the need of a external binary. 

## usage:
```
$ venv/bin/python3 rcswitch.py -h                                                                                                                                      
  usage: rc-switch-mqtt [-h] --id ID -c PLUG_CONFIG --mqtt-host MQTT_HOST
                        [--mqtt-topic MQTT_TOPIC] --binary BINARY
                        [--binary-off BINARY_OFF] [--prom-port PROM_PORT]
                        [--verbose]
  
  If an arg is specified in more than one place, then commandline values
  override environment variables which override defaults.
  
  optional arguments:
    -h, --help            show this help message and exit
    --id ID               Unique identifier for this plug. [env var: RC_ID]
    -c PLUG_CONFIG, --plug-config PLUG_CONFIG
                          Valid JSON example: {"plugs":[{"identifier":
                          "coffee_switch", "on":"binary arg to switch on",
                          "off":"binary arg to switch off"}]} [env var:
                          RC_CONFIG]
    --mqtt-host MQTT_HOST
                          The mqtt server to connect to [env var: RC_MQTT_HOST]
    --mqtt-topic MQTT_TOPIC
                          The topic to subscribe to [env var: RC_MQTT_TOPIC]
    --binary BINARY       The binary to execute when a switch cmd has been
                          received [env var: RC_BINARY]
    --binary-off BINARY_OFF
                          The binary to execute when a switch OFF cmd has been
                          received. If not specified, the same binary for
                          switching off and on is used. [env var: RC_BINARY_OFF]
    --prom-port PROM_PORT
                          The port of the prometheus http server. If you do not
                          want to run a prometheus server, supply a value < 1.
                          [env var: RC_PROMPORT]
    --verbose             Logs debug messages
```

## configuration
Easily configurable via JSON. Can be passed as parameter or ENV_VAR, support for reading from file is planned. 
```json
{
  "plugs": [
    {
      "identifier": "coffeemachine",
      "on": "xxxxx yyyyy 1",
      "off": "xxxxx yyyyy 0"
    }
  ]
}
```

Multiple plugs supported, each plug consists of a name and the parameter for sending the 'ON' and 'OFF' command to the adapter. 

## bootstrapping
```
$ make venv
```

## tests
```
$ make unittest
$ make integrationtest
```

## run it
```
$ venv/bin/python3 main.py --id kitchen -c='{"plugs":[{"identifier": "coffeemachine", "on":"xxxxx yyyyy 1", "off":"xxxxx yyyyy 0"}]}' --mqtt-host mqtt --verbose --binary=/opt/433Utils/RPi_utils/send
```

## interact with it

### switching it on
```
$ mosquitto_pub -h mqtt -t iot/switch/kitchen/coffeemachine/set -m on
```

### switching it off
```
$ mosquitto_pub -h mqtt -t iot/switch/kitchen/coffeemachine/set -m off
```
