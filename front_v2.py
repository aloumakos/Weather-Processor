import dash
from dash import dcc, html
from dash.dependencies import Input, Output
import dash_bootstrap_components as dbc
from dash import dash_table
from datetime import datetime
import pandas as pd
import os
import re
import logging

# load_figure_template('darkly')

logging.basicConfig(level=logging.DEBUG)

app = dash.Dash(__name__)
app.config.external_stylesheets = [dbc.themes.DARKLY]
app.title = 'Based'
app._favicon = ("peeporain.gif")

server = app.server

tabs_styles = {
    'height': '100px'
}
tab_style = {
    'borderTop': '1px solid #0a0a0a',
    'borderBottom': '1px solid #0a0a0a',
    'borderLeft': '1px solid #0a0a0a',
    'borderRight': '1px solid #0a0a0a',
    'padding': '15px',
    'color': 'black',
    'backgroundColor': '#779ECB',
    'border-radius':'20px',
    'margin':"5px"
}

tab_selected_style = {
    'borderTop': '5px solid #779ECB',
    'borderBottom': '5px solid #779ECB',
    'borderLeft': '5px solid #779ECB',
    'borderRight': '5px solid #779ECB',
    'backgroundColor': '#386394',
    'color': 'white',
    'padding': '16px',
    'fontWeight': 'bold',
    'border-radius':'20px'
    
}

app.layout = html.Div(
    style={'textAlign': 'center', 'font-family': "Lucida Console, monospace", },
    children=[
        html.Div(id="countdown-output"),
        dcc.Interval(
            id="interval-component-countdown",
            interval=1000,  # in milliseconds
            n_intervals=0,
        ),
        html.H1(children="hello werld", style={'textAlign': 'center', 'padding-top': '30px','padding-bottom':'40px'}),
        dcc.Tabs(id='tabs', value='tab-00', children=[
            dcc.Tab(label='cycle 00', value='tab-00',style=tab_style, selected_style=tab_selected_style),
            dcc.Tab(label='cycle 06', value='tab-06',style=tab_style, selected_style=tab_selected_style),
            dcc.Tab(label='cycle 12', value='tab-12',style=tab_style, selected_style=tab_selected_style),
            dcc.Tab(label='cycle 18', value='tab-18',style=tab_style, selected_style=tab_selected_style),
        ],
        style={'backgroundColor': 'transparent'}),
        html.H5(id='title', style={'textAlign': 'center', 'padding-top': '20px'}),
        html.H5(id='current-time', style={'textAlign': 'center', 'padding-top': '20px'}),
        html.Div(id="table-output", style={'textAlign': 'center', 'padding-top': '20px','margin': 'auto'}),
        dcc.Interval(id="interval-component", interval=1 * 30 * 1000, n_intervals=0),
        html.H6(id='refresh_cycle', style={'textAlign': 'right', 'padding-top': '20px', 'padding-right': '10px'}),
        html.Div(id='cycle-selection', style={'display': 'none'}),
        
    ]
)

report_times = [3, 8, 13, 18]

@app.callback(
    Output("countdown-output", "children"),
    Output("current-time", "children"),
    Input("interval-component-countdown", "n_intervals"),
)
def update_countdown(n):
    now = datetime.now()
    next_report_times = [time for time in report_times if time > now.hour]

    if not next_report_times:
        next_report_time = min(report_times) + 24
    else:
        next_report_time = min(next_report_times)

    next_report_hour = next_report_time % 24

    next_report_datetime = datetime(now.year, now.month, now.day, next_report_hour)
    if next_report_hour == 0:
        time_difference = str(next_report_datetime - now).split(".")[0]
        time_difference =str(time_difference).split(",")[1]
    else:
        time_difference = str(next_report_datetime - now).split(".")[0]
    cd_output = f"time until next report: {time_difference}"
    current_time = datetime.now().strftime('%H:%M:%S')
    current_time =f"current time: {current_time}"
    return dbc.Alert(cd_output,color="primary"), current_time


def extract_date(filename):
    parts = filename.split('_')
    date_part = parts[1]
    cycle_part = parts[2]
    return date_part, cycle_part

@app.callback(
    Output('cycle-selection', 'children'),
    [Input('tabs', 'value')]
)
def cycle_tab(tab_value):
    cycle_hour = tab_value.split('-')[1] if tab_value else '00'
    return cycle_hour

@app.callback(Output("table-output", "children"),
              Output("title", "children"),
              Output("refresh_cycle", "children"),
              [Input("interval-component", "n_intervals"),
               Input("cycle-selection", "children")])
def update_table(n, cycle_hour):

    refresh = f"Refreshed {n} times"

    report_ls = os.listdir("./reports")
    r = re.compile(f"_{cycle_hour}$")
    try:
        fn = list(filter(r.search, report_ls))[0]
    except:
        return None, "Could not find data for this cycle atm", refresh

    cycle_date = extract_date(fn)
    filename = f"./reports/{fn}"

    report_df = pd.read_csv(filename)
    report_df = report_df.fillna("")
    report_df = report_df.applymap(lambda x: x.lower() if isinstance(x, str) else x)
    report_df.columns = map(str.lower, report_df.columns)

    def calculate_color(value):
        try:
            numeric_value = float(value)
            if -15 < numeric_value < 0:
                red_value = int(255 - abs(numeric_value) * 55)
                return f'rgb(255, {red_value}, {red_value})'
            elif 0 < numeric_value < 15:
                blue_value = int(255 - abs(numeric_value) * 55)
                return f'rgb({blue_value}, {blue_value}, 255)'
            else:
                return 'rgb(73,77,74)'
        except ValueError:
            return 'rgb(73,77,74)'


    style_conditions = [
        {
            'if': {'column_id': col, 'row_index': i},
            'backgroundColor': calculate_color(value) if col in report_df.columns[-2:] else 'rgb(73,77,74)',
            'color': 'black' if col in report_df.columns[-2:] else 'white'
        } for col in report_df.columns[1:] for i, value in enumerate(report_df[col])
    ]

    style_data_conditional_first_col = [
        {
            'if': {'column_id': report_df.columns[0], 'row_index': i},
            'backgroundColor': 'rgb(30, 30, 30)',
            'color': 'white',
            'fontWeight': 'bold'
        } for i in range(len(report_df))
    ]

    style_data_conditional = style_data_conditional_first_col + style_conditions

    title = cycle_date[0]
    title = datetime.strptime(title,'%Y-%m-%d')
    title = title.strftime("%d-%m-%Y")
    title = f"today's date: {title}"

    table = dash_table.DataTable(id="table",
                                 data=report_df.to_dict("records"),
                                 columns=[{"name": i, "id": i} for i in report_df.columns],
                                 style_table={'height': '600px','width': '80%','margin-right':'10px','margin-left':'30px'},
                                 style_cell={'textAlign': 'center', 'font-family': 'Lucida Console,monospace','minWidth': '170px'},
                                 style_header={
                                     'backgroundColor': 'rgb(30, 30, 30)',
                                     'fontWeight': 'bold',
                                     'color': 'white'},
                                 style_data={
                                     'backgroundColor': 'rgb(50, 50, 50)',
                                     'color': 'white'
                                 },
                                 style_data_conditional=style_data_conditional
                                 )
    return html.Div([table]), title, refresh







if __name__ == "__main__":
    app.run_server(port=8050,debug='True')
