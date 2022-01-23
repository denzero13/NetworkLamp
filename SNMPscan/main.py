from functions import ip_scan_diapason, start_get_printer_info
from config import ip_network_diapason
import time


t = time.time()

if __name__ == '__main__':
    print("Start first scan")
    ip_scan_diapason(ip_diapason=ip_network_diapason)
    start_get_printer_info(time=t)
    print("End first start scan")
    order_run = 0
    while True:
        if time.time() - t > 1000:
            if order_run == 4:
                print("Devises scan")
                ip_scan_diapason(ip_diapason=ip_network_diapason)
                print("Devises scan done")
                n = 0
            print("Printers scan")
            start_get_printer_info(t)
            print("Printers scan done")
            order_run += 1
            t = time.time()