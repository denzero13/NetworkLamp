from dash import dash_table, html
import dash_bootstrap_components as dbc

from network_lamp_app.app import inventory_mongo_df
from network_lamp_app.config import style_cell, style_data


def layout():
    df = inventory_mongo_df()
    data = df.to_dict("records")

    colors = {"background": "#2b2b2b",
              "text": "#8ab4f8",
              "font": "Lora"}

    return html.Div(style={"backgroundColor": colors["background"], "color": colors["text"]}, children=[
        html.Div([
            dbc.Row(dbc.Col(html.H3("Інвентаризація"),
                            width={'size': 6, 'offset': 3})),
            dbc.Row(dbc.Col(html.Div([
                dbc.Label("Тип Операції"),
                dbc.RadioItems(
                    options=[
                        {"label": "Прихід", "value": "+"},
                        {"label": "Списання", "value": "-"},
                    ],
                    value="+",
                    id="operation-inline-input",
                    inline=True,
                ),
                dbc.Input(id='input_barcode', type='text'),
                html.Br(),
                dbc.Input(type="number", min=0, max=50, step=1, id="barcode-count"),


                html.P(id="output_barcode", style={"color": colors["text"]}),
            ]),
                width={'size': 6, 'offset': 3}))]),

        dash_table.DataTable(
            id="inventory-table",
            style_header={'backgroundColor': 'rgb(30, 30, 30)', 'color': 'white', 'border': '1px solid black'},
            columns=[{"name": str(i), "id": str(i)} for i in df.columns],
            data=data,
            export_format='xlsx',
            style_as_list_view=True,
            row_deletable=True,
            filter_action="custom",
            sort_action="native",
            sort_mode='multi',
            filter_query=str(),
            style_cell=style_cell,
            style_data=style_data,
            style_cell_conditional=[{'if': {'column_id': c},
                                     'textAlign': 'center'}
                                    for c in ["ip_host"]])
    ])