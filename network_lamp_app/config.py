import os

from pymongo import MongoClient

# db.createUser({user: 'admindb', pwd: 'qwertyrud13', roles: [{role: 'readWrite', db: 'network_lamp_db'}]})
# mongo_connection = MongoClient('mongodb://' + os.environ['MONGODB_USERNAME'] + ':' + os.environ['MONGODB_PASSWORD'] + '@' + os.environ['MONGODB_HOSTNAME'] + ':27017/' + os.environ['MONGODB_DATABASE'])
mongo_connection = MongoClient(host="localhost", port=27017)
mongo_db = mongo_connection.network_lamp

devices_mongo = mongo_db.devices
history_mongo = mongo_db.history
tmp_mongo = mongo_db.tmp
toner_replace_inventory_mongo = mongo_db.toner_replace_inventory
barcode_base_mongo = mongo_db.toner_barcode_base


tmp = "network_lamp_app/tmp.csv"
visual_for_terminal = "network_lamp_app/data/visual.csv"

# Style for Dash Table
style_cell = {"textAlign": "left", "color": "white",
              "font-family": "Lora", "font-size": "90%"}
style_data = {"backgroundColor": "rgb(50, 50, 50)",
              'border': "1px solid grey",
              "whiteSpace": "normal",
              "height": "auto",
              "minWidth": "160px", "width": "170px", "maxWidth": "180px",
              "lineHeight": "65px"}