import dash
from dash import dcc, html
from dash.dependencies import Input, Output
import pandas as pd
import os

app = dash.Dash(__name__)

app.layout = html.Div(
    [
        dcc.Graph(id="table"),
        dcc.Interval(id="interval-component", interval=1 * 60 * 1000, n_intervals=0),
    ]
)


@app.callback(Output("table", "figure"), [Input("interval-component", "n_intervals")])
def update_table(n):
    last_report_fn = os.listdir("./reports")[0]

    report_df = pd.read_csv(f"./reports/{last_report_fn}")
    report_df = report_df.fillna("")
    figure = {
        "data": [
            {
                "type": "table",
                "header": {
                    "values": report_df.columns,
                    "fill": {"color": "#0074cc"},
                    "font": {"color": "white"},
                },
                "cells": {
                    "values": [report_df[col] for col in report_df.columns],
                    "fill": {"color": "#e6f7ff"},
                },
            }
        ],
        "layout": {"title": f"Report Table - Interval {n}"},
    }
    return figure


if __name__ == "__main__":
    app.run_server(debug=True)
