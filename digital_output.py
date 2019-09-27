import gc
from handlers import *


class DigitalOutput(AutoHandlers):
    """Shortcut for having an mqtt-contrrolled pinout"""
    def __init__(self, pin_name, mqtt_cmd, mqtt_get=None, init_value=0, inverse_logic=True,
                 pin_mode=machine.Pin.OUT, no_auto=False):
        """
        Construct an MQTT-controlled pinout
        :param pin_name: Pin name, like 'D5'
        :param conf_cmd: Conf field name to receive commands on.
        :param conf_get: Conf field name to send status on. None for "optimistic" mode (in Home Assistant)
        :param init_value: 0 for OFF, 1 for ON. Affected by inverse_logic
        :param inverse_logic: On most ESP8266 it's True
        :param pin_mode: Usually machine.Pin.OUT
        :param no_auto: Don't handle automatically mqtt commands on this pin
        """
        self.inverse_logic = 1 if inverse_logic else 0
        self.pin_name = pin_name
        self.init_value = init_value
        self.pin_mode = pin_mode
        self.no_auto = no_auto
        self.mqtt_cmd_topic = api.app.conf.get(mqtt_cmd, '/DigitalOutput/pin_%s/cmd_topic/not/found' % mqtt_cmd)
        self.mqtt_get_topic = api.app.conf.get(mqtt_get, None)
        self.pin = None
        self.setup()
        super(self).__init__()

    def setup(self):
        self.pin = machine.Pin(api.PinOut.resolve(self.pin_name), mode=self.pin_mode)
        self.set_to(self.init_value)

    def toggle(self):
        self.set_to(1 - self.value())

    def set_to(self, new_value):
            new_value_int = 1 if as_lowercase(new_value) in ['1', 'on', 'yes', 'true'] else 0
            self.pin.value((self.inverse_logic + new_value_int) & 1)
            self.publish()

    def value(self):
        return (self.inverse_logic + self.pin.value()) & 1

    def on_mqtt_disconnect(self):
        self.setup()


gc.collect()
