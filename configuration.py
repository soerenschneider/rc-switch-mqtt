import logging

PLUGS = "plugs"
IDENTIFIER = "identifier"
ON = "on"
OFF = "off"
PLUG_FIELDS = [IDENTIFIER, ON, OFF]

class SwitchConfiguration:
    def __init__(self, config):
        self.validate(config)
        self.plugs = config[PLUGS]
        logging.info("Loaded %d configured plugs", len(self.plugs))

    def validate(self, config):
        if not config:
            raise ValueError("Empty configuration supplied")

        if PLUGS not in config:
            raise ValueError("Missing 'plugs' field in JSON")

        if len(config[PLUGS]) < 1:
            raise ValueError("No plugs defined")

        for plug in config[PLUGS]:
            for field in PLUG_FIELDS:
                if field not in plug:
                    raise ValueError("plug has no '{}' set".format(field))

    def get_config_for_plug(self, plug_name):
        """ Try to find the configuration for a given plug. Returns None if no matching configuration was found. """
        for plug in self.plugs:
            if plug[IDENTIFIER] == plug_name:
                return plug

        logging.info("Did not find plug %s in plugs", plug_name)
        return None