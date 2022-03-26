import json
import datetime
import csv
import concurrent.futures


import pandas as pd
from pysnmp.entity.rfc3413.oneliner import cmdgen
from pysnmp.hlapi import getCmd, SnmpEngine, CommunityData, UdpTransportTarget, ContextData, ObjectType, ObjectIdentity
import ipaddress
import socket
import getmac
from mac_vendor_lookup import MacLookup

from network_lamp_app.Classes import PrinterModel
from network_lamp_app.config import tmp, devices_mongo, history_mongo, tmp_mongo, toner_replace_inventory_mongo


def snmp_cmd_gen(oid, ip_address, community="public", port=161):
    """
    The function takes the printer IDs and returns the value using the oid
    """
    get_printer_data = cmdgen.CommandGenerator()
    errorIndication, errorStatus, errorIndex, varBinds = get_printer_data.getCmd(
        cmdgen.CommunityData(community, mpModel=0),
        cmdgen.UdpTransportTarget((ip_address, port)),
        oid)

    if errorIndication is None:
        return varBinds[0][1]


def snmp_cmd_get(ip_address, community="public", port=161):
    """
    The function takes the address and checks
    it for the SNMP v1 v2 protocol whit standard settings
    """
    try:
        iterator = getCmd(SnmpEngine(),
                          CommunityData(community, mpModel=0), UdpTransportTarget((ip_address, port)),
                          ContextData(), ObjectType(ObjectIdentity('SNMPv2-MIB', 'sysDescr', 0)))

        errorIndication, errorStatus, errorIndex, varBinds = next(iterator)
    except:
        return None

    if errorIndication:  # SNMP engine errors
        return None
    else:
        if errorStatus:  # SNMP agent errors
            # status = str('%s at %s' % (errorStatus.prettyPrint(), varBinds[int(errorIndex) - 1] if errorIndex else '?'))
            return None
        else:
            for varBind in varBinds:  # SNMP response contents
                var = str(' = '.join([x.prettyPrint() for x in varBind]))
                return var


def ip_scan_diapason(ip_diapason="172.16.0.0/22"):
    """
    The function scans the specified range of addresses and create
    json with the list of devices in which the SNMP protocol is enabled
    """
    print("Start scan local network")
    ip_diapason = ipaddress.IPv4Network(ip_diapason)

    with concurrent.futures.ThreadPoolExecutor(max_workers=60) as processing:
        data = processing.map(device_snmp_filter, ip_diapason)

    for device in data:
        status = devices_mongo.find_one({"ip_host": device["ip_host"]})

        if device["mac-address"]:
            device["timestamp"] = datetime.datetime.today().strftime("%Y-%m-%d %H:%M:%S")

        if status:
            devices_mongo.update_one({"ip_host": device["ip_host"]}, {"$set": device})
        else:
            devices_mongo.insert_one(device)


def device_snmp_filter(ip_address):
    """
    Accepts the address and filters all devices if there is a protocol SNMP
    """
    ip_dict = dict()
    ip = str(ip_address)

    ip_dict["ip_host"] = ip
    ip_dict["snmp"] = snmp_cmd_get(ip)
    ip_dict["mac-address"] = getmac.get_mac_address(ip=ip, network_request=True)

    if ip_dict["mac-address"] == "00:00:00:00:00:00":
        ip_dict["mac-address"] = None

    if ip_dict["mac-address"]:
        try:
            ip_dict["company"] = MacLookup().lookup(str(ip_dict["mac-address"]))
        except KeyError:
            ip_dict["company"] = "NotFound"
            print("KeyError: ", ip_dict)
    else:
        ip_dict["company"] = "none"

    try:
        ip_dict["hostname"] = socket.gethostbyaddr(ip)[0]
    except socket.herror:
        ip_dict["hostname"] = "none"
    print(ip_dict)
    return ip_dict


