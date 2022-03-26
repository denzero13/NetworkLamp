from dash import html, dcc
import dash_bootstrap_components as dbc
from dash.dependencies import Input, Output

from .app import app
from .apps import printer_level, devises_list, printer_list, toner_replace_inventory_list, toner_balance, barcode_base

app.title = "Network Lamp"

app.layout = html.Div(style={'textAlign': 'center', 'backgroundColor': 'white', 'color': 'black', 'border': '1px solid black'},
                      children=[
                        dcc.Link(dbc.Button("Printer Level", outline=True,  color="primary", className="me-1"), href='/level'),
                        dcc.Link(dbc.Button("Inventory", outline=True, color="primary", className="me-1"), href='/inventory'),
                        dcc.Link(dbc.Button("Toner Balance", outline=True, color="primary", className="me-1"), href='/balance'),
                        dcc.Link(dbc.Button("Barcode Base", outline=True, color="primary", className="me-1"), href='/barcode'),
                        dcc.Link(dbc.Button("Printers", outline=True, color="primary", className="me-1"), href='/printers'),
                        dcc.Link(dbc.Button("Devises", outline=True, color="primary", className="me-1"), href='/devises'),
                        dcc.Location(id='url', refresh=True),
                        html.Div(id='page-content')
                      ])


@app.callback(Output('page-content', 'children'),
              Input('url', 'pathname'))
def display_page(pathname):
    if pathname == '/level' or pathname == '/':
        return printer_level.layout()
    if pathname == '/devises':
        return devises_list.layout()
    if pathname == '/printers':
        return printer_list.layout()
    if pathname == '/inventory':
        return toner_replace_inventory_list.layout()
    if pathname == '/balance':
        return toner_balance.layout()
    if pathname == '/barcode':
        return barcode_base.layout()
    else:
        return '404'
