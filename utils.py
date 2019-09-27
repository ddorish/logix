import network
from reader import read_config
from umqttsimple import MQTTClient
import utime
import machine
import micropython
import api
import gc


from defaults import *

class App:
    _conn_states = ['boot', 'wifi_trying', 'wifi_up', 'mqtt_trying', 'mqtt_up']

    def __init__(self):
        self._is_running = False
        self._current_state = 0
        self._state_start_time = 0
        self._state_aux_var = 0
        self._station = None
        self._mqtt_client = None
        self._last_ip_report = True
        self._last_mqtt_connect_time = False  # False/True: Not/connected. int: Connected for a short time
        self.autos_mqtt_topics = {}  # {Topic: [handlers, ]} for objects framework automatically handles e.g. MqttSwitch
        self.autos_with_loop = []
        self.autos_full_list = []
        self.conf = read_config()
        api.app = self
        setup()

    def register(self, auto_obj, topics_list):
        self.autos_full_list.append(auto_obj)
        if hasattr(auto_obj, 'loop'):
            self.autos_with_loop.append(auto_obj)
        for topic in topics_list:
            topic_addressees = self.autos_mqtt_topics.get(topic, [])
            topic_addressees.append(auto_obj)
            self.autos_mqtt_topics[topic] = topic_addressees

    def run_func_on_handlers(self, func_name, *args, **kwargs):
        """Run a specific function on all handlers if exists.
        loop and on_mqtt have special treatments, to not waste too much resources every iteration"""
        for i, auto in enumerate(self.autos_full_list):
            if hasattr(auto, func_name):
                try:
                    getattr(auto, func_name)(*args, **kwargs)
                except Exception as e:
                    print("Error evaluating %s on auto %d (of type %s):\n%s" % (func_name, i, type(auto), e))

    def on_mqtt(self, topic, payload):
        """A mediator between the user's on_mqtt and the "auto" objects (e.g. MqttSwitch)
        This enables us to call both user's and auto's on_mqtt"""
        topic = topic.decode('utf-8')
        payload = payload.decode('utf-8')
        for i, auto in enumerate(self.autos_mqtt_topics.get(topic, [])):
            try:
                auto.on_mqtt(topic, payload)
            except Exception as e:
                print("Error evaluating on_mqtt of auto %d (of type %s):\n%s" % (i, type(auto), e))
        # And call the rest...
        on_mqtt(topic, payload)

    def on_wifi_connect(self, *args, **kwargs):
        self.run_func_on_handlers('on_wifi_connect', *args, **kwargs)
        try:
            on_wifi_connect(*args, **kwargs)
        except Exception as err:
            print("Error running on_wifi_connect: %s" % str(err))

    def on_wifi_connect_fail(self, *args, **kwargs):
        self.run_func_on_handlers('on_wifi_connect_fail', *args, **kwargs)
        try:
            on_wifi_connect_fail(*args, **kwargs)
        except Exception as err:
            print("Error running on_wifi_connect_fail: %s" % str(err))

    def on_wifi_disconnect(self, *args, **kwargs):
        self.run_func_on_handlers('on_wifi_disconnect', *args, **kwargs)
        try:
            on_wifi_disconnect(*args, **kwargs)
        except Exception as err:
            print("Error running on_wifi_disconnect: %s" % str(err))

    def on_mqtt_connect(self, *args, **kwargs):
        self.run_func_on_handlers('on_mqtt_connect', *args, **kwargs)
        try:
            on_mqtt_connect(*args, **kwargs)
        except Exception as err:
            print("Error running on_mqtt_connect: %s" % str(err))

    def on_mqtt_connect_fail(self, *args, **kwargs):
        self.run_func_on_handlers('on_mqtt_connect_fail', *args, **kwargs)
        try:
            on_mqtt_connect_fail(*args, **kwargs)
        except Exception as err:
            print("Error running on_mqtt_connect_fail: %s" % str(err))

    def on_mqtt_disconnect(self, *args, **kwargs):
        self.run_func_on_handlers('on_mqtt_disconnect', *args, **kwargs)
        try:
            on_mqtt_disconnect(*args, **kwargs)
        except Exception as err:
            print("Error running on_mqtt_disconnect: %s" % str(err))

    def _get_conn_state(self):
        """Get connectivity state"""
        ms_in_state = utime.ticks_diff(utime.ticks_ms(), self._state_start_time)
        return self._conn_states[self._current_state], ms_in_state

    def _conn_state_of(self, which):
        return self._conn_states.index(which)

    def _set_conn_state(self, which):
        self._current_state = self._conn_state_of(which)
        self._state_start_time = utime.ticks_ms()

    def wifi_connected(self):
        station = self._station
        return station is not None and station.isconnected()

    def mqtt_connected(self):
        client = self._mqtt_client
        if client is None:
            return False
        ping_age = client.ms_since_server_seen()
        return ping_age is not None and ping_age < 5000  # mSec

    def publish(self, topic, payload, retain=False, qos=0):
        if not self.mqtt_connected():
            return False
        self._mqtt_client.publish(topic, str(payload), retain=retain, qos=qos)

    def run(self):
        self._is_running = True
        self.loop()

    def stop(self):
        self._is_running = False

    def loop(self, *args):
        """This function is performed every XXX mSec"""
        self.curr_loop_time_ms = utime.ticks_ms()
        self._check_wifi()
        self._check_mqtt()
        self._maybe_mqtt_disconnect_timeout()
        if self.mqtt_connected():
            self._mqtt_client.check_msg()
        for auto_with_loop in self.autos_with_loop:
            auto_with_loop.loop(self.curr_loop_time_ms)
        try:
            loop(self.curr_loop_time_ms)
        except Exception as err:
            print("Error when evaluating user's loop function:\n%s" % err)
        if self._is_running:
            machine.Timer(1).init(mode=machine.Timer.ONE_SHOT, period=150, callback=schedule_run)

    def _check_wifi(self):
        """Make sure WIFI ok. Will increment self.current_state accordingly"""
        current_state, ms_in_state = self._get_conn_state()
        conf = self.conf
        wifi_ssid = conf.get('wifi_ssid', 'pynode_config')
        wifi_pass = conf.get('wifi_pass', '12345')

        if self._conn_state_of('wifi_up') <= self._current_state:
            # Just make sure it's still up
            if self.wifi_connected():
                # All cool! That should happen most of the times.
                return
            self.on_wifi_disconnect(wifi_ssid)
            self._set_conn_state('boot')

        if current_state == 'boot':
            # Need to setup the WiFi interface:
            print("Setting WiFi interface")
            conf = self.conf
            network.WLAN(network.AP_IF).active(False)
            station = network.WLAN(network.STA_IF)
            station.active(True)
            station.connect(wifi_ssid, wifi_pass)
            self._station = station
            print("Attempting to connect...")
            self._set_conn_state('wifi_trying')
            self._state_aux_var = 0  # Says when was last query of station.status
        elif current_state == 'wifi_trying':
            if ms_in_state > self._state_aux_var + 1500:
                # Passed 200 mSec since last check. Can try again
                self._state_aux_var = ms_in_state
                if self._station.isconnected():
                    self.on_wifi_connect(wifi_ssid)
                    self._set_conn_state('wifi_up')
                    return
            if ms_in_state > 15000:
                self.on_wifi_connect_fail(wifi_ssid)
                self._set_conn_state('boot')

    def _check_mqtt(self):
        current_state, _ = self._get_conn_state()
        conf = self.conf
        if not 'mqtt_server' in conf:
            # Bad config. Cannot do anything
            return
        if self._current_state < self._conn_state_of('wifi_up'):
            # No WiFi. Byebye
            return

        if self._conn_state_of('mqtt_up') <= self._current_state:
            # MQTT allegedly connected. Just make sure we're still in...
            if self.mqtt_connected():
                return
            print("MQTT connection temporarily lost...")

        # Here it means WiFi is up, and MQTT not... Let's give it a try
        # Note: This can somewhat hang the python interpeter, when it's waiting for the socket probably
        self._set_conn_state('mqtt_trying')
        conf = self.conf
        server = conf.get('mqtt_server')
        port = conf.get('mqtt_port')
        user = conf.get('mqtt_user')
        password = conf.get('mqtt_pass')
        print("Mqtt-connecting device %s to server %s, port %s, user=%s, pass of %d chars" % (
            api.uid(), server, port, user, 0 if password is None else len(password)))
        self._mqtt_client = MQTTClient(client_id=api.uid(), server=server, port=port, user=user, password=password)
        if self._mqtt_client.connect():
            self._mqtt_client.set_callback(self.on_mqtt)
            conf_keys_listen = conf.get('mqtt_listen', '').split()
            auto_topics = self.autos_mqtt_topics.keys()
            conf_topics = [conf.get(k) for k in conf_keys_listen]
            for topic in set(conf_topics).union(set(auto_topics)):
                if topic is None:
                    continue
                print("Subscribing to %s" % topic)
                self._mqtt_client.subscribe(topic)
            self.on_mqtt_connect()
            self._set_conn_state('mqtt_up')
            self._last_mqtt_connect_time = utime.ticks_ms()
            return
        self.on_mqtt_connect_fail()

    def _maybe_mqtt_disconnect_timeout(self):
        """Check if MQTT is disconnected for XXX mSec, and if so, run callback"""
        if type(self._last_mqtt_connect_time) is int:
            dtime = int(self.conf.get('mqtt_grace_period_ms', 120000))
            if utime.ticks_diff(utime.ticks_ms(), self._last_mqtt_connect_time) > dtime:
                self._last_mqtt_connect_time = True
        if self._last_mqtt_connect_time is True and not self.mqtt_connected():
            self._last_mqtt_connect_time = False
            print("MQTT is disconnected for long enough")
            self.on_mqtt_disconnect()

    def station(self):
        return self._station


def schedule_run(*args):
    micropython.schedule(api.app.loop, None)


# Generate everything...
App()

gc.collect()
print("Before importing logix.py: %d mem free" % gc.mem_free())

# Load user data
try:
    from logix import *
except Exception as e:
    err = e
    status_msg = "Error in logix.py: %s: %s" % (type(err), str(err))
    print(status_msg)  # Will only be seen if connected via serial

gc.collect()
print("After utils.py: %d mem free" % gc.mem_free())
