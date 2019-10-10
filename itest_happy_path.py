from main import Main, setup_logging
import json
import configargparse
import unittest
from threading import Thread
from time import sleep
import paho.mqtt.client as mqtt
import os.path

class Test_Integration(unittest.TestCase):
    def test_obj_creation_empty(self):
        f = "/tmp/rc-switch-integrationtest"
        if os.path.isfile(f):
            os.remove(f)

        self.assertFalse(os.path.isfile(f))

        args = configargparse.Namespace(id="bla",mqtt_topic="iot/switch/{}/+/set",mqtt_host="localhost",binary="touch",binary_off="rm",plug_config=json.loads('{"plugs":[{"identifier": "inttest", "on":"/tmp/rc-switch-integrationtest", "off":"/tmp/rc-switch-integrationtest"}]}'),prom_port=0,verbose=True)
        setup_logging(args)
        impl = Main(args)
        thread = Thread(target=self.bla, args = (impl, ))
        thread.start()
        sleep(2)
        client = mqtt.Client()
        client.connect("localhost", 1883, 60)
        client.publish("iot/switch/bla/inttest/set", "on")
        sleep(2)
        self.assertTrue(os.path.isfile(f))
        client.publish("iot/switch/bla/inttest/set", "off")
        sleep(2)
        self.assertFalse(os.path.isfile(f))
        client.disconnect()
        impl.quit()
        thread.join()

    def bla(self, impl):
        print(impl)
        impl.run()
        
if __name__ == '__main__':
    unittest.main()