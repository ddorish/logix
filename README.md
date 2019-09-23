# logix
Highlights:
===========
* Home automation u-python environment for MQTT microcontrollers (e.g. ESP8266 + home-assistant)
* A disctict feature here is what-to-do-when-mqtt-server-is-gone (e.g. turn off irrigation)

Details:
===

The devices are meant to connect to a central MQTT server, and toggle things in your house.
This project was written with home-assistance in mind, but would probably match other platforms as well.

Unlike other projects, you do need to know some python, but you can also perform more complicated things.


As a user, you should edit 3 files:
- secrets.conf - Where you put your WiFi/MQTT passwords, etc.
- config.conf - Where you decide to what topics this device will subscribe
- logix.py - Where you write the (usually) few lines to perform what you need.

Check out the example of
----
2 flood lights (call "garden lights") on a device, listening on /garden/light/
When a command is given to turn the lights on, one light turns on (randomally selecting), and after a predefined delay, the other responses too.
Works as a "non-optimistic" switch, i.e. the device sends acknowledgements for given commands.
If disconnected from WiFi or MQTT, after 2 minutes, the lights turn out (in the same fashion)


Version 1.0:
===
Supports numerical MQTT-variables (float and int), and digital-outputs
