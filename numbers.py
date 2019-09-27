import gc
from handlers import *


class FloatNumber(AutoHandlers):
    """Represent an MQTT-controlled floating point number variable."""
    def __init__(self, mqtt_cmd, mqtt_get=None, init_value=0, min_value=0, max_value=100, no_auto=False):
        self.min_value = as_float(min_value, 0)
        self.max_value = as_float(max_value, self.min_value + 100)
        self.init_value = as_float(init_value, self.min_value)
        self.no_auto = no_auto
        self.mqtt_cmd_topic = api.app.conf.get(mqtt_cmd, '/Number/%s/cmd_topic/not/found' % mqtt_cmd)
        self.mqtt_get_topic = api.app.conf.get(mqtt_get, None)
        self.val = None
        self.setup()
        if not no_auto:
            api.app.register(self, [self.mqtt_cmd_topic])

    def setup(self):
        self.set_to(self.init_value)

    def value(self):
        return self.val

    def set_to(self, new_value):
        try:
            new_value = as_float(new_value, None)
            if new_value is not None:
                self.val = new_value
                self.publish()
        except Exception as err:
            print("Error setting value %s for Number: %s" % (new_value, err))
            import sys
            sys.print_exception(err)


class IntNumber(FloatNumber):
    def value(self):
        return int(self.val) if self.val is not None else None


gc.collect()
