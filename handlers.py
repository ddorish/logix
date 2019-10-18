# This file is for auto-handled devices. If you only want to have a simple MQTT switch, no need to write lotta-code
import api
import utime
import machine

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
        if not self.no_auto:
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


class PeriodicHandler(AutoHandlers):
    """"Run a custom function on a timer or by special demand"""
    def __init__(self, func, mqtt_get=None, report_rate_ms=120000, no_auto=False, *args, **kwargs):
        self.func = func
        self.mqtt_get_topic = api.app.conf.get(mqtt_get, '/String/%s/cmd_topic/not/found' % mqtt_get)
        self.args = args
        self.kwargs = kwargs
        self.report_rate_ms = int(as_float(report_rate_ms))
        self.no_auto = no_auto
        self.last_report_msec = None
        self.need_report = True
        self.setup()
        super(self.__class__, self).__init__()

    def setup(self):
        self.last_report_msec = None

    def execute(self):
        self.func(*self.args, **self.kwargs)
        self.need_report = False

    def set_to(self, *args, **kwargs):
        self.execute()

    def loop(self, curr_time_ms):
        self.need_report = self.need_report or \
                           (self.mqtt_get_topic is not None and
                            (self.last_report_msec is None or
                             utime.ticks_diff(curr_time_ms, self.last_report_msec) > self.report_rate_ms))

        if self.need_report:
            self.execute()
            self.last_report_msec = curr_time_ms

