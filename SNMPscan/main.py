from time import sleep
import datetime

from network_lamp_app.functions import start_get_printer_info, ip_scan_diapason


def run():
    print("Big scan")
    ip_scan_diapason(ip_diapason="172.16.0.0/20")

    while True:
        hour = datetime.datetime.today().hour
        minute = datetime.datetime.today().minute
        start_get_printer_info()

        if hour in [4, 6, 7, 11, 12, 18, 19, 22, 23] and minute >= 50:
            print("Big scan")
            ip_scan_diapason(ip_diapason="172.16.0.0/20")

        sleep(600)


if __name__ == "__main__":
    run()