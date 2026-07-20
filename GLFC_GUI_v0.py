from dash import Dash, dcc, html, callback, Input, Output ,dash_table,ctx,State
import dash
import dash_auth
import credentials as creds
from Beckhoff_PLC import beckhoff_plc
import SAFL_Dash_Toolbox as safl
import datetime
import time
import json
import flask
import uuid

i = 0
while not beckhoff_plc.data:
    i = i+1
    print(f'Waiting for an MQTT message to be received. Waited: {i} seconds')
    time.sleep(1)
if i != 0:
    print('Message Received!')

credentials = creds.credentials
token       = creds.token

update_interval = 200 #msec
active_clients = {}

app = Dash(name=__name__,use_pages=True)
auth = dash_auth.BasicAuth(app,credentials)
app.server.secret_key = token

@app.server.before_request
def ensure_client_id():
    if "client_id" not in flask.session:
        flask.session["client_id"] = str(uuid.uuid4())

app.layout = html.Div(children= [
    dcc.Interval(id='interval-timer',interval=update_interval,n_intervals=0),
    dcc.Store(id='stored_variables',data={'last-loop-time':datetime.datetime.now()}),
    html.Img(src=dash.get_asset_url("FishPass_Banner.jpeg"),style={"display":"block","marginLeft":"auto","marginRight":"auto","width":"30%"}),
    html.H1("Data Carriage HMI",style={'textAlign':'center'}),
    safl.value_display(title="Connected Users",id='connected-users-label'),
    safl.value_display(title='Time since last Message',           id='last-message-time'    ),
    safl.value_display(title='HMI Loop time',id='hmi-loop-time'),
    html.Br(),
    html.Div(children=[
        html.H3('Select a View',style={'textAlign':'center'}),
        html.Div(children=[
            html.Div(
                dcc.Link(
                    dcc.Button(f"{page['name']}",className='custom-btn') ,href=page["relative_path"]
                    )
            ) for page in dash.page_registry.values()
        ],className='divHorizontal'),
        html.Br(),
        dash.page_container])
],className='divOverall')

@callback(Output('last-message-time','children'),
          Output('last-message-time','style'),
          Output('hmi-loop-time','children'),
          Output('stored_variables','data'),
          Input('interval-timer','n_intervals'),
          State('stored_variables','data'))
def update_hmi_loop_time(n,stored_data):
    time_now = datetime.datetime.now()
    last_loop_time = datetime.datetime.strptime(stored_data['last-loop-time'],'%Y-%m-%dT%H:%M:%S.%f')
    # print(last_loop_time)
    dt_loop = time_now-last_loop_time
    stored_data['last-loop-time'] = time_now

    elapsed_time = datetime.datetime.now()-beckhoff_plc.time_of_last_message
    elapsed_time = elapsed_time.seconds+elapsed_time.microseconds/1e6
    if elapsed_time > 5: #sec
        style = {'color':"#FF0000","fontWeight":"bold"}
    else:
        style = {'color':"#0C9600","fontWeight":"bold"}


    # print(f'Test: {beckhoff_plc.counter}')
    # new_ctr_struct = beckhoff_plc.data['MOTION/CTR_ECHO']
    # new_ctr_struct['SCRIPTNAME'] = f'Test: {beckhoff_plc.counter}'
    # beckhoff_plc.counter +=1
    # json_ctr = json.dumps(new_ctr_struct)
    # # Publicsh the JSON to the "MOTION/CTR" topic over MQTT
    # beckhoff_plc.client.publish(topic='MOTION/CTR',payload=json_ctr)

    return f'{datetime.datetime.now()-beckhoff_plc.time_of_last_message}',style,f'{dt_loop}',stored_data

@callback(Output('connected-users-label','children'),
    Input("interval-timer","n_intervals"),
    prevent_initial_call=True
)
def heartbeat(n):
    session_id = flask.session.get("client_id")
    # print(session_id)
    active_clients[session_id] = time.time()

    now = time.time()
    connected_clients = len([t for t in active_clients.values() if now - t < 10])

    return f'{connected_clients}'


if __name__ == '__main__':
    app.run(host='0.0.0.0',port=8050,debug=True)