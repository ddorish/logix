# This is a dummy file to bypass the import problem
# Problem: utils.py imports logix.py
# We want to accss 'app', which is defined in utils.py from within logix

import array
from machine import unique_id  # Timer

app = None


class cb:
    # Used to store all the callbacks (as defined in defaults.py)
    pass


def as_uint32(x):
    return array.array('I', [x])[0]


def ifconfig():
    return app.station().ifconfig()


def hexalify(num):
    text = '0123456789ABCDEF'
    res = ''
    while num > 0:
        res = res + text[num % 16]
        num = int(num / 16)
    return res


def uid():
    return ''.join([hexalify(x) for x in unique_id()])


class PinOut:
    """https://forum.arduino.cc/index.php?topic=485831.0"""
    LED_BUILTIN = 16
    BUILTIN_LED = 16
    D0   = 16
    D1   = 5
    D2   = 4
    D3   = 0
    D4   = 2
    D5   = 14
    D6   = 12
    D7   = 13
    D8   = 15
    D9   = 3
    D10  = 1

    @staticmethod
    def resolve(pin_name):
        return getattr(PinOut, pin_name, None)
