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
        for f in dir(defaults):
            if hasattr(logix, f):
                setattr(api.cb, f, getattr(logix, f))
            else:
                setattr(api.cb, f, getattr(defaults, f))

        # Now everything is up and connected. Run user's setup function:
        api.cb.setup()

    except Exception as e:
        err = e
        status_msg = "Error in logix.py: %s: %s" % (type(err), str(err))
        print(status_msg)  # Will only be seen if connected via serial


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

