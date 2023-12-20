from dash import dcc, html, clientside_callback, ClientsideFunction, Input, Output, State, Dash
from dash.exceptions import PreventUpdate
import dash_bootstrap_components as dbc
from dash import dash_table
import pandas as pd
import os
from io import StringIO
import logging
import redis
from helpers import get_tabs_from_files, calculate_color

log = logging.getLogger('werkzeug')
log.setLevel(logging.CRITICAL)

r = redis.Redis(host='localhost', port=6379, decode_responses=True)

app = Dash(__name__,title="&#65279;", update_title=None,meta_tags=[
                {"name": "viewport", "content": "width=device-width, initial-scale=1"}
            ],)
app.config.external_stylesheets, app._favicon, server = [dbc.themes.DARKLY], ("peeporain.gif"), app.server
icon_path = './assets/icons/'

def serve_layout():
    try: rand_image = r.get('peepo')
    except: rand_image = 'pepe-el.gif'
    return html.Div(
    style={'textAlign': 'center', 'font-family': "Lucida Console, monospace", },
    children=[ dbc.Alert(id="countdown", color="primary"), dcc.Interval( id="interval-component-countdown", interval=100, n_intervals=0,),
        dcc.Tabs(id='tabs', value='tab-00',style={'display':'flex', 'align-items': 'center', 'justify-content': 'center'},children=[
            dcc.Tab(id='tab1',label='', value='tab-00',className="custom-tab", selected_className="selected-tab"),
            dcc.Tab(id='tab2',label='', value='tab-06',className="custom-tab", selected_className="selected-tab"),
            dcc.Tab(id='tab3',label='', value='tab-12',className="custom-tab", selected_className="selected-tab"),
            dcc.Tab(id='tab4',label='', value='tab-18',className="custom-tab", selected_className="selected-tab"),]),
        html.Div(id="table-output", style={'textAlign': 'center', 'padding-top': '40px','padding-bottom': '40px','margin': 'auto',},className="table-size"),
        dcc.Interval(id="interval-component", interval=1 * 30 * 1000, n_intervals=0,),
        dcc.Interval(id="peepo-interval-component", interval=5 * 60 * 1000, n_intervals=0),
        html.Div(id='progress-div', children=[dbc.Progress(id='progress-bar', min=0, max=30, value=0, style={'margin-bottom':'10px','width': '180px'})],style={'display': 'flex', 'justify-content': 'center', 'align-items': 'center'}),
        html.Div([html.Img(src="assets/hello_kitty.gif", style={'width': '6%', 'height': 'auto'}),
                  html.Div(id='peepo', children = [html.Img( src=f'{icon_path}{rand_image}', srcSet=f'{icon_path}{rand_image}', style={"max-width": '100%'})],style={"display": "flex", "align-items":"center" , "max-width": '6%'}),
    ], style={"display": "flex", "justify-content":"center"}),
    dcc.Store(id='store', storage_type='memory', data={'peepo':'','column_length':16})
])

app.layout = serve_layout

clientside_callback(ClientsideFunction(namespace='clientside', function_name='update_progress_bar'),
    [Output('progress-bar', 'value'),Output('progress-div', 'style')],
    [Input("interval-component-countdown", "n_intervals"),State("store", "data")]
)
clientside_callback(ClientsideFunction(namespace='clientside', function_name='update_countdown'),
    Output('countdown', 'children'),
    Input("interval-component-countdown", "n_intervals")
)
@app.callback(
    [Output("peepo", "children"), Output('store', 'data', allow_duplicate=True)],
    [Input("peepo-interval-component", "n_intervals"), State('store', 'data'),], prevent_initial_call=True)
def peepo(n, data):
    try: rand_image= r.get('peepo')
    except: rand_image = 'pepe-el.gif'
    if (rand_image) == data['peepo']: raise PreventUpdate
    else:
        data['peepo'] = rand_image
        return html.Img( src=f'{icon_path}{rand_image}', srcSet=f'{icon_path}{rand_image}' ,style={"max-height": '100%'},), data

@app.callback([Output("table-output", "children"), Output("store", "data"), Output('tab1','label'),
              Output('tab2','label'),Output('tab3','label'),Output('tab4','label'),],
              Input("interval-component", "n_intervals"),Input('tabs', 'value'), State('store', 'data'))
def update_table(n, tab_value, data):

    cycle_hour = tab_value.split('-')[1] if tab_value else '00'
    report_ls = os.listdir("./reports")

    if (tabs:= r.hgetall("tabs")) is None:
        tabs, filename = get_tabs_from_files(report_ls)
    if (fn:= r.get(cycle_hour)) is None:
        if filename is None: return None, None, None, tabs['00'], tabs['06'], tabs['12'], tabs['18']
        else: report_df = pd.read_csv(f"./reports/{filename}")
    else: report_df = pd.read_csv(StringIO(fn))
    
    report_df = report_df.fillna("")
    report_df = report_df.map(lambda x: x.lower() if isinstance(x, str) else x)
    report_df.columns = map(str.lower, report_df.columns)

    data['column_length'] = (report_df['current fc']!='').sum()    
    col_names = ['diff from normal','diff 12 hours ago','diff 24 hours ago']
    style_conditions = [{'if': {'column_id': col, 'row_index': i},'backgroundColor': calculate_color(value) if col in col_names else 'rgb(73,77,74)',
                        'color': 'black' if col in col_names else 'white'} for col in report_df.columns[1:] for i, value in enumerate(report_df[col])]

    style_data_conditional_first_col = [{'if': {'column_id': report_df.columns[0], 'row_index': i},'backgroundColor': 'rgb(30, 30, 30)','color': 'white',
                                         'fontWeight': 'bold'} for i in range(len(report_df))]
    style_data_conditional = style_data_conditional_first_col + style_conditions

    table = dash_table.DataTable(id="table",
                                 data=report_df.to_dict("records"),
                                 columns=[{"name": i, "id": i} for i in report_df.columns],
                                 style_table={'border': '10px solid #313532','border-radius':'5px'},
                                 style_cell={'textAlign': 'center', 'font-family': 'Lucida Console,monospace','minWidth': '170px','border': '2px solid #3e423f'},
                                 style_header={'backgroundColor': 'rgb(30, 30, 30)', 'fontWeight': 'bold', 'color': 'white'},
                                 style_data={'backgroundColor': 'rgb(50, 50, 50)', 'color': 'white'},
                                 style_data_conditional=style_data_conditional)
    return html.Div([table]), data, tabs['00'], tabs['06'], tabs['12'], tabs['18']

if __name__ == "__main__":
    app.run_server(port=8050,)
