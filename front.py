import dash
from dash import dcc, html,ctx
from dash.dependencies import Input, Output, State
import dash_bootstrap_components as dbc
#from dash_bootstrap_templates import load_figure_template
from dash import dash_table
import pandas as pd
import os
from datetime import date
import re

#load_figure_template('darkly')

app = dash.Dash(__name__)
app.config.external_stylesheets = [dbc.themes.DARKLY]
app.title = 'My Weather App'
app._favicon = ("ok.ico")

server = app.server

app.layout = html.Div(
    style = {'textAlign':'center','font-family':"Tahoma, sans-serif",},
    children=[
        html.Button('Cycle 00', id='btn-00', n_clicks=0),
        html.Button('Cycle 06', id='btn-06', n_clicks=0),
        html.Button('Cycle 12', id='btn-12', n_clicks=0),
        html.Button('Cycle 18', id='btn-18', n_clicks=0),
        html.H4(id='title', style={'textAlign':'left','padding-top': '20px','padding-left':'20px'}),
        html.Div(id="table-output", style={'textAlign': 'center','padding-top': '10px'}),
        dcc.Interval(id="interval-component", interval=1 * 30 * 1000, n_intervals=0),
        html.H6(id='refresh_cycle', style={'textAlign':'right','padding-top':'20px','padding-right':'10px'}),
        html.Div(id='cycle-selection',style={'display': 'none'}),
        
        
    ]
)

def extract_date(filename):
    parts = filename.split('_')
    date_part = parts[1]
    cycle_part = parts[2]
    return date_part, cycle_part

@app.callback(
        Output('cycle-selection','children'),
        [Input('btn-00', 'n_clicks'),
        Input('btn-06', 'n_clicks'),
        Input('btn-12', 'n_clicks'),
        Input('btn-18', 'n_clicks'),]
)
def cycle_button(btn_00, btn_06, btn_12, btn_18):
    ctx = dash.callback_context

    if not ctx.triggered_id:
        button_id = 'btn-00'
    else:
        button_id = ctx.triggered_id.split('.')[0]

    if button_id == 'btn-00':
        cycle_hour = '00'
    elif button_id == 'btn-06':
        cycle_hour = '06'
    elif button_id == 'btn-12':
        cycle_hour = '12'
    elif button_id == 'btn-18':
        cycle_hour = '18'
    else:
        cycle_hour = '00'
    return cycle_hour


@app.callback(Output("table-output", "children"),
              Output("title","children"),
              Output("refresh_cycle","children"),
              [Input("interval-component", "n_intervals"),
               Input("cycle-selection","children")])
def update_table(n,cycle_hour):

    report_ls = os.listdir("./reports")
    r = re.compile(f"_{cycle_hour}$")
    fn = list(filter(r.search, report_ls))[0]
    
    cycle_date = extract_date(fn)
    filename = f"./reports/{fn}"
    
    report_df = pd.read_csv(filename)
    report_df = report_df.fillna("")

    def calculate_color(value):
        try:
            numeric_value = float(value)
            if -3 < numeric_value < 0:
                red_value = int(255 - abs(numeric_value) * 85) 
                return f'rgb(255, {red_value}, {red_value})'
            elif 0 < numeric_value < 3:
                blue_value = int(numeric_value * 85)
                return f'rgb({blue_value}, {blue_value}, 255)'
            else:
                return 'rgb(73,77,74)'
        except ValueError:
            return 'rgb(73,77,74)'

    style_conditions = [
    {
        'if': {'column_id': col, 'row_index': i},
        'backgroundColor': calculate_color(value),
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

    title = f"{cycle_date[0]}, Cycle {cycle_hour}"
    refresh = f"Refreshed {n} times"
    table = dash_table.DataTable(id="table",
                                data = report_df.to_dict("records"),
                                columns = [{"name": i, "id": i} for i in report_df.columns],
                                style_table={'height': '600px'},
                                style_cell={'textAlign':'center','font-family':'Tahoma,sans-serif'},
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
    app.run_server(port=8050)