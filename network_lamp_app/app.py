import datetime

import dash
import dash_bootstrap_components as dbc
from dash.dependencies import Input, Output, State
from flask import Flask
import pandas as pd

from .config import devices_mongo, tmp_mongo, toner_replace_inventory_mongo, barcode_base_mongo


external_stylesheets = [dbc.themes.CYBORG]
app = dash.Dash(__name__, external_stylesheets=external_stylesheets, suppress_callback_exceptions=True)


operators = [["ge ", ">="],
             ["le ", "<="],
             ["lt ", "<"],
             ["gt ", ">"],
             ["ne ", "!="],
             ["eq ", "="],
             ["contains "],
             ["datestartswith "]]


def split_filter_part(filter_part):
    for operator_type in operators:
        for operator in operator_type:
            if operator in filter_part:
                name_part, value_part = filter_part.split(operator, 1)
                name = name_part[name_part.find("{") + 1: name_part.rfind("}")]

                value_part = value_part.strip()
                v0 = value_part[0]
                if v0 == value_part[-1] and v0 in ("'", '"', "`"):
                    value = value_part[1: -1].replace("\\" + v0, v0)
                else:
                    try:
                        value = float(value_part)
                    except ValueError:
                        value = value_part

                # word operators need spaces after them in the filter string,
                # but we don"t want these later
                return name, operator_type[0].strip(), value

    return [None] * 3


def filter_df(df, filter_query):
    filtering_expressions = filter_query.split(" && ")

    for filter_part in filtering_expressions:
        col_name, operator, filter_query = split_filter_part(filter_part)

        filter_query = str(filter_query)

        if operator in ("eq", "ne", "lt", "le", "gt", "ge"):
            # these operators match pandas series operator method names
            df = df.loc[getattr(df[col_name], operator)(filter_query, case=False)]

        elif operator == "contains":
            df = df.loc[df[col_name].str.contains(filter_query, na=False, case=False)]

        elif operator == "datestartswith":
            # this is a simplification of the front-end filtering logic,
            # only works with complete fields in standard format
            df = df.loc[df[col_name].str.startswith(filter_query, na=False, case=False)]
    return df.to_dict("records")


# Devices list callback
def devices_list_mongo_df():
    return pd.DataFrame(list(devices_mongo.find({}, {'_id': False})))


@app.callback(
    Output("table-filtering-be-device", "data"),
    Input("table-filtering-be-device", "filter_query"))
def update_table(filter_value):

    return filter_df(devices_list_mongo_df(), filter_value)


# Printers list mongo data request and callback
def printers_list_mongo_df():
    query = {"_id": False, "location": True, "model": True, "InventoryNumber": True,
             "TonerModel": True, "TonerType": True, "ip_host": True}
    return pd.DataFrame(list(tmp_mongo.find({}, query)))


@app.callback(
    Output("table-filtering", "data"),
    Input("table-filtering", "filter_query"))
def update_table(filter_value):

    return filter_df(printers_list_mongo_df(), filter_value)


# Toner balance mongo data request and callback
def toner_balance_df():
    pipeline = [
        {"$unwind": "$TonerModel"},
        {"$group": {"_id": "$TonerModel", "amount": {"$sum": "$amount"}}},
        {"$sort": {"amount": 1}}
    ]
    return pd.DataFrame(list(toner_replace_inventory_mongo.aggregate(pipeline)))


@app.callback(
    Output("balance-table", "data"),
    Input("balance-table", "filter_query"))
def update_table(filter_value):

   return filter_df(toner_balance_df(), filter_value)


# Inventory section
def inventory_mongo_df():
    query = {"_id": False, "location": True, "model": True,
             "TonerModel": True, "amount": True, "time": True}
    df = pd.DataFrame(list(toner_replace_inventory_mongo.find({}, query).sort("time", -1)))
    return df


