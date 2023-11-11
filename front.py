import dash
from dash import dcc, html
import pandas as pd

# Sample DataFrame
@app.callback(
    
    ServersideOutput('table_current'),
    ServersideOutput('table_06'),
    ServersideOutput('table_12'),
    ServersideOutput('table_24'),
    ServersideOutput('diff_12'),
    ServersideOutput('diff_24')
)
def store_data(
    Input()
)

# Initialize the Dash app
app = dash.Dash(__name__)

# Define the layout of the app
app.layout = html.Div(
    [
        html.H1("Hello"),
        dcc.Graph(
            id="table",
            figure={
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
                "layout": {"title": "Report Table"},
            },
        ),
    ]
)

# Run the app
if __name__ == "__main__":
    app.run_server(debug=True)
