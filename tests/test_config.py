from mqttcommander.config import ConfigBuilder
import json
import unittest

class Test_TestIncrementDecrement(unittest.TestCase):
    def test_valid_config(self):
        conf = ConfigBuilder.build("tests/configs/config-valid.json")
        self.assertIsNotNone(conf)

        self.assertEqual(2, len(conf))

        self.assertTrue("topic1" in conf)
        self.assertTrue("topic2" in conf)

        self.assertEqual(["sleep", "30"], conf["topic1"].triggers["on"])
        self.assertEqual(["touch", "/tmp/test"], conf["topic1"].triggers["off"])

        self.assertEqual(["touch", "/tmp/bla"], conf["topic2"].triggers[""])

    def test_edge_none(self):
        self.assertRaises(ValueError, ConfigBuilder.build, None)

    def test_invalid_missing_file(self):
        self.assertRaises(FileNotFoundError, ConfigBuilder.build, "tests/configs/doesntexist.json")

    def test_invalid_json(self):
        self.assertRaises(json.decoder.JSONDecodeError, ConfigBuilder.build, "tests/configs/config-empty.json")

    def test_invalid_config_missing_topics(self):
        self.assertRaises(ValueError, ConfigBuilder.build, "tests/configs/config-invalid-missing-topics.json")

    def test_invalid_config_missing_cmds(self):
        self.assertRaises(ValueError, ConfigBuilder.build, "tests/configs/config-invalid-missing-cmds.json")

    def test_invalid_config_missing_triggers(self):
        self.assertRaises(ValueError, ConfigBuilder.build, "tests/configs/config-invalid-missing-triggers.json")

    def test_invalid_config_missing_root_node(self):
        self.assertRaises(ValueError, ConfigBuilder.build, "tests/configs/config-invalid-missing-root-node.json")


if __name__ == '__main__':
    unittest.main()