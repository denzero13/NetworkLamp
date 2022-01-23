import dash
from dash import dcc, html
import plotly.express as px
import plotly.graph_objects as go
import pandas as pd
import numpy as np

from config import tmp_mongo
from app import app

colors = {"background": "#111111",
          "text": "#7FDBFF"}


def data_visual_stack_bar(data, color):
    """
    Style for apps page
    """
    color_map = {"black": "0,0,0,",
                 "cyan": "60,163,206,",
                 "yellow": "255,245,57",
                 "magenta": "246,78,139,"}

    fig = go.Figure()
    fig.add_trace(go.Bar(
        y=data["Full Name"],
        x=data["Level"],
        name='Level',
        orientation='h',
        marker=dict(
                color=f'rgba({color_map.get(color)} 0.8)',
                line=dict(color=f'rgba({color_map.get(color)} 1.0)', width=3)
                )
        ))
    fig.add_trace(go.Bar(
        y=data["Full Name"],
        x=data["Used"],
        name='Used',
        orientation='h',
        marker=dict(
            color='rgba(68, 81, 90, 0.4)',
            line=dict(color='rgba(58, 71, 80, 1.0)', width=3)
            )
        ))

    if color != "black":
        fig.update_layout(barmode='stack', height=400,
                          autosize=True,
                          plot_bgcolor="#111111",
                          paper_bgcolor="#111111",
                          font=dict(family="Courier New, monospace", size=16,  color=color))
    else:
        fig.update_layout(barmode='stack', height=1200,
                          autosize=True,
                          plot_bgcolor="#a4a4a4",
                          paper_bgcolor="#a4a4a4",
                          font=dict(family="Courier New, monospace", size=18, color=color))
    return fig


def data_preparation(df, color):
    toner_data = df[["Full Name", "TonerType", "Level", "Used"]].loc[df["TonerType"] == color].sort_values("Level")
    return data_visual_stack_bar(toner_data, color)


def layout():
    df = pd.DataFrame(list(tmp_mongo.find()))
    df["CartridgeMaxCapacity"] = df["CartridgeMaxCapacity"].replace(0, 0.0001)

    df["TonerType"] = df["TonerType"].replace(np.nan, "black")
    df["Level"] = [int(float(df["TonerLevel"][i]) * 100 / float(df["CartridgeMaxCapacity"][i])) for i in range(len(df))]
    df["Used"] = [100 - df["Level"][i] for i in range(len(df))]
    df["Full Name"] = [str(df["location"][i]) + ": " + str(df["TonerModel"][i]) + " " for i in range(len(df))]

    return html.Div(style={"backgroundColor": colors["background"]}, children=[
        html.H1(
            children="Toner Level RUD",
            style={"textAlign": "center", "color": colors["text"]}),

        html.H6(children="Author Denys Pavliuk",
                style={"textAlign": "center", "color": colors["text"]}),

        html.Div(children=[
            dcc.Graph(
                id="graph-black",
                figure=data_preparation(df=df, color="black"),
                className='seven columns'),
            dcc.Graph(
                id="graph-magenta",
                figure=data_preparation(df=df, color="magenta"),
                className='five columns'),
            dcc.Graph(
                id="graph-yellow",
                figure=data_preparation(df=df, color="yellow"),
                className='five columns'),
            dcc.Graph(
                id="graph-cyan",
                figure=data_preparation(df=df, color="cyan"),
                className='five columns')],
            className='double-graph',
            style={'width': '100%', 'display': 'inline-block'})])