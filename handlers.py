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
