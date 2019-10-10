from mqttbackend import MqttListener
import unittest

class Test_TestIncrementDecrement(unittest.TestCase):
    def test_obj_creation_empty(self):
        with self.assertRaises(ValueError): 
            MqttListener(host=None, location="", topic="", transmitter="")

    def test_obj_creation(self):
        mqtt = MqttListener(host="host", location="location", topic="topic", transmitter="sender")
        self.assertIsNotNone(mqtt)

    def test_extract_plugname_not_found(self):
        mqtt = MqttListener(host="host", location="location", topic="topic", transmitter="sender")
        plug_name = mqtt.extract_plug_name("bla")
        self.assertIsNone(plug_name)

    def test_extract_plugname_prefix(self):
        mqtt = MqttListener(host="host", location="location", topic="prefix/+", transmitter="sender")
        plug_name = mqtt.extract_plug_name("prefix/plugname")
        self.assertEqual(plug_name, "plugname")

    def test_extract_plugname_weird_format(self):
        mqtt = MqttListener(host="host", location="location", topic="+", transmitter="sender")
        plug_name = mqtt.extract_plug_name("plugname")
        self.assertEqual(plug_name, "plugname")

    def test_extract_plugname_weird_suffix(self):
        mqtt = MqttListener(host="host", location="location", topic="+/suffix", transmitter="sender")
        plug_name = mqtt.extract_plug_name("plugname/suffix")
        self.assertEqual(plug_name, "plugname")

    def test_extract_plugname(self):
        mqtt = MqttListener(host="host", location="location", topic="prefix/+/suffix", transmitter="sender")
        plug_name = mqtt.extract_plug_name("prefix/plugname/suffix")
        self.assertEqual(plug_name, "plugname")

if __name__ == '__main__':
    unittest.main()