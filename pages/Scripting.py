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
        html.H3('Add Tasks to Script'),
        html.Label('Enter a Name for your Script:'),
        dcc.Input(id='script-name-input',type='text',debounce=True),

        html.Label('Select a Command Type:'),
        dcc.Dropdown(options=['Null Instruction','Pause and Wait for Button Press','Go to Absolute Position','Move Relative Distance'],value='Go to Absolute Position',id='motion-command'),

        html.Div(children=[
            html.Div(children=[
                html.Label('Set X Target Position:'),
                dcc.Input(id='setxpos',type='number',debounce=True,step=0.1)],style={'margin':'10px'}),
            html.Div(children=[
                html.Label('Set X Target Velocity:'),
                dcc.Input(id='setxvel',type='number',debounce=True,step=1)],style={'margin':'10px'}),
        ],className='divHorizontal'),

        html.Div(children=[
            html.Div(children=[
                html.Label('Set Y Target Position:'),
                dcc.Input(id='seyxpos',type='number',debounce=True,step=0.1)],style={'margin':'10px'}),
            html.Div(children=[
                html.Label('Set Y Target Velocity:'),
                dcc.Input(id='setyvel',type='number',debounce=True,step=1)],style={'margin':'10px'}),
        ],className='divHorizontal'),
        
        html.Div(children=[
            html.Div(children=[
                html.Label('Set Z Target Position:'),
                dcc.Input(id='setzpos',type='number',debounce=True,step=0.1)],style={'margin':'10px'}),
            html.Div(children=[
                html.Label('Set Z Target Velocity:'),
                dcc.Input(id='setzvel',type='number',debounce=True,step=1)],style={'margin':'10px'}),
        ],className='divHorizontal'),

        html.Label('Set Pause Time Before Next Move (milliseconds):'),
        dcc.Input(id='setpause',type='number',debounce=True,step=1),

        html.Label('Add a Comment for this instruction (optional)'),
        dcc.Input(id='comment',type='text',debounce=True),

        dcc.Button('CMDADD',id='CMDADD',className='button'),
        dcc.Button('CMDCLR',id='CMDCLR',className='button'),
        dcc.Button('CMDDEL',id='CMDDEL',className='button'),
        dcc.Checklist(options=['Loop Script'],id='CMDLOOP'),
        html.Label('Select which Basin this Script should be run in:'),
        dcc.Dropdown(id='BASINCTR',options=['Basin A','Basin B']),
        dcc.Button('CMDRUN',id='CMDRUN',className='button'),
        html.Label('How Many Times to Repeat this Script?'),
        dcc.Input(id='SCRIPTITERATIONS',type='number'),
       
    ],className='divBorder'),

    html.Div(children = [
        html.H3('File Operations'),
        dcc.Button('CMDSCRIPTDEL',id='CMDSCRIPTDEL',className='button'),
        dcc.Button('CMDSCRIPTWRITE',id='CMDSCRIPTWRITE',className='button'),
        dcc.Button('CMDSCRIPTREAD',id='CMDSCRIPTREAD',className='button'),
        dcc.Button('CMDREQLIST',id='CMDREQLIST',className='button'),
        dcc.Button('CMDREQSCRIPT',id='CMDREQSCRIPT',className='button')
    ],className='divBorder')
],className='divHorizontal')


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

@callback(Input('CMDADD','n_clicks'))
def send_CMDADD(n):
    new_ctr_struct = beckhoff_plc.data['MOTION/CTR_ECHO']
    del new_ctr_struct['timestamp']

    new_ctr_struct['CMDADD'] = True
    # Convert the Dict to a properly JSON formatted string
    json_ctr = json.dumps(new_ctr_struct)

    # Publicsh the JSON to the "MOTION/CTR" topic over MQTT
    beckhoff_plc.client.publish(topic='MOTION/CTR',payload=json_ctr)

@callback(Input('setxpos','value'))
def send_new_xpos_instr(value):
    new_struct = beckhoff_plc.data['MOTION/INSTR_ECHO']
    del new_struct['timestamp']
    new_struct['SetXPosition'] = float(value)
    beckhoff_plc.client.publish(topic='MOTION/INSTR',payload=json.dumps(new_struct))

@callback(Input('setxvel','value'))
def send_new_xvel_instr(value):
    new_struct = beckhoff_plc.data['MOTION/INSTR_ECHO']
    del new_struct['timestamp']
    new_struct['SetXVelocity'] = int(value)
    beckhoff_plc.client.publish(topic='MOTION/INSTR',payload=json.dumps(new_struct))