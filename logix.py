import utime

# This is the main file you want to edit. You should provide here 2 methods: init and loop
# You can implement any of the funcs in defaults.py to override them

from vars import *
from digital_output import *


class Data:
    led_r = machine.Pin(api.PinOut.D5, mode=machine.Pin.OUT, value=1)
    led_l = machine.Pin(api.PinOut.D6, mode=machine.Pin.OUT, value=1)

    # This will play the role of a "non-optimistic" switch. We sync the led_* to it when we need
    curr_state = IntVar(mqtt_cmd='led_cmd', mqtt_get='led_get', init_value=0, min_value=0, max_value=1)
    last_state = curr_state.value()

    # This sets the amount of delay between the lights:
    t_delay = FloatVar(mqtt_cmd='delay_cmd', mqtt_get='delay_get', init_value=2000, min_value=0, max_value=10000)
    last_update_ms = None


def loop(curr_time_ms):
    if Data.curr_state.value() != Data.last_state:
        # Change detected. Select one LED and turn it on. If enough time passed, turn on both
        if Data.last_update_ms is None:
            r_goes_first = (curr_time_ms & 1) == 1
            set_first = Data.led_r if r_goes_first else Data.led_l
            set_first.value(1 - Data.curr_state.value())
            print("Turned %s to %d" % ("R" if r_goes_first else "L", Data.curr_state.value()))
            Data.last_update_ms = curr_time_ms
        elif utime.ticks_diff(curr_time_ms, Data.last_update_ms) > Data.t_delay.value():
            print("Turned both to %d" % Data.curr_state.value())
            Data.led_r.value(1 - Data.curr_state.value())
            Data.led_l.value(1 - Data.curr_state.value())
            Data.last_state = Data.curr_state.value()
            Data.last_update_ms = None




# def setup():
#     """Happens once when booting. Don't count on WiFi/MQTT connections"""
#     foo = DigitalOutput(api.PinOut.D4, 'led_cmd', 'led_get')


#
# def loop(curr_time_ms):
#     """Happens every so and so mSec. See config"""
#     pass
#
#
# def on_wifi_connect(network_name):
#     """You can query api.app.station() for more details"""
#     print("WiFi connected to %s" % network_name)
#
#
# def on_wifi_disconnect(network_name):
#     print("WiFi disconnected from %s" % network_name)
#
#
# def on_wifi_connect_fail(network_name):
#     print("WiFi connection to %s failed" % network_name)
#
#
# def on_mqtt(topic, payload):
#     """Handle whatever events you want to handle here"""
#     print("MQTT message:\n  topic %s\n  payload %s" % (topic, payload))
#
#
# def on_mqtt_connect():
#     """Not really much to do here... Topics from config are already subscribed for you"""
#     print("MQTT connected")
#
#
# def on_mqtt_disconnect():
#     """You can set mqtt_grace_period in the config file to get this after a certain timeout
#     You probably want to turn off things here, as the node is unreachable by smart home apps while no MQTT"""
#     print("MQTT disconnected")
#
#
# def on_mqtt_connect_fail():
#     """Will not call on_mqtt_disconnect. This probably means something with the setup is wrong."""
#     print("MQTT connection failed")
#
