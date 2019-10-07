import api
from printer import Print

##################################################################
# Default funcs for all events. Can be overriden by user if wanted
##################################################################
g_loop_Print = True


def loop(curr_time_ms):
    global g_loop_Print
    g_loop_Print = g_loop_Print and Print("Loop is missing")
setup = lambda: Print("setup is missing")
on_mqtt = lambda topic, payload: Print("mqtt arrived on %s: %s" % (topic, payload))
on_wifi_connect = lambda network_name: Print("wifi connected to %s" % network_name)
on_wifi_connect_fail = lambda network_name: Print("wifi connect fail to %s" % network_name)
# on_wifi_disconnect = lambda network_name: Print("wifi disconnect from %s" % network_name)
on_mqtt_connect = lambda: Print("mqtt connected")
# on_mqtt_connect_fail = lambda: Print("mqtt connect failed")
on_mqtt_disconnect = lambda: Print("mqtt disconnected")


def send_report():
    """Send some data about the machine... IP address. Anything else ??"""
    app = api.app
    if app.mqtt_connected():
        report_topic = app.conf.get('device_report_topic', None)
        if report_topic is not None:
            app.publish(report_topic, 'Network: %s' % str(app._station.ifconfig()))
