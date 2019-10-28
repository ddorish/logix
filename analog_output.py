from handlers import *


class AnalogOutput(AutoHandlers):
    """Shortcut for having an mqtt-contrrolled pinout"""
    min_duty = 0
    max_duty = 1023
    mid_duty = (min_duty + max_duty) / 2

    def __init__(self, pin_name, mqtt_cmd, mqtt_get=None, init_value=0, inverse_logic=True,
                 freq=500, no_auto=False):
        """
        Construct an MQTT-controlled pinout
        :param pin_name: Pin name, like 'D5'
        :param mqtt_cmd: Conf field name to receive commands on.
        :param mqtt_get: Conf field name to send status on. None for "optimistic" mode (in Home Assistant)
        :param init_value: 0 for OFF, 1 for ON. Affected by inverse_logic
        :param inverse_logic: Make 0 the darkest and 1023 the brightest
        :param freq: PWM Freq. 500 is a nice value after all
        :param no_auto: Don't handle automatically mqtt commands on this pin
        """
        self.inverse_logic = 1 if inverse_logic else 0
        self.pin_name = pin_name
        self.init_value = init_value
        self.freq = freq
        self.no_auto = no_auto
        self.mqtt_cmd_topic = api.app.conf.get(mqtt_cmd, '/DigitalOutput/pin_%s/cmd_topic/not/found' % mqtt_cmd)
        self.mqtt_get_topic = api.app.conf.get(mqtt_get, None)
        self.pin = None
        self.curr_value = None
        self.setup()
        super(self.__class__, self).__init__()

    def setup(self):
        self.pin = machine.PWM(machine.Pin(api.PinOut.resolve(self.pin_name)), freq=self.freq)
        self.set_to(self.init_value)

    def toggle(self):
        self.set_to(1 - self.value())

    def set_to(self, new_value):
            new_value_int = int(min(self.max_duty, max(self.min_duty, as_float(new_value, self.mid_duty))))
            self.curr_value = new_value_int
            self.pin.duty(int(self.value_mapped()))
            self.publish()

    def value_mapped(self):
        """Take care of the inverse_logic, as well as  non-linear mapping to match the LED's actual behavior"""
        v2 = self.curr_value if self.inverse_logic else self.max_duty - self.curr_value
        range = (self.max_duty - self.min_duty)
        offset = (v2 - self.min_duty)
        v3 = int(self.min_duty + (offset / range) ** .5  * range)
        print("v3=", v3)
        return v3

    def value(self):
        return self.curr_value

    def on_mqtt_disconnect(self):
        self.setup()

