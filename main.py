if 1:
    import utils  # This fires up everything more or less...

    # Generate everything...
    utils.App()

    # Load user data
    try:
        from logix import *
    except Exception as e:
        err = e
        status_msg = "Error in logix.py: %s: %s" % (type(err), str(err))
        print(status_msg)  # Will only be seen if connected via serial

    import api

    try:
        import logix as logix_module
        api.logix = logix_module
    except:
        # Nahh. Forget.
        pass


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

