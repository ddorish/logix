# This file is for auto-handled devices. If you only want to have a simple MQTT switch, no need to write lotta-code
import machine
import api


def as_float(val, default=0.):
    """Convert val to an int. use default if conversion fails"""
    try:
        return float(val)
    except ValueError:
        return default


def as_lowercase(val: any):
    """Convert to lowercase if possible"""
    try:
        return val.lower()
    except AttributeError:
        return val


class AutoHandlers:
    """Base class for all 'auto-handlers'. They must have value, publish, init. They can have the on_* funcs"""
    # def on_mqtt(self, topic, payload): pass
    # def on_wifi_connect(self, network_name): pass
    # def on_wifi_connect_fail(self, network_name): pass
    # def on_wifi_disconnect(self, network_name): pass
    # def on_mqtt_connect(self): pass
    # def on_mqtt_connect_fail(self): pass
    # def on_mqtt_disconnect(self): pass
    no_auto = False
    mqtt_cmd_topic = None
    mqtt_get_topic = None

    def __init__(self):
        if not self.no_auto and self.mqtt_cmd_topic is not None:
            api.app.register(self, [self.mqtt_cmd_topic])

    def publish(self):
        if self.mqtt_get_topic is not None:
            # Send an ack
            api.app.publish(self.mqtt_get_topic, self.value())

    def on_mqtt(self, topic, payload):
        if topic == self.mqtt_cmd_topic:
            pay_strip = payload.strip()
            self.set_to(pay_strip)

    def value(self):
        assert False, "You must override this function"

    def set_to(self, *args, **kwargs):
        """Handlers with writable state should override this"""
        pass




