from dash import dash_table, html, dcc
from dash.dependencies import Input, Output
import pandas as pd

from config import tmp_mongo
from app import app


def layout():
    df = pd.DataFrame(list(tmp_mongo.find({}, {"location", "model", "TonerModel", "ip_host", "InventoryNumber"})))
    data = []
    for j in df.index:
        data_dict = dict()
        for i in df.columns:
            data_dict[str(i)] = str(df[i][j])
        data.append(data_dict)

    colors = {"background": "#2b2b2b",
              "text": "#8ab4f8",
              "font": "Lora"}

    return html.Div(style={"backgroundColor": colors["background"]},
                    children=[
            html.H3(
                children="Printers",
                style={"textAlign": "center", "color": colors["text"], "font-family": "Lora"}),

            dash_table.DataTable(
                    id="table-filtering",
                    style_header={'backgroundColor': 'rgb(30, 30, 30)', 'color': 'white', 'border': '1px solid black'},
                    columns=[{"name": str(i), "id": str(i)} for i in df.columns[1:]],
                    data=data,
                    export_format='xlsx',
                    style_as_list_view=True,
                    filter_action="custom",
                    sort_action="native",
                    sort_mode='multi',
                    filter_query=str(),
                    style_cell={"textAlign": "left",  'color': 'white',
                                "font-family": "Didact Gothic", "font-size": "140%"},
                    style_data={'backgroundColor': 'rgb(50, 50, 50)',
                                'border': '1px solid grey',
                                "whiteSpace": "normal",
                                "height": "auto",
                                "minWidth": "180px", "width": "180px", "maxWidth": "180px",
                                "lineHeight": "65px"},


                    style_cell_conditional=[{'if': {'column_id': c},
                                             'textAlign': 'center'}
                                            for c in ["ip_host"]]),
                    ])


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


@app.callback(
    Output("table-filtering", "data"),
    Input("table-filtering", "filter_query"))
def update_table(filter_value):
    filtering_expressions = filter_value.split(" && ")
    df = pd.DataFrame(list(tmp_mongo.find()))
    data = []
    for j in df.index:
        data_dict = dict()
        for i in df.columns[1:]:
            data_dict[str(i)] = str(df[i][j])
        data.append(data_dict)
    dff = pd.DataFrame(data)
    for filter_part in filtering_expressions:
        col_name, operator, filter_value = split_filter_part(filter_part)
        filter_value = str(filter_value)
        if operator in ("eq", "ne", "lt", "le", "gt", "ge"):
            # these operators match pandas series operator method names
            dff = dff.loc[getattr(dff[col_name], operator)(filter_value)]

        elif operator == "isin":
            dff = dff[dff[col_name].isin([filter_value])]

        elif operator == "contains":
            dff = dff.loc[dff[col_name].str.contains(filter_value, na=False)]

        elif operator == "datestartswith":
            # this is a simplification of the front-end filtering logic,
            # only works with complete fields in standard format
            dff = dff.loc[dff[col_name].str.startswith(filter_value, na=False)]
    return dff.to_dict("records")