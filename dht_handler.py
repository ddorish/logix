import api
from handlers import *
import dht
import utime
import machine

class DHTSensor(AutoHandlers):

    def __init__(self, pin_name, mqtt_get=None, report_rate_ms=120000, measure_rate_ms=None, no_auto=False, dht_type=22):
        self.pin_name = pin_name
        self.mqtt_get_topic = api.app.conf.get(mqtt_get, None)
        self.report_rate_ms = int(as_float(report_rate_ms))
        self.measure_rate_ms = measure_rate_ms
        self.no_auto = no_auto
        self.dht_type = dht_type
        self.pin = None
        self.sensor = None
        self.last_report_msec = None
        self.last_measure_msec = None
        self.is_valid = False
        self.need_report = True
        self.need_measure = True
        self.setup()
        super(self.__class__, self).__init__()

    def setup(self):
        self.sensor = (dht.DHT11 if self.dht_type == 11 else dht.DHT22)(machine.Pin(api.PinOut.resolve(self.pin_name)))
        self.last_report_msec = None
        self.last_measure_msec = None
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
                api.app.publish('/'.join([self.mqtt_get_topic.rstrip('/'), 'temperature']), temp) and \
                api.app.publish('/'.join([self.mqtt_get_topic.rstrip('/'), 'humidity']), humi)
            return did_publish

    def loop(self, curr_time_ms):
        self.need_report = self.need_report or \
                           (self.mqtt_get_topic is not None and
                            (self.last_report_msec is None or
                             utime.ticks_diff(curr_time_ms, self.last_report_msec) > self.report_rate_ms))
        if self.measure_rate_ms is None:
            self.need_measure = self.need_report
        else:
            self.need_measure = self.need_measure or \
                                (self.last_measure_msec is None or
                                 utime.ticks_diff(curr_time_ms, self.last_measure_msec) > self.measure_rate_ms)
        if self.need_measure or self.need_report:
            self.read()
            if self.is_valid:
                self.last_measure_msec = curr_time_ms
                self.need_measure = False
                if self.need_report and self.publish():
                    self.last_report_msec = curr_time_ms
                    self.need_report = False

