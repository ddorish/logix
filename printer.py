import utime


class Print:
    activity = {}
    timeout = 5000
    NORMAL = 0
    level = NORMAL

    def __init__(self, message, level=NORMAL):
        if level < Print.level:
            return
        if message in self.activity:
            time_since = utime.ticks_diff(utime.ticks_ms(), self.activity.get(message, 0))
            if time_since > self.timeout:
                self.print(message)
        self.cleanup()

    def print(self, message):
        print(message)
        self.activity[message] = utime.ticks_ms()

    def cleanup(self):
        now = utime.ticks_ms()
        for k in self.activity.keys():
            if utime.ticks_diff(now, self.activity.get(k, 0)) > self.timeout:
                self.activity.pop(k)

    @staticmethod
    def set_level(new_level):
        Print.level = new_level

