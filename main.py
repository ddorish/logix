if 1:
    import utils  # This fires up everything more or less...
    import api


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

