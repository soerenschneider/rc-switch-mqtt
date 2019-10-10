import subprocess
import logging
import time
from threading import Lock

class Transmitter:
    def __init__(self, configuration, binary, binary_off=None):
        if not configuration:
            raise ValueError("No configuration defined")
        self.plugs = configuration

        if not binary:
            raise ValueError("No binary defined")
        self.binary = dict()
        self.binary['on'] = binary

        if not binary_off:
            binary_off = binary
        self.binary['off'] = binary_off

        self.lock = Lock()

    def send_signal(self, plug_name, payload):
        """ Sends a signal to the plug. """
        if not payload:
            logging.warn("Empty payload received")
            return

        plug_configuration = self.plugs.get_config_for_plug(plug_name)
        if not plug_configuration:
            return
        
        with self.lock:
            cmd = plug_configuration[payload].split()
            logging.debug("Sending '%s' cmd: %s %s", payload, self.binary, cmd)
            subprocess.Popen([self.binary[payload], *cmd])
