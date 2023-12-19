import dash
from dash import dcc, html, clientside_callback, ClientsideFunction, Input, Output, State
import dash_bootstrap_components as dbc
from dash import dash_table
from datetime import datetime
import pandas as pd
import os
import re
import random
import time
from dotenv import load_dotenv
import logging
log = logging.getLogger('werkzeug')
log.setLevel(logging.CRITICAL)

app = dash.Dash(__name__,title="&#65279;", update_title=None,meta_tags=[
                {"name": "viewport", "content": "width=device-width, initial-scale=1"}
            ],)
app.config.external_stylesheets = [dbc.themes.DARKLY]

app._favicon = ("peeporain.gif")

server = app.server

tab_style = {
    'border': '1px solid #0a0a0a',
    'padding-bottom': '39px',
    'color': 'black',
    'backgroundColor': '#779ECB',
    'border-radius':'20px',
    'margin':'5px',
    'width':'330px',
    'height':'50px',    
}

tab_selected_style = {
    'border': '5px solid #779ECB',
    'backgroundColor': '#386394',
    'color': 'white',
    'padding-bottom': '40px',
    'fontWeight': 'bold',
    'border-radius':'20px',
    'width':'330px',
    'height':'50px',
}

icons = os.listdir('./assets/icons')
full_paths = [os.path.join('./assets/icons', icon) for icon in icons]

def extract_date(filename):
    parts = filename.split('_')
    date_part = parts[1]
    cycle_part = parts[2]
    return date_part, cycle_part

def serve_layout():

    load_dotenv(override=True)
    random.seed(os.environ['RAND'])
    rand_image = random.choice(full_paths)

    return html.Div(
    style={'textAlign': 'center', 'font-family': "Lucida Console, monospace", },
    children=[
        dbc.Alert(id="countdown", color="primary"),
        dcc.Interval(
            id="interval-component-countdown",
            interval=100, 
            n_intervals=0,
        ),
        html.Div([
    ], style={'bottom': 0, 'left': 0, 'width': '100%'}),
        dcc.Tabs(id='tabs', value='tab-00',style={'margin':'auto'},children=[
            dcc.Tab(id='tab1',label='', value='tab-00',style=tab_style,selected_style=tab_selected_style),
            dcc.Tab(id='tab2',label='', value='tab-06',style=tab_style,selected_style=tab_selected_style),
            dcc.Tab(id='tab3',label='', value='tab-12',style=tab_style,selected_style=tab_selected_style),
            dcc.Tab(id='tab4',label='', value='tab-18',style=tab_style,selected_style=tab_selected_style),
        ]),
        html.Div(id="table-output", style={'textAlign': 'center', 'padding-top': '40px','padding-bottom': '40px','margin': 'auto',},className="table-size"),
        dcc.Interval(id="interval-component", interval=1 * 30 * 1000, n_intervals=0,),
        dcc.Interval(id="peepo-interval-component", interval=5 * 60 * 1000, n_intervals=0),
        html.Div(id='cycle-selection', style={'display': 'none'}),
        html.Div(id='filtered_list', style={'display': 'none'}),
        html.Br(),
        html.Div(id='progress-div', children=[dbc.Progress(id='progress-bar', min=0, max=30, value=0, style={'margin-bottom':'10px','width': '180px'})],style={'display': 'flex', 'justify-content': 'center', 'align-items': 'center'}),
        html.Div([html.Img(src="assets/hello_kitty.gif", style={'width': '6%', 'height': 'auto'}),
                  html.Div(id='peepo', children = [html.Img( src=rand_image, srcSet=rand_image, style={"max-width": '100%'})],style={"display": "flex", "align-items":"center" , "max-width": '6%'}),
    ], style={"display": "flex", "justify-content":"center"}),
    html.Div(id='col_len', style={'display': 'none'}),
])


app.layout = serve_layout

clientside_callback(
    ClientsideFunction(
        namespace='clientside',
        function_name='update_progress_bar'
    ),
    [Output('progress-bar', 'value'),
    Output('progress-div', 'style')],
    [Input("interval-component-countdown", "n_intervals"),
    Input("col_len", "children")]
)