def start_get_printer_info():
    """
    Start get information about printers status
    """
    fieldnames = list(PrinterModel("").KYOCERA.keys())
    fieldnames.append("time")
    file = open(tmp, "w", newline='')
    writer = csv.DictWriter(file, fieldnames=fieldnames)
    writer.writeheader()
    file.close()

    print("Start Level Scan")
    multi_scan_run()
    data = pd.read_csv(tmp)
    tmp_json = json.loads(data.to_json(orient="records"))
    tmp_mongo.drop()

    for j in tmp_json:
        history_mongo.insert_one(j)
        tmp_mongo.insert_one(j)

    query = {"CartridgeMaxCapacity": None, "TonerModel": None, "TonerLevel": None, "time": None}
    history_mongo.delete_many(query)
    tmp_mongo.delete_many(query)
    replace_inventory()
    print("Done Level Scan")


def multi_scan_run():
    """
    Start OID scan with multiprocess
    """
    devices = list()
    for dev in list(devices_mongo.find()):
        if dev["snmp"] and dev["mac-address"] and dev["company"] != "NotFound":
            oid_list = PrinterModel(dev).printer_model()
            if oid_list:
                devices.append([dev, oid_list])

    with concurrent.futures.ThreadPoolExecutor(max_workers=60) as processing:
        data = processing.map(oid_scan, devices)


def oid_scan(device):
    oid_list = device[1]
    device = device[0]
    ip_device = device["ip_host"]

    toner_type = snmp_cmd_gen(oid=oid_list["TonerType"], ip_address=ip_device)
    toner_type_color = snmp_cmd_gen(oid=str(oid_list["TonerType"])[:-1]+str(2), ip_address=ip_device)

    with open(tmp, "a", newline="") as tmp_file:
        fieldnames = list(oid_list.keys())
        fieldnames.append("time")
        tmp_writer = csv.DictWriter(tmp_file, fieldnames=fieldnames, escapechar='\\')
        if "OctetString" in str(type(toner_type_color)) and str(toner_type_color) in ["cyan", "magenta", "yellow"]:
            for n in range(1, 5):
                oid_list["TonerModel"] = str(oid_list["TonerModel"])[:-1]+str(n)
                oid_list["TonerType"] = str(oid_list["TonerType"])[:-1] + str(n)
                oid_list["TonerLevel"] = str(oid_list["TonerLevel"])[:-1] + str(n)
                oid_list["CartridgeMaxCapacity"] = str(oid_list["CartridgeMaxCapacity"])[:-1] + str(n)
                scan_result = indicators_oid(ip_device, oid_list)
                tmp_writer.writerow(scan_result)
                print(scan_result)

        elif "NoneType" in str(type(toner_type)) or str(toner_type) == "None":
            pass

        else:
            scan_result = indicators_oid(ip_device, oid_list)
            print(scan_result)
            tmp_writer.writerow(scan_result)


def indicators_oid(ip_address, oid_list):
    """
    Get information in OID SNMP system with loop
    """
    printer_info = {}
    for oid_key in oid_list.keys():
        oid = oid_list[oid_key]
        if oid == "1.3.6.1.4.1.2699.1.2.1.3.1.1.4.1.3":
            printer_info["ip_host"] = ip_address
        else:
            printer_info[oid_key] = snmp_cmd_gen(oid=oid, ip_address=ip_address)

    printer_info["time"] = datetime.datetime.today().strftime("%Y-%m-%d %H:%M:%S")
    return printer_info


def replace_inventory():
    printers = list(tmp_mongo.find({}, {"location", "TonerModel"}))
    for pr in printers:
        print(pr)
        toner_level_info = list(history_mongo.find({"location": pr.get("location"), "TonerModel": pr.get("TonerModel")},
                                                   {"location", "model", "TonerModel", "TonerLevel",
                                                    "CartridgeMaxCapacity", "time"}).sort("time", -1))
        try:
            toner_level_now = toner_level_info[0].get("TonerLevel")
            toner_level_back = toner_level_info[1].get("TonerLevel")
            toner_level_max = toner_level_info[0].get("CartridgeMaxCapacity")*0.85

            if toner_level_max < toner_level_now > toner_level_back:
                toner_level_info[1]["amount"] = -1
                toner_level_info[1]["time"] = toner_level_info[0]["time"]
                toner_replace_inventory_mongo.insert_one(toner_level_info[1])
                print(toner_level_info[:2])
                print("Toner replace")
        except (IndexError, TypeError) as Er:
            print(Er, "\n", toner_level_info)


