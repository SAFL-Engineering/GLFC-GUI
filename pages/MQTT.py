from dash import Dash, dcc, html, callback, Input, Output ,dash_table,ctx,State
import dash
from Beckhoff_PLC import beckhoff_plc
import SAFL_Dash_Toolbox as safl
import time

dash.register_page(__name__,title='View PLC Comms')


layout = html.Div(id='mqtt_topics')

@callback(Output('mqtt_topics','children'),
        Input('interval-timer','n_intervals'),
        prevent_initial_call=False)
def update_status_table(n):
    tables = []
    for topic in beckhoff_plc.data.keys():
        # print(beckhoff_plc.data[topic])
        tables.append(safl.json_table(title=topic,json_dict=beckhoff_plc.data[topic]))

    div = html.Center(html.Div(children=tables,className='divCentered'))
    return div