@app.callback(
    Output(component_id="inventory-table", component_property="data"),
    Output("output_barcode", "children"),
    Output(component_id="input_barcode", component_property="value"),
    [Input("input_barcode", "n_submit"), Input("barcode-count", "n_submit"),
     Input("inventory-table", "filter_query"), Input("inventory-table", "data_previous")],
    [State("operation-inline-input", "value"), State("input_barcode", "value"), State("barcode-count", "value"), State("inventory-table", "data"), State("inventory-table", "data_previous")])
def output_text(br_enter, count_enter, filter_query, edit_table, operation, barcode, count, table, previous):

    if br_enter and barcode or count_enter:
        try:
            if count is None:
                count = 1

            count = int(operation + str(count))
            toner_model = barcode_base_mongo.find({"barcode": barcode})
            toner_model = toner_model[0].get("TonerModel")
            print("R ", barcode, "->", toner_model)
            if toner_model:
                toner_replace_inventory_mongo.insert_one({"location": "SKLAD", "TonerModel": toner_model, "amount": count,
                                                          "time": datetime.datetime.today().strftime("%Y-%m-%d %H:%M:%S")})
            if operation == "+":
                operation = "Додано Тонер : "
            elif operation == "-":
                operation = "Списано Тонер : "

            barcode = operation + toner_model +" | "+ "Штрихкод : " + barcode
        except IndexError:
            barcode = "NotFound"
        data = inventory_mongo_df().to_dict("records")

    elif len(filter_query) != 0:
        data = inventory_mongo_df().to_dict("records")
        data = filter_df(pd.DataFrame(data), filter_query)

    elif edit_table:
        for row in previous:
            if row not in table:
                delete_row = row
                toner_replace_inventory_mongo.delete_one(row)

        data = inventory_mongo_df().to_dict("records")
        barcode = f"Видалено {delete_row}"

    else:
        data = inventory_mongo_df().to_dict("records")
        barcode = "Очікування"

    return data, barcode, ""


# Barcode base
def barcode_mongo_df():
    query = {"_id": False}
    df = pd.DataFrame(list(barcode_base_mongo.find({}, query).sort("time", -1)))

    return df


@app.callback(
    Output(component_id="barcode-table", component_property="data"),
    Output("output-barcode-base", "children"),
    Output(component_id="barcode-to-base", component_property="value"),
    [Input("barcode-to-base", "n_submit"), Input("toner-model-name", "n_submit"),  Input("barcode-table", "filter_query")],
    [State("operation-barcode-input", "value"), State("toner-model-name", "value"), State("barcode-to-base", "value")])
def output_text(br_enter, model_enter, filter_query, operation, model, barcode):
    if br_enter or model_enter and len(barcode) > 2:
        try:
            status_find = barcode_base_mongo.find_one({"barcode": str(barcode)}, {"_id": False})
            print(status_find)

            if operation == "+" and model:

                if status_find:
                    operation = "in use"
                else:
                    barcode_base_mongo.insert_one({"TonerModel": model, "barcode": barcode,
                                                   "time": datetime.datetime.today().strftime("%Y-%m-%d %H:%M:%S")})
            elif operation == "-" and status_find:
                barcode_base_mongo.delete_one({"barcode": barcode})

            if operation == "+":
                barcode = "Створено Тонер : " + model +" | "+ "Штрихкод : " + barcode
            elif operation == "-":
                barcode = "Видалено Тонер : " + model +" | "+ "Штрихкод : " + barcode
            elif operation == "in use":
                barcode = "Штрихкод вже використовується : " + str(status_find)
        except IndexError:
            barcode = "NotFound"
        data = barcode_mongo_df().to_dict("records")

    elif model or barcode:
        barcode = "Потрібно заповнити всі поля"
        data = barcode_mongo_df().to_dict("records")

    elif len(filter_query) != 0:
        data = barcode_mongo_df().to_dict("records")
        data = filter_df(pd.DataFrame(data), filter_query)

    else:
        data = barcode_mongo_df().to_dict("records")
        barcode = "Очікування"

    return data, barcode, ""
