import dash
from dash import dcc, html
from dash.dependencies import Input, Output
import dash_bootstrap_components as dbc
#from dash_bootstrap_templates import load_figure_template
from dash import dash_table
import pandas as pd
import os

#load_figure_template('darkly')

app = dash.Dash(__name__)
app.config.external_stylesheets = [dbc.themes.DARKLY]
app.title = 'My Weather App'
app._favicon = ("ok.ico")


app.layout = html.Div(
    style = {'textAlign':'center','font-family':"Arial, sans-serif",},
    children=[
        html.H4(id='title', style={'padding-top': '20px'}),
        html.Div(id="table", style={'textAlign': 'center','padding-top': '20px'}),
        dcc.Interval(id="interval-component", interval=1 * 60 * 1000, n_intervals=0),
        html.H6(id='refresh_cycle', style={'textAlign':'right','padding-top':'20px','padding-right':'10px'}),
        
    ]
)

def extract_date(filename):
    parts = filename.split('_')
    date_part = parts[1]
    cycle_part = parts[2]
    return date_part, cycle_part

@app.callback(Output("table", "children"),
              Output("title","children"),
              Output("refresh_cycle","children"),
              [Input("interval-component", "n_intervals")])
def update_table(n):
    last_report_fn = os.listdir("./reports")[0]
    cycle_date = extract_date(last_report_fn)
    report_df = pd.read_csv(f"./reports/{last_report_fn}")
    report_df = report_df.fillna("")
    style_conditions = [
    {
        'if': {'column_id': col},
        'backgroundColor': 'rgb(118,148,126)' if any(report_df[col] != '') else 'rgb(73,77,74)',
        'color': 'white'
    } for col in report_df.columns[1:]]
    style_data_conditional_first_col = [
    {
        'if': {'column_id': report_df.columns[0]},
        'backgroundColor': 'rgb(30, 30, 30)',
        'color': 'white'
    }]
    style_data_conditional = style_data_conditional_first_col + style_conditions

    title = f"Report For {cycle_date[0]}, Cycle {cycle_date[1]}"
    refresh = f"Refreshed {n} times"
    table = dash_table.DataTable(id="table",
                                data = report_df.to_dict("records"),
                                columns = [{"name": i, "id": i} for i in report_df.columns],
                                style_table={'height': '600px'},
                                style_cell={'textAlign':'center','font-family':'Arial,sans-serif'},
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
    return table, title, refresh


if __name__ == "__main__":
    app.run_server(debug=True)