clientside_callback(
    ClientsideFunction(
        namespace='clientside',
        function_name='update_countdown'
    ),
    Output('countdown', 'children'),
    Input("interval-component-countdown", "n_intervals")
)

@app.callback(
    Output('cycle-selection', 'children'),
    [Input('tabs', 'value')])
def cycle_tab(tab_value):
    cycle_hour = tab_value.split('-')[1] if tab_value else '00'
    return cycle_hour

@app.callback(
    Output("peepo", "children"),
    [Input("peepo-interval-component", "n_intervals")])
def peepo(n):
    
    load_dotenv(override=True)
    random.seed(os.environ['RAND'])

    report_times = [datetime.now().replace(hour=3, minute=0, second=0).timestamp(),
                datetime.now().replace(hour=7, minute=0, second=0).timestamp(),
                datetime.now().replace(hour=12, minute=15, second=0).timestamp(),
                datetime.now().replace(hour=17, minute=50, second=0).timestamp()]
    
    for tm in report_times:
        if time.time()-600<tm and time.time()>tm:
            rand_image = random.choice(full_paths)
            return html.Img( src=rand_image, srcSet=rand_image ,style={"max-height": '100%'})
    raise SystemExit()

@app.callback([Output("table-output", "children"),
              Output("col_len", "children"),
              Output("filtered_list", "children"),
              Output('tab1','label'),
              Output('tab2','label'),
              Output('tab3','label'),
              Output('tab4','label'),],
              Input("interval-component", "n_intervals"),
               Input("cycle-selection", "children"))
def update_table(n, cycle_hour,):

    report_ls = os.listdir("./reports")
    tab1_label = tab2_label = tab3_label = tab4_label = "TBA"
    filtered_list = [item for item in report_ls if item.startswith('report_2023')]
    for file in filtered_list:
        tab_l = extract_date(file)
        date = datetime.strptime(tab_l[0],'%Y-%m-%d')
        date = date.strftime('%d-%m-%Y')
        filenames = f"{date} - {tab_l[1]}"
    
        if filenames.endswith('00'):
            tab1_label = filenames
        elif filenames.endswith('06'):
            tab2_label = filenames
        elif filenames.endswith('12'):
            tab3_label = filenames
        elif filenames.endswith('18'):
            tab4_label = filenames

    r = re.compile(f"_{cycle_hour}$")
    try:
        fn = list(filter(r.search, report_ls))[0]
    except:
        return None,None,None, tab1_label, tab2_label, tab3_label, tab4_label

    filename = f"./reports/{fn}"

    report_df = pd.read_csv(filename)
    report_df = report_df.fillna("")
    report_df = report_df.map(lambda x: x.lower() if isinstance(x, str) else x)
    report_df.columns = map(str.lower, report_df.columns)

    
    col_len = (report_df['current fc']!='').sum()


    def calculate_color(value):
        try:
            numeric_value = float(value)
            if -30 < numeric_value <= 0:
                red_value = int(255 - abs(numeric_value) * 85)
                return f'rgb(255, {red_value}, {red_value})'
            elif 0 <= numeric_value < 30:
                blue_value = int(255 - abs(numeric_value) * 85)
                return f'rgb({blue_value}, {blue_value}, 255)'
            else:
                return 'rgb(73,77,74)'
        except ValueError:
            return 'rgb(73,77,74)'
        
    
    col_names = ['diff from normal','diff 12 hours ago','diff 24 hours ago']


    style_conditions = [
        {
            'if': {'column_id': col, 'row_index': i},
            'backgroundColor': calculate_color(value) if col in col_names else 'rgb(73,77,74)',
            'color': 'black' if col in col_names else 'white'
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
    
    return html.Div([table]), col_len, filtered_list, tab1_label, tab2_label, tab3_label, tab4_label


if __name__ == "__main__":
    app.run_server(port=8050, debug=True)
