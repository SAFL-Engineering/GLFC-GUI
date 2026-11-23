from dash import Dash, dcc, html, callback, Input, Output ,dash_table,ctx,State
import dash_daq as daq
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

    if i > 30: #after 30 seconds stop trying to connect. 
        print(f"No MQTT message has been received after 30 seconds. Aborting.")
        break
if i != 0:
    print('Message Received!')

beckhoff_plc.axes_enabled = beckhoff_plc.data['MOTION/CTR_ECHO']['AXESEN']
beckhoff_plc.loop_script  = beckhoff_plc.data['MOTION/CTR_ECHO']["CMDLOOP"]

credentials = creds.credentials
token       = creds.token

update_interval = 250 #msec
active_clients = {}

app = Dash(name=__name__,use_pages=True)
auth = dash_auth.BasicAuth(app,credentials)
app.server.secret_key = token

@app.server.before_request
def ensure_client_id():
    if "client_id" not in flask.session:
        flask.session["client_id"] = str(uuid.uuid4())

## Code for preventing more than one connection to the GUI. 
ACTIVE_SESSION = {
    "session_id": None,
    "last_seen": 0
}
TIMEOUT_SECONDS = 10  # Seconds before an inactive connection is dropped



app.layout = html.Div(children= [
    html.Div(children=[
        dcc.Store(id="session-store",storage_type="session"),
        dcc.Interval(id="heartbeat-interval",interval=3000,n_intervals=0),
        dcc.Interval(id='interval-timer',interval=update_interval,n_intervals=0),
        dcc.Store(id='stored_variables',data={'last-loop-time':datetime.datetime.now()}),
        html.Img(src=dash.get_asset_url("FishPass_Banner.jpeg"),style={"display":"block","marginLeft":"auto","marginRight":"auto","width":"30%"}),
        html.H1("Data Carriage Control Interface",style={'textAlign':'center'}),
        html.Div(id='app-content')]),
    html.Div(id='main_ui',children=[
        safl.value_display(title="Connected Users",id='connected-users-label'),
        safl.value_display(title='Time since last Message',           id='last-message-time'    ),
        safl.value_display(title='HMI Loop time',id='hmi-loop-time'),
        html.Br(),
        safl.value_display(title='Currently Selected Basin',id='mainpage-selected-basin'),
        html.Br(),
        safl.value_display('Motion Status',id='pause-status'),
        html.Div(children=[
            dcc.Button(children=['Pause'],id='stop-start',className='button'),
            dcc.Button(children=['Cancel'],id='cancel',className='button')
        ],className='divJogButtons'),
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
            dash.page_container])])
],className='divOverall')

@app.callback(
    Output("app-content", "children"),
    Output("session-store", "data"),
    Output('main_ui','style'),
    Output('interval-timer','disabled'), #disable the interval timer if the user is denied access so we don't bog down the system.
    Input("heartbeat-interval", "n_intervals"),
    State("session-store", "data")
)
def manage_single_session(n, store_data):
    current_time = time.time()
    
    # Ensure client has a persistent UUID for this tab/session
    session_id = store_data.get("id") if store_data else str(uuid.uuid4())
    
    # Check if existing lock expired
    lock_is_active = (current_time - ACTIVE_SESSION["last_seen"]) < TIMEOUT_SECONDS
    
    # Grant access if there is no lock, or lock is held by the same session ID
    if not lock_is_active or ACTIVE_SESSION["session_id"] == session_id:
        ACTIVE_SESSION["session_id"] = session_id
        ACTIVE_SESSION["last_seen"] = current_time
        
        # Render actual dashboard content
        main_ui = html.Div([
            html.H2("You are the only connected User")        
        ],style={'display':'None'})
        return main_ui, {"id": session_id},{'visibility':'visible'},False

    # Reject connection if another device/browser holds the lock
    warning_ui = html.Div(
        style={
            "textAlign": "center",
            "marginTop": "100px",
            "color": "#721c24",
            "backgroundColor": "#f8d7da",
            "padding": "20px",
            "borderRadius": "8px",
            "maxWidth": "500px",
            "margin": "100px auto"
        },
        children=[
            html.H3("Access Denied"),
            html.P("Another user or browser session is currently connected to this app."),
            html.P("Please wait for them to disconnect or close their browser tab."),
            html.P("This browser tab will become active 10 seconds after the other session is closed.")
        ]
    )
    return warning_ui, {"id": session_id},{'visibility':'hidden'},True



@callback(Output('last-message-time','children'),
          Output('last-message-time','style'),
          Output('hmi-loop-time','children'),
          Output('stored_variables','data'),
          Output('pause-status','children'),
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
    if beckhoff_plc.data['MOTION/STATUS']['Stop_Int'] == 1:
        pause_status = 'Paused'
    else:
        pause_status = 'Not Paused'

    return f'{datetime.datetime.now()-beckhoff_plc.time_of_last_message}',style,f'{dt_loop}',stored_data,pause_status

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

@callback(Output('mainpage-selected-basin','children'),
          Output('stop-start','children'),
          Input('interval-timer','n_intervals'))
def update_selected_basin(n):
    which_basin = beckhoff_plc.data['MOTION/STATUS']['basinstate']
    paused_status = beckhoff_plc.data['MOTION/STATUS']['Stop_Int']

    if paused_status == True:
        pause_text = 'Unpause'
    else:
        pause_text = 'Pause'
    
    if which_basin == 0:
        basin_text =  "A"
    elif which_basin == 1:
        basin_text =  "B"
    else: 
        basin_text = "Unknown"

    return basin_text, pause_text

@callback(Input('stop-start','n_clicks'),
          prevent_initial_call=True)
def pause_unpause(n):
    # print(f'Pause Button has been pressed: {n} times')
    new_ctr_struct = beckhoff_plc.data['MOTION/CTR_ECHO'].copy()
    try:
        del new_ctr_struct['timestamp']
    except:
        pass

    new_ctr_struct['STOP'] = True

    # Publicsh the JSON to the "MOTION/CTR" topic over MQTT
    beckhoff_plc.client.publish(topic='MOTION/CTR',payload=json.dumps(new_ctr_struct))

@callback(Input('cancel','n_clicks'))
def send_cancel(n):
    new_ctr_struct = beckhoff_plc.data['MOTION/CTR_ECHO'].copy()
    try:
        del new_ctr_struct['timestamp']
    except:
        pass

    new_ctr_struct['CANCEL'] = True

    # Publicsh the JSON to the "MOTION/CTR" topic over MQTT
    beckhoff_plc.client.publish(topic='MOTION/CTR',payload=json.dumps(new_ctr_struct))

@callback(Input('interval-timer','n_intervals'))
def send_heartbeat(n):
    '''
    Send a heartbeat every update interval to the MQTT MOTION/CTR topic that the PLC will read. 
    If jogging (or other motion) is ongoing and the PLC does not receive a heartbeat within a set amount of time motion will be stopped. 
    This is to protect against situations where the user might be jogging and then the network connection is lost or the browser is closed. 
    '''
    
    beckhoff_plc.client.publish(topic='MOTION/HB',payload='{"HEARTBEAT":true}')

    # print(f'{datetime.datetime.now()} Sent a heartbeat to Townswick')
    


if __name__ == '__main__':
    app.run(host='0.0.0.0',port=8050,debug=True)