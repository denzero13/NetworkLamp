from dash import dash_table, html
import dash_bootstrap_components as dbc




def layout():

    colors = {"background": "#2b2b2b",
              "text": "#8ab4f8",
              "font": "Lora"}

    return html.Div(style={"backgroundColor": colors["background"], "color": colors["text"]},
                    children=[
            dbc.Label("Settings NetworkLamp"),
            dbc.Checklist(
                options=[
                    {"label": "Printer Level Scan", "value": 1},
                    {"label": "LAN devises scan", "value": 2},
                ],
                # value=True,
                id="conf-inline-input",
                inline=True,
                switch=True,
            )
])