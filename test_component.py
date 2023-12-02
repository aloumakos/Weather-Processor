import dash
from dash import dcc, html
from dash.dependencies import Input, Output
from datetime import datetime, timedelta

app = dash.Dash(__name__)


# Define layout
app.layout = html.Div([
    html.H1("Countdown Timer"),
    
    html.Div(id='countdown-output'),

    dcc.Interval(
        id='interval-component',
        interval=1000,  # in milliseconds
        n_intervals=0
    )
])

report_times = [0,6,12,18]
# Define callback to update countdown
@app.callback(
    Output('countdown-output', 'children'),
    Input('interval-component', 'n_intervals')
)
def update_countdown(n_intervals):
    current_time = datetime.now()
    countdowns = [str(target_time - current_time).split(".")[0] for target_time in target_times]
    
    return html.Div([
        html.P(f"Time to {target_hour}: {countdown}") for target_hour, countdown in zip([6, 12, 18, 0], countdowns)
    ])

if __name__ == '__main__':
    app.run_server(debug=True)
