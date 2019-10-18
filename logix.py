# This is the main file you want to edit.
# For basic cases, you only need to instantiate any of the 'handlers' (e.g. DigitalOutput, DHTSensor, ...)
# For advanced cases you should [also] override here any of the funcs in defaults.py

from vars import *
from digital_output import *
from dht_handler import DHTSensor
from handlers import PeriodicHandler
import machine
import utime


class Data:
    # Have 2 GPIOs controlling relays:
    led_r = machine.Pin(api.PinOut.D5, mode=machine.Pin.OUT, value=1)
    led_l = machine.Pin(api.PinOut.D6, mode=machine.Pin.OUT, value=1)

    # This will play the role of a "non-optimistic" switch. We sync the led_* to it when we need
    curr_state = IntVar(mqtt_cmd='led_cmd', mqtt_get='led_get', init_value=0, min_value=0, max_value=1)
    last_state = curr_state.value()

    # This sets the amount of delay between the lights:
    t_delay = FloatVar(mqtt_cmd='delay_cmd', mqtt_get='delay_get', init_value=2000, min_value=0, max_value=10000)
    last_update_ms = None

    # Have a DHT in hand:
    dht = DHTSensor(pin_name="D4", mqtt_get='dht_get')



def loop(curr_time_ms):
    if Data.curr_state.value() != Data.last_state:
        print(Data.curr_state.value(), Data.last_state)
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


print("\nLogix: File loaded successfully\n")




