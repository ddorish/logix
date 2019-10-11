import api
from handlers import *
import dht
import utime

class DHTSensor(AutoHandlers):

    def __init__(self, pin_name, mqtt_get=None, report_rate_ms=2000, measure_rate_ms=1000, no_auto=False, dht_type=22):
        self.pin_name = pin_name
        self.mqtt_get_topic = api.app.conf.get(mqtt_get, None)
        self.report_rate_ms = int(as_float(report_rate_ms))
        self.measure_rate_ms = measure_rate_ms
        self.no_auto = no_auto
        self.dht_type = dht_type
        self.pin = None
        self.sensor = None
        self.last_transmit_msec = None
        self.last_measure_msec = None
        self.temperature = None
        self.humidity = None
        self.is_valid = False
        self.setup()
        a = super(self)
        print(a)
        print(a.__init__)
        super(self).__init__()

    def setup(self):
        self.sensor = (dht.DHT11 if self.dht_type == 11 else dht.DHT22)(api.PinOut.resolve(self.pin_name))
        self.last_transmit_msec = None
        self.last_measure_msec = None
        self.temperature = None
        self.humidity = None
        self.is_valid = False

    def read(self):
        try:
            self.sensor.measure()
            self.is_valid = True
        except OSError:
            self.is_valid = False

    def publish(self):
        if self.mqtt_get_topic is not None:
            temp = str(self.sensor.temperature()) if self.is_valid else 'Problem'
            humi = str(self.sensor.humidity()) if self.is_valid else 'Problem'
            did_publish = \
                api.app.publish('/'.join([self.mqtt_get_topic, 'temperature']), temp) and \
                api.app.publish('/'.join([self.mqtt_get_topic, 'humidity']), humi)
            return did_publish

    def loop(self, curr_time_ms):
        if self.last_measure_msec is None or \
                utime.ticks_diff(curr_time_ms, self.last_measure_msec) > self.measure_rate_ms:
            self.read()
            self.last_measure_msec = curr_time_ms
        if self.mqtt_get_topic is not None:
            return
        if self.last_transmit_msec is None or \
                utime.ticks_diff(curr_time_ms, self.last_transmit_msec) > self.report_rate_ms:
            if self.publish():
                self.report_rate_ms = curr_time_ms


print("Finished importing dht_handler.py")
