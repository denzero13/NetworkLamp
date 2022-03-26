from dash import dash_table, html

from network_lamp_app.app import printers_list_mongo_df
from network_lamp_app.config import style_cell, style_data


def layout():
    df = printers_list_mongo_df()
    data = df.to_dict("records")

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
                    columns=[{"name": str(i), "id": str(i)} for i in df.columns],
                    data=data,
                    export_format='xlsx',
                    style_as_list_view=True,
                    filter_action="custom",
                    sort_action="native",
                    sort_mode='multi',
                    filter_query=str(),
                    style_cell=style_cell,
                    style_data=style_data,
                    style_cell_conditional=[{'if': {'column_id': c},
                                             'textAlign': 'center'}
                                            for c in ["ip_host"]]),
                    ])