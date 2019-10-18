if 1:
    import umqttsimple
    import api
    # Set all default callbacks:
    import utils  # Get the things under the hood imported

    import defaults

    utils.App()  # Fire up the application

    # Load user data, and override the callbacks
    try:
        import logix
    except Exception as e:
        err = e
        status_msg = "Error in logix.py: %s: %s" % (type(err), str(err))
        print(status_msg)  # Will only be seen if connected via serial
        # Make logix an empty object:

        def logix():
            print("It didn't work:\n%s" % status_msg)
            pass

    print("Inserting callbacks...")
    for f in dir(defaults):
        if f.startswith('__'):
            continue
        if hasattr(logix, f):
            print("Found user defined function %s" % f)
            setattr(api.cb, f, getattr(logix, f))
        else:
            print("Using default function for %s" % f)
            setattr(api.cb, f, getattr(defaults, f))

    # Now everything is up and connected. Run user's setup function:
    api.cb.setup()

    # Send IP every 2 minutes:
    from handlers import PeriodicHandler
    meta_sender = PeriodicHandler(api.cb.send_report)



    def run():
        api.app.run()


    def stop():
        api.app.stop()


    def main():
        run()


    if __name__ == '__main__':
        run_on_boot_str = api.app.conf.get('run_on_boot', '1')
        if run_on_boot_str != '0':
            print("Auto-running...")
            main()
        print("Main is done.")

