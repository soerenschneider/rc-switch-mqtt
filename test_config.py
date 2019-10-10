from configuration import SwitchConfiguration
import json
import unittest

class Test_TestIncrementDecrement(unittest.TestCase):
    def test_obj_creation_empty(self):
        json_string = '{}'
        parsed = json.loads(json_string)
        with self.assertRaises(ValueError): 
            SwitchConfiguration(parsed)

    def test_obj_creation(self):
        json_string = '{"plugs":[{"identifier": "coffee", "on":"11", "off":"2"}]}'
        parsed = json.loads(json_string)
        config = SwitchConfiguration(parsed)
        self.assertIsNotNone(config)

    def test_config_for_plug(self):
        json_string = '{"plugs":[{"identifier": "coffee", "on":"11", "off":"2"}]}'
        parsed = json.loads(json_string)
        config = SwitchConfiguration(parsed)
        plug = config.get_config_for_plug("coffee")
        self.assertIsNotNone(plug)
        self.assertEqual(plug['on'], "11")

    def test_config_for_plug_unknown(self):
        json_string = '{"plugs":[{"identifier": "coffee", "on":"11", "off":"2"}]}'
        parsed = json.loads(json_string)
        config = SwitchConfiguration(parsed)
        plug = config.get_config_for_plug("unknown")
        self.assertIsNone(plug)


if __name__ == '__main__':
    unittest.main()