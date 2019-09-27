import api

##################################################################
# Default funcs for all events. Can be overriden by user if wanted
##################################################################
g_loop_print = True


def loop(curr_time_ms):
    global g_loop_print
    g_loop_print = g_loop_print and print("Loop is missing")
setup = lambda: print("setup is missing")
on_mqtt = lambda topic, payload: print("mqtt arrived on %s: %s" % (topic, payload))
on_wifi_connect = lambda network_name: print("wifi connected to %s" % network_name)
on_wifi_connect_fail = lambda network_name: print("wifi connect fail to %s" % network_name)
on_wifi_disconnect = lambda network_name: print("wifi disconnect from %s" % network_name)
on_mqtt_connect = lambda: print("mqtt connected")
on_mqtt_connect_fail = lambda: print("mqtt connect failed")
on_mqtt_disconnect = lambda: print("mqtt disconnected")


def send_report():
    """Send some data about the machine... IP address. Anything else ??"""
    app = api.app
    if app.mqtt_connected():
        report_topic = app.conf.get('device_report_topic', None)
        if report_topic is not None:
            app.publish(report_topic, 'Network: %s' % str(app._station.ifconfig()))
