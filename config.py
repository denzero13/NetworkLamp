from pymongo import MongoClient


mongo_connection = MongoClient(host="localhost", port=27017)
mongo_db = mongo_connection.network_lamp

devices_mongo = mongo_db.devices
history_mongo = mongo_db.history
tmp_mongo = mongo_db.tmp
toner_replace_inventory = mongo_db.toner_replace_inventory


devices = "~/data/devices.json"
tmp = "../data/tmp.csv"
log = "../data/log.csv"
ip_network_diapason = "172.16.0.0/22"
visual_for_terminal = "../data/visual.csv"