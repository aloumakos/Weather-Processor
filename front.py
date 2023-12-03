import dash
from dash import dcc, html
from dash.dependencies import Input, Output
import dash_bootstrap_components as dbc
from dash import dash_table
from datetime import datetime,timedelta
import pandas as pd
import os
import re

# load_figure_template('darkly')
import logging
log = logging.getLogger('werkzeug')
log.setLevel(logging.ERROR)

app = dash.Dash(title="Based", update_title=None )
app.config.external_stylesheets = [dbc.themes.DARKLY]

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

def extract_date(filename):
    parts = filename.split('_')
    date_part = parts[1]
    cycle_part = parts[2]
    return date_part, cycle_part

report_ls = os.listdir("./reports")


app.layout = html.Div(
    style={'textAlign': 'center', 'font-family': "Lucida Console, monospace", },
    children=[
        html.Div(id="countdown-output"),
        dcc.Interval(
            id="interval-component-countdown",
            interval=100,  # in milliseconds
            n_intervals=0,
        ),
        html.H1(children="hello werld", style={'textAlign': 'center', 'padding-top': '30px','padding-bottom':'40px'}),
        dcc.Tabs(id='tabs', value='tab-00', style={'display':'inline-block'},children=[
            dcc.Tab(id='tab1',label='', value='tab-00',style=tab_style, selected_style=tab_selected_style),
            dcc.Tab(id='tab2',label='', value='tab-06',style=tab_style, selected_style=tab_selected_style),
            dcc.Tab(id='tab3',label='', value='tab-12',style=tab_style, selected_style=tab_selected_style),
            dcc.Tab(id='tab4',label='', value='tab-18',style=tab_style, selected_style=tab_selected_style),
        ]),
        html.H5(id='title', style={'display':'None'}),
        html.H5(id='current-time', style={'display':'None'}),
        html.Div(id="table-output", style={'textAlign': 'center', 'padding-top': '40px','padding-bottom': '40px','margin': 'auto','display':'inline-block'}),
        dcc.Interval(id="interval-component", interval=1 * 30 * 1000, n_intervals=0),
        html.H6(id='refresh_cycle', style={'display': 'none'}),
        #html.H6(id='refresh_cycle', style={'textAlign': 'right', 'padding-top': '20px', 'padding-right': '10px'}),
        html.Div(id='cycle-selection', style={'display': 'none'}),
        html.Br(),
        html.Div(dbc.Progress(id='progress-bar',value=0, max=30,style={'margin-bottom':'10px','width': '180px'}),style={'display': 'flex', 'justify-content': 'center', 'align-items': 'center'}),
        html.Div([
        html.Img(src="assets/hello_kitty.gif", style={'width': '10%', 'height': 'auto'}),
    ], style={'bottom': 0, 'left': 0, 'width': '100%'})
])


@app.callback(
    Output("progress-bar", "value"),
    [Input('interval-component-countdown', 'n_intervals')]
)
def update_progress_bar(n):
    progress = (n*0.1)%30
    return progress

report_times = [datetime.now().replace(hour=3, minute=0, second=0),
                datetime.now().replace(hour=8, minute=0, second=0),
                datetime.now().replace(hour=12, minute=15, second=0),
                datetime.now().replace(hour=17, minute=50, second=0)]

@app.callback(
    Output("countdown-output", "children"),
    Output("current-time", "children"),
    Input("interval-component-countdown", "n_intervals"),
)
def update_countdown(n):
    now = datetime.now()
    current_time = now.strftime('%H:%M:%S')

    next_report_times = [time for time in report_times if time > now]

    if not next_report_times:
        next_report_time = min(report_times) + timedelta(days=1)
    else:
        next_report_time = min(next_report_times)

    time_difference = str(next_report_time - now).split(".")[0]

    cd_output = f"time until next report: {time_difference}"
    current_time = f"current time: {current_time}"

    return dbc.Alert(cd_output, color="primary"), current_time

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
              Output('tab1','label'),
              Output('tab2','label'),
              Output('tab3','label'),
              Output('tab4','label'),
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
    report_df = report_df.map(lambda x: x.lower() if isinstance(x, str) else x)
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

    tabs_labels = []
    for file in report_ls[:-1]:
        tab_l = extract_date(file)
        date = datetime.strptime(tab_l[0],'%Y-%m-%d')
        date = date.strftime('%d-%m-%Y')
        filenames = f"{date} - {tab_l[1]}"
        tabs_labels.append(filenames)
    
    for i in tabs_labels:
        if i.endswith(str(00)):
            tab1_label = i
        if i.endswith(str('{:02d}'.format(6))):
            tab2_label = i
        if i.endswith(str(12)):
            tab3_label = i
        if i.endswith(str(18)):
            tab4_label = i
    

    table = dash_table.DataTable(id="table",
                                 data=report_df.to_dict("records"),
                                 columns=[{"name": i, "id": i} for i in report_df.columns],
                                 style_table={'border': '10px solid #313532','border-radius':'5px'},
                                 style_cell={'textAlign': 'center', 'font-family': 'Lucida Console,monospace','minWidth': '170px','border': '2px solid #3e423f'},
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
    
    
    
    
    return html.Div([table]), title, refresh, tab1_label, tab2_label, tab3_label, tab4_label


if __name__ == "__main__":
    app.run_server(port=8050)
