from dash import Dash, dcc, html, callback, Input, Output ,dash_table,ctx,State
import dash
from Beckhoff_PLC import beckhoff_plc
import SAFL_Dash_Toolbox as safl
import json
import pandas as pd


dash.register_page(__name__)

# time.sleep(1)

layout = html.Div(children=[
    # html.Div(id='ctr-echo-table',className='divBorder'),                
    html.Div(children=[
        html.H3('Add Instructions to Script'),
        html.Label('Select which Basin this Script should be run in:'),
        safl.value_display('Currently Selected Basin','scripting-page-selected-basin'),
        dcc.Button(id='BASINCTR',children='Toggle Selected Basin',persistence=True,persistence_type='local'),
        html.Br(),
        html.Label('Select a Command Type:'),
        dcc.Dropdown(options=['Null Instruction','Pause and Wait for Button Press','Go to Absolute Position','Move Relative Distance'],value='Go to Absolute Position',id='motion-command'),

        html.Div(children=[
            html.Div(children=[
                html.Label('Set X Target Position:'),
                dcc.Input(id='setxpos',type='number',debounce=True,step=0.1,value = 0)],style={'margin':'10px'}),
            html.Div(children=[
                html.Label('Set X Target Velocity:'),
                dcc.Input(id='setxvel',type='number',debounce=True,step=1,value=10)],style={'margin':'10px'}),
        ],className='divHorizontal'),

        html.Div(children=[
            html.Div(children=[
                html.Label('Set Y Target Position:'),
                dcc.Input(id='setypos',type='number',debounce=True,step=0.1,value = 0)],style={'margin':'10px'}),
            html.Div(children=[
                html.Label('Set Y Target Velocity:'),
                dcc.Input(id='setyvel',type='number',debounce=True,step=1,value=10)],style={'margin':'10px'}),
        ],className='divHorizontal'),
        
        html.Div(children=[
            html.Div(children=[
                html.Label('Set Z Target Position:'),
                dcc.Input(id='setzpos',type='number',debounce=True,step=0.1,value = 0)],style={'margin':'10px'}),
            html.Div(children=[
                html.Label('Set Z Target Velocity:'),
                dcc.Input(id='setzvel',type='number',debounce=True,step=1,value=10)],style={'margin':'10px'}),
        ],className='divHorizontal'),

        html.Label('Set Pause Time Before Next Move (milliseconds):'),
        dcc.Input(id='setpause',type='number',debounce=True,step=1,min=0,value=0),

        html.Label('Add a Comment for this instruction (optional)'),
        dcc.Input(id='comment',type='text',debounce=True,value=""),
        html.Br(),

        dcc.Button('Add Instruction to the Script',id='CMDADD',className='button'),
        dcc.Button('Delete the last task from the Script',id='CMDDEL',className='button'),
        dcc.Button('Clear the currently loaded Script',id='CMDCLR',className='button')
        
        
       
    ],className='divBorder'),
    html.Div(children=[
        html.Div(children = [
            html.H3('File Operations'),
            html.Label('Enter a Name for your Script (no spaces or < > : " / \\ | ? *):'),
            dcc.Input(id='script-name-input',type='text',debounce=True),
            dcc.Button('Save Script to File on PLC',id='CMDSCRIPTWRITE',className='button'),
            html.Br(),
            dcc.Button('Request List of Script Files from PLC',id='CMDREQLIST',className='button'),
            dcc.Dropdown(id="script-list"),
            html.Br(),
            html.Label('Currently Selected Script:',id='active-script-1'),
            dcc.Button('Set Selected Script as Active',id='CMDSCRIPTREAD',className='button'),
            dcc.Button('View Contents of Selected Script',id='CMDREQSCRIPT',className='button'),
            dcc.Button('Delete Currently Selected Script',id='CMDSCRIPTDEL',className='button')
        ],className='divBorder'),
        html.Div(children=[
            html.H3('Run Script'),
            html.Label('Currently Active Script:',id='active-script'),
            html.Br(),
            html.Div(children=[
                dcc.Checklist(options=['Loop Script Indefinitely'],id='CMDLOOP'),
            ],className='divHorizontal'),
            html.Div(children=[html.B('OR')],className='divHorizontal'),
            html.Label('Specify Many Times to Repeat this Script:'),
            dcc.Input(id='SCRIPTITERATIONS',type='number',min=1),
            html.Br(),
            dcc.Button('Run Active Script',id='CMDRUN',className='button')
        ],className='divBorder')
    ])
],className='divHorizontal')

@callback(Output('active-script','children'),
          Output('active-script-1','children'),
          Input('interval-timer','n_intervals'))
def update_active_script_label(n):
    script_name = beckhoff_plc.data['MOTION/CTR_ECHO']['SCRIPTNAME']
    label = 'Currently Selected Script:  ' 
    new = html.Div(children= [
        html.B(label),
        html.Div(script_name,style={'margin-left':'5px'})
    ],style={
        'display':'flex',
        'flexdirection':'row',
        'backgroundColor':"#C7C5C5",
        'borderRadius':'2px',
        'padding':'2px'
    })

    new2 = html.Div(children= [
            html.B('Currently Active Script:  '),
            html.Div(script_name,style={'margin-left':'5px'})
        ],style={
            'display':'flex',
            'flexdirection':'row',
            'backgroundColor':"#C7C5C5",
            'borderRadius':'2px',
            'padding':'2px'
        })
    return new2, new


