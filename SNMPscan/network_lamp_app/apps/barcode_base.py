from dash import dash_table, html
import dash_bootstrap_components as dbc

from network_lamp_app.app import barcode_mongo_df
from network_lamp_app.config import style_cell, style_data


def layout():
    df = barcode_mongo_df()
    data = df.to_dict("records")

    colors = {"background": "#2b2b2b",
              "text": "#8ab4f8",
              "font": "Lora"}

    return html.Div(style={"backgroundColor": colors["background"]}, children=[
        html.Div([
            dbc.Row(dbc.Col(html.H3("База Штрихкодів"),
                            width={"size": 6, "offset": 3})),
            dbc.Row(dbc.Col(html.Div([
                dbc.Label("Тип Операції"),
                dbc.RadioItems(
                    options=[
                        {"label": "Створення", "value": "+"},
                        {"label": "Видалення", "value": "-"},
                    ],
                    value="+",
                    id="operation-barcode-input",
                    inline=True,
                ),
                dbc.Input(id="toner-model-name", type="text"),
                html.Br(),
                dbc.Input(id="barcode-to-base", type="text"),

                html.P(id="output-barcode-base", style={"color": colors["text"]}),
            ]),
                width={"size": 6, "offset": 3}))]),

        dash_table.DataTable(
            id="barcode-table",
            style_header={"backgroundColor": "rgb(30, 30, 30)", "color": "white", "border": "1px solid black"},
            columns=[{"name": str(i), "id": str(i)} for i in df.columns],
            data=data,
            export_format="xlsx",
            style_as_list_view=True,
            filter_action="custom",
            sort_action="native",
            sort_mode="multi",
            filter_query=str(),
            style_cell=style_cell,
            style_data=style_data,

            style_cell_conditional=[{"if": {"column_id": c},
                                     "textAlign": "center"}
                                    for c in ["_id"]]),
    ])