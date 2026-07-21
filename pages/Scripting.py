from dash import Dash, dcc, html, callback, Input, Output ,dash_table,ctx,State
import dash
from Beckhoff_PLC import beckhoff_plc
import SAFL_Dash_Toolbox as safl
import json
import pandas as pd

new_command = beckhoff_plc.data['MOTION/INSTR_ECHO']
del new_command['timestamp']

new_command['MotionCommand'] = 2

dash.register_page(__name__)

# time.sleep(1)

layout = html.Div(children=[
    # html.Div(id='ctr-echo-table',className='divBorder'),                
    html.Div(children=[
        html.H3('Add Tasks to Queue'),

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
                dcc.Input(id='setypos',type='number',debounce=True,step=0.1)],style={'margin':'10px'}),
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
        dcc.Input(id='setpause',type='number',debounce=True,step=1,min=0,value=0),

        html.Label('Add a Comment for this instruction (optional)'),
        dcc.Input(id='comment',type='text',debounce=True),
        html.Br(),

        dcc.Button('Add task to the queue',id='CMDADD',className='button'),
        dcc.Button('Delete the last task from the queue',id='CMDDEL',className='button'),
        dcc.Button('Clear the currently loaded queue',id='CMDCLR',className='button')
        
        
       
    ],className='divBorder'),
    html.Div(children=[
        html.Div(children = [
            html.H3('File Operations'),
            html.Label('Enter a Name for your Script:'),
            dcc.Input(id='script-name-input',type='text',debounce=True),
            html.Br(),
            dcc.Button('Save queue as script file on PLC',id='CMDSCRIPTWRITE',className='button'),
            dcc.Button('CMDSCRIPTDEL',id='CMDSCRIPTDEL',className='button'),            
            dcc.Button('CMDSCRIPTREAD',id='CMDSCRIPTREAD',className='button'),
            dcc.Button('Request List of Scripts from PLC',id='CMDREQLIST',className='button'),
            dcc.Button('CMDREQSCRIPT',id='CMDREQSCRIPT',className='button')
        ],className='divBorder'),
        html.Div(children=[
            html.H3('Run Script'),
            html.Label('Select which Basin this Script should be run in:'),
            dcc.Dropdown(id='BASINCTR',options=['Basin A','Basin B']),
            dcc.Checklist(options=['Loop Script'],id='CMDLOOP'),
            html.Label('How Many Times to Repeat this Script?'),
            dcc.Input(id='SCRIPTITERATIONS',type='number'),
            html.Br(),
            dcc.Button('CMDRUN',id='CMDRUN',className='button')
        ],className='divBorder')
    ])
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
    # Send the json array with the new command 
    beckhoff_plc.client.publish(topic='MOTION/INSTR',payload=json.dumps(new_command))

    # Build the CTR Structure to send the CMDADD command
    new_ctr_struct = beckhoff_plc.data['MOTION/CTR_ECHO']
    del new_ctr_struct['timestamp']

    new_ctr_struct['CMDADD'] = True
    # Convert the Dict to a properly JSON formatted string
    json_ctr = json.dumps(new_ctr_struct)

    # Publicsh the JSON to the "MOTION/CTR" topic over MQTT
    beckhoff_plc.client.publish(topic='MOTION/CTR',payload=json_ctr)

@callback(Input('motion-command','value'))
def add_value(value):
    if value=='Pause and Wait for Button Press':
        command = 1
    elif value=='Go to Absolute Position':
        command = 2
    elif value=='Move Relative Distance':
        command = 3
    else:
        command = 0

    new_command['MotionCommand'] = command
    print(new_command)

@callback(Input('setxpos','value'))
def add_value(value):
    new_command['SetXPosition'] = value

@callback(Input('setxvel','value'))
def add_value(value):
    new_command['SetXVelocity'] = value

@callback(Input('setypos','value'))
def add_value(value):
    new_command['SetYPosition'] = value

@callback(Input('setyvel','value'))
def add_value(value):
    new_command['SetYVelocity'] = value

@callback(Input('setzpos','value'))
def add_value(value):
    new_command['SetZPosition'] = value

@callback(Input('setzvel','value'))
def add_value(value):
    new_command['SetZVelocity'] = value

@callback(Input('setpause','value'))
def add_value(value):
    new_command['PauseTime'] = value

@callback(Input('comment','value'))
def add_value(value):
    new_command['Comment'] = value

@callback(Input('CMDDEL','n_clicks'),
          Input('CMDCLR','n_clicks'),
          Input('CMDREQLIST','n_clicks'))
def delete_task(bt1,bt2,bt3):
    new_ctr_struct = beckhoff_plc.data['MOTION/CTR_ECHO']
    del new_ctr_struct['timestamp']

    which_button = dash.ctx.triggered_id

    new_ctr_struct[which_button] = True
    # Convert the Dict to a properly JSON formatted string
    json_ctr = json.dumps(new_ctr_struct)

    # Publicsh the JSON to the "MOTION/CTR" topic over MQTT
    beckhoff_plc.client.publish(topic='MOTION/CTR',payload=json_ctr)

