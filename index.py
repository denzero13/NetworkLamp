from dash import html, dcc
import dash_bootstrap_components as dbc
from dash.dependencies import Input, Output
import pandas as pd


from app import app
from apps import printer_level, devises_list, printer_list


app.title = "Network Lamp"

app.layout = html.Div([
    dcc.Link(dbc.Button("Printer Level",  color="secondary", className="me-1"), href='/level'),
    dcc.Link(dbc.Button("Printers",  color="secondary", className="me-1"), href='/printers'),
    dcc.Link(dbc.Button("Devises",  color="primary", className="me-1"), href='/devises'),
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
    else:
        return '404'


if __name__ == '__main__':
    app.run_server(debug=True)