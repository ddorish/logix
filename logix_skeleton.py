# This is the main file you want to edit. You should provide here 2 methods: init and loop
# You can implement the following additional methods:
# on_mqtt(topic, payload) - Will be called when a message arrives
# on_mqtt_connect_fail() - Will be called if we cannot connect to broker
# on_mqtt_connect, on_mqtt_disconnect - What to do when MQTT does like this
# on_wifi_connect, on_wifi_disconnect - What to do when WiFi does like this
# on_wifi_connect_fail - Called when cannot connect to desired network


# def init():
#     """Happens once when booting. Don't count on WiFi/MQTT connections"""
#     print("Initializing logix!")
#
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
