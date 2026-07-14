from dash import Dash, dcc, html, callback, Input, Output ,dash_table,ctx,State
import dash
from Beckhoff_PLC import beckhoff_plc
import SAFL_Dash_Toolbox as safl
import json
import time


dash.register_page(__name__)

# time.sleep(1)

layout = html.Div(children=[
    # html.Div(id='ctr-echo-table',className='divBorder'),                
    html.Div(children=[
        html.H3('Control Inputs'),
        html.Label('Enter a Name for your Script:'),
        dcc.Input(id='script-name-input',type='text',debounce=True),
        dcc.Button('CMDADD',id='CMDADD-true'),
        html.Br(),
        html.Label('Enter Acquisition Spacing (mm):'),
        dcc.Input(id='acqres-input',type='number',debounce=True),
        html.Br(),
        html.Label('Set X Position Instr:'),
        dcc.Input(id='setxpos',type='number',debounce=True),
        html.Br(),
        html.Label('Set X Velocity Instr:'),
        dcc.Input(id='setxvel',type='number',debounce=True),
        html.Button(
            html.Img(src=dash.get_asset_url('Green_LED_On.png'),style={'height':'30px','width':'30px'}),id='green-led',className='htmlButton'
        )



    
    ],className='divBorder')
],className='divHorizontal')


# @callback(Input('green-led','n_clicks'))
# def green_led(n):
#     print(f'Number of Clicks on the Green LED: {n}')

# @callback(Output('ctr-echo-table','children'              ),
#           Input('interval-timer','n_intervals'))
# def update_ctr_echo_values(n):
#     updated_table = safl.json_table(title=['MOTION/CTR_ECHO'],json_dict=beckhoff_plc.data['MOTION/CTR_ECHO'])

#     return updated_table

@callback(Input('script-name-input','value'),
          prevent_intiail_call=True)
def update_script_name(value):
    # Start with the current Control Struct Echo
    new_ctr_struct = beckhoff_plc.data['MOTION/CTR_ECHO']
    del new_ctr_struct['timestamp']
    #change the value in the struct for scriptname
    new_ctr_struct['SCRIPTNAME'] = value
    # new_ctr_struct = {'CTR':new_ctr_struct}
    # Convert the Dict to a properly JSON formatted string
    json_ctr = json.dumps(new_ctr_struct)

    # Publicsh the JSON to the "MOTION/CTR" topic over MQTT
    beckhoff_plc.client.publish(topic='MOTION/CTR',payload=json_ctr)

@callback(Input('CMDADD-true','n_clicks'))
def send_CMDADD(n):
    new_ctr_struct = beckhoff_plc.data['MOTION/CTR_ECHO']
    del new_ctr_struct['timestamp']

    new_ctr_struct['CMDADD'] = True
    # Convert the Dict to a properly JSON formatted string
    json_ctr = json.dumps(new_ctr_struct)

    # Publicsh the JSON to the "MOTION/CTR" topic over MQTT
    beckhoff_plc.client.publish(topic='MOTION/CTR',payload=json_ctr)

@callback(Input('acqres-input','value'),
          prevent_intiail_call=True)
def send_acqres(value):
    new_struct = beckhoff_plc.data['DAQ/CTR_ECHO']
    del new_struct['timestamp']
    new_struct['DAQACQRES'] = value
    beckhoff_plc.client.publish(topic='DAQ/CTR',payload=json.dumps(new_struct))

@callback(Input('setxpos','value'))
def send_new_xpos_instr(value):
    new_struct = beckhoff_plc.data['MOTION/INSTR_ECHO']
    del new_struct['timestamp']
    new_struct['SetXPosition'] = float(value)
    beckhoff_plc.client.publish(topic='MOTION/INSTR_BUFFER',payload=json.dumps(new_struct))

@callback(Input('setxvel','value'))
def send_new_xvel_instr(value):
    new_struct = beckhoff_plc.data['MOTION/INSTR_ECHO']
    del new_struct['timestamp']
    new_struct['SetXVelocity'] = int(value)
    beckhoff_plc.client.publish(topic='MOTION/INSTR_BUFFER',payload=json.dumps(new_struct))