@callback(Input('script-name-input','value'))
def update_script_name(value):
    # Start with the current Control Struct Echo
    new_ctr_struct = beckhoff_plc.data['MOTION/CTR_ECHO'].copy()
    try:
        del new_ctr_struct['timestamp']
    except:
        pass
    #change the value in the struct for scriptname
    new_ctr_struct['SCRIPTNAME'] = value
    # new_ctr_struct = {'CTR':new_ctr_struct}
    # Convert the Dict to a properly JSON formatted string
    json_ctr = json.dumps(new_ctr_struct)

    # Publicsh the JSON to the "MOTION/CTR" topic over MQTT
    beckhoff_plc.client.publish(topic='MOTION/CTR',payload=json_ctr)


@callback(Input('motion-command','value'),
          Input('setxpos','value'),
          Input('setxvel','value'),
          Input('setypos','value'),
          Input('setyvel','value'),
          Input('setzpos','value'),
          Input('setzvel','value'),
          Input('setpause','value'),
          Input('comment','value'))
def add_instr(motion_command,setxpos,setxvel,setypos,setyvel,setzpos,setzvel,setpause,comment):
    
    # Build the INSTR Structure to send the CMDADD command
    new_instr_struct = beckhoff_plc.data['MOTION/INSTR_ECHO'].copy()
    try:
        del new_instr_struct['timestamp']
    except:
        pass

    if motion_command=='Pause and Wait for Button Press':
        command = 1
    elif motion_command=='Go to Absolute Position':
        command = 2
    elif motion_command=='Move Relative Distance':
        command = 3
    else:
        command = 0

    new_instr_struct['MotionCommand'] = command

    new_instr_struct['SetXPosition']= setxpos
    new_instr_struct['SetXVelocity']= setxvel
    new_instr_struct['SetYPosition']= setypos
    new_instr_struct['SetYVelocity']= setyvel
    new_instr_struct['SetZPosition']= setzpos
    new_instr_struct['SetZVelocity']= setzvel
    new_instr_struct['PauseTime']   = setpause
    new_instr_struct['Comment'] = comment

    # Send the json array with the new command 
    beckhoff_plc.client.publish(topic='MOTION/INSTR',payload=json.dumps(new_instr_struct))

@callback(Input('CMDADD','n_clicks'))
def send_CMDADD(n):
    new_command = beckhoff_plc.data['MOTION/INSTR_ECHO']
    del new_command['timestamp']
    # Send the json array with the new command 
    beckhoff_plc.client.publish(topic='MOTION/INSTR',payload=json.dumps(new_command))

    # Build the CTR Structure to send the CMDADD command
    new_ctr_struct = beckhoff_plc.data['MOTION/CTR_ECHO'].copy()
    try:
        del new_ctr_struct['timestamp']
    except:
        pass

    new_ctr_struct['CMDADD'] = True
    # Convert the Dict to a properly JSON formatted string
    json_ctr = json.dumps(new_ctr_struct)

    # Publicsh the JSON to the "MOTION/CTR" topic over MQTT
    beckhoff_plc.client.publish(topic='MOTION/CTR',payload=json_ctr)



@callback(Input("BASINCTR","n_clicks"))
def set_basin(n):
        # Build the CTR Structure to send the CMDADD command
    new_ctr_struct = beckhoff_plc.data['MOTION/CTR_ECHO'].copy()
    try:
        del new_ctr_struct['timestamp']
    except:
        pass

    command = not new_ctr_struct['BASINCTR']

    new_ctr_struct['BASINCTR'] = command
    beckhoff_plc.client.publish(topic='MOTION/CTR',payload=json.dumps(new_ctr_struct))

@callback(Input("CMDLOOP",'value'))
def loop(val):

            # Build the CTR Structure to send the CMDADD command
    new_ctr_struct = beckhoff_plc.data['MOTION/CTR_ECHO'].copy()
    try:
        del new_ctr_struct['timestamp']
    except:
        pass

    if len(val) > 0:
        new_ctr_struct['CMDLOOP'] = True
    else:
        new_ctr_struct['CMDLOOP'] = False

    beckhoff_plc.client.publish(topic='MOTION/CTR',payload=json.dumps(new_ctr_struct))


@callback(Input('CMDDEL','n_clicks'),
          Input('CMDCLR','n_clicks'),
          Input('CMDREQLIST','n_clicks'),
          Input('CMDSCRIPTWRITE','n_clicks'),
          Input("CMDSCRIPTDEL",'n_clicks'),
          Input("CMDSCRIPTREAD","n_clicks"),
          Input("CMDREQSCRIPT","n_clicks"),
          Input("CMDRUN","n_clicks"))
def delete_task(bt1,bt2,bt3,bt4,bt5,bt6,bt7,bt8):
    new_ctr_struct = beckhoff_plc.data['MOTION/CTR_ECHO'].copy()
    try:
        del new_ctr_struct['timestamp']
    except:
        pass

    which_button = dash.ctx.triggered_id

    new_ctr_struct[which_button] = True
    # Convert the Dict to a properly JSON formatted string
    json_ctr = json.dumps(new_ctr_struct)

    # Publicsh the JSON to the "MOTION/CTR" topic over MQTT
    beckhoff_plc.client.publish(topic='MOTION/CTR',payload=json_ctr)

@callback(Input("SCRIPTITERATIONS","value"))
def update_script_iterations(val):
    new_ctr_struct = beckhoff_plc.data['MOTION/CTR_ECHO'].copy()
    try:
        del new_ctr_struct['timestamp']
    except:
        pass

    new_ctr_struct['SCRIPTITERATIONS'] = val

    beckhoff_plc.client.publish(topic='MOTION/CTR',payload=json.dumps(new_ctr_struct))

@callback(Output('scripting-page-selected-basin','children'),
          Input('interval-timer','n_intervals'))
def update_active_basin(n):
    which_basin = beckhoff_plc.data['MOTION/CTR_ECHO']['BASINCTR']
    
    if which_basin == True:
        return  "A"
    elif which_basin == False:
        return "B"
    else: 
        return "Unknown"