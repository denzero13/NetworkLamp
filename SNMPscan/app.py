import dash
from dash import dcc, html
import dash_bootstrap_components as dbc
import plotly.express as px
import pandas as pd
import numpy as np
from functions import data_visual_stack_bar, tmp


df = pd.read_csv(tmp)
external_stylesheets = ["https://codepen.io/chriddyp/pen/bWLwgP.css"]
app = dash.Dash(__name__, external_stylesheets=external_stylesheets)

colors = {"background": "#111111",
          "text": "#7FDBFF"}

df["TonerType"] = df["TonerType"].replace(np.nan, "black")
df["Level"] = [int(float(df["TonerLevel"][i]) * 100 / float(df["CartridgeMaxCapacity"][i])) for i in range(len(df))]
df["Used"] = [100 - df["Level"][i] for i in range(len(df))]
df["Full Name"] = [str(df["location"][i])+": "+str(df["TonerModel"][i])+" " for i in range(len(df))]

black_toner_data = df[["Full Name", "TonerType", "Level", "Used"]].loc[df["TonerType"] == "black"].sort_values("Level")
cyan_toner_data = df[["Full Name", "TonerType", "Level", "Used"]].loc[df["TonerType"] == "cyan"].sort_values("Level")
magenta_toner_data = df[["Full Name", "TonerType", "Level", "Used"]].loc[df["TonerType"] == "magenta"].sort_values("Level")
yellow_toner_data = df[["Full Name", "TonerType", "Level", "Used"]].loc[df["TonerType"] == "yellow"].sort_values("Level")

black_toner_data = data_visual_stack_bar(black_toner_data, "black")
cyan_toner_data = data_visual_stack_bar(cyan_toner_data, "cyan")
magenta_toner_data = data_visual_stack_bar(magenta_toner_data, "magenta")
yellow_toner_data = data_visual_stack_bar(yellow_toner_data, "yellow")

app.layout = html.Div(style={"backgroundColor": colors["background"]}, children=[
        html.H1(
            children="Toner Level RUD",
            style={"textAlign": "center", "color": colors["text"]}),

        html.H6(children="Author Denys Pavliuk",
                style={"textAlign": "center", "color": colors["text"]}),

        html.Div(children=[
            dcc.Graph(
                id="graph-black",
                figure=black_toner_data,
                className='seven columns'),
            dcc.Graph(
                id="graph-magenta",
                figure=magenta_toner_data,
                className='five columns'),
            dcc.Graph(
                id="graph-yellow",
                figure=yellow_toner_data,
                className='five columns'),
            dcc.Graph(
                id="graph-cyan",
                figure=cyan_toner_data,
                className='five columns')],
            className='double-graph',
            style={'width': '100%', 'display': 'inline-block'})
    ])

app.run_server(debug=True)


