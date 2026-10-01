import dash
from dash import dcc, html, Input, Output, ALL, ctx, clientside_callback,callback,dash_table,no_update
import dash_daq as daq
from Beckhoff_PLC import beckhoff_plc
import json
import SAFL_Dash_Toolbox as safl
import pandas as pd

dash.register_page(__name__,) # Registering the page

pos_table_dict = {
    "Axis":["X","Y","Z"],
    "Basin Min":[0,0,0],
    "Position": [0,0,0],
    "Basin Max":[0,0,0],
    "Velocity": [0,0,0]
}
pos_table_df = pd.DataFrame(pos_table_dict) 

if beckhoff_plc.data['MOTION/CTR_ECHO']['AXESEN'] == True:
    lab = 'Disable Axes'
    col = "#00FF0D"
else:
    lab = 'Enable Axes'
    col = "#FF0000"



layout = html.Div(children=[
        html.Div(children=[
            html.Div(children=[
            safl.indicator_display(title='Axes Enabled',id='enabled-status'),
            dcc.Button("Enable/Disable",id='axes-enable-button'),
            html.Br(),
            html.Label('If motors have errors, click RESET to atempt to clear.'),
            dcc.Button("RESET All Axes", id='AXESRESET')
            ],className='divBorder'),

        ],className='divHorizontal'),
        html.Br(),
        html.Div(children=[
        html.Div(children=[
            html.H2(children='Homing Controls'),
            safl.indicator_display(title='All Axes Located/Homed',          id='axes-homed-label'      ),
            dcc.Button("Home X Axis",className='button',    id='CMDHOMEX'),
            dcc.Button("Home Y Axis",className='button',    id='CMDHOMEY'),
            dcc.Button("Home Z Axis",className='button',    id='CMDHOMEZ')
        ],className='divBorder'),
        html.Div(children=[
            html.H2(children='Manually Set Position'),
            dcc.Button(children=['Couple/Decouple X Motors'],id='CMDCOUPLE'),
            safl.indicator_display(title='X Motors Coupled',id='x-coupled-bool'),
            html.Div(children=[
                dcc.Input(type='number',debounce=False,step=0.1,id='POSX',value=0,persistence=True,persistence_type='local'),
                html.Label(id='xpos',style={'width':'150px','alignContent':'center','textAlign':'center','backgroundColor':'black','color':"#00FF15",'fontFamily':'Consolas','height':'40px','margin':'3px'}),
                dcc.Button("Set X Position",id='SETXPOS',className='button')
            ],className='divHorizontal'),
            html.Div(children=[
                dcc.Input(type='number',debounce=False,step=0.1,id='POSY',value=0,persistence=True,persistence_type='local'),
                html.Label(id='ypos',style={'width':'150px','alignContent':'center','textAlign':'center','backgroundColor':'black','color':"#00FF15",'fontFamily':'Consolas','height':'40px','margin':'3px'}),
                dcc.Button("Set Y Position",id='SETYPOS',className='button')
            ],className='divHorizontal'),
            html.Div(children=[
                dcc.Input(type='number',debounce=False,step=0.1,id='POSZ',value=0,persistence=True,persistence_type='local'),
                html.Label(id='zpos',style={'width':'150px','alignContent':'center','textAlign':'center','backgroundColor':'black','color':"#00FF15",'fontFamily':'Consolas','height':'40px','margin':'3px'}),
                dcc.Button("Set Z Position",id='SETZPOS',className='button')
            ],className='divHorizontal')
        ],className='divBorder')

    ],className='divHorizontal'),
    html.Br(),
    html.Div([
    dash_table.DataTable(columns = [{"name": i, "id": i} for i in pos_table_df.columns], 
                                 data=pos_table_df.to_dict('records'), 
                                 id='pos-vel-extents-table',
                                 style_table={
                                     'maxWidth':'650px'
                                 },
                                 style_cell={
                                     'fontFamily':'Arial, sans-serif',
                                     'textAlign':'center',
                                     'minWidth':'100px'
                                 },
                                 style_header={
                                     'fontWeight': 'bold'
                                 },
                                 style_data={'pointer-events':'none'})],className='divHorizontal'),
    html.Br(),
    dcc.Graph(id='current-xy-pos',className='plots')
])

@callback(Output('x-coupled-bool','color'),
          Output('axes-homed-label'   ,'color'),
          Input('interval-timer','n_intervals'),
          prevent_initial_call =True)
def update_homing(n):

    return safl.update_indicator_color(beckhoff_plc.data['MOTION/STATUS']['xCoupled'],"#DA2020","#9B9B9B"),\
           safl.update_indicator_color(beckhoff_plc.data['MOTION/STATUS']['AxesLocated'],"#DA2020","#9B9B9B")

@callback(Output('pos-vel-extents-table','data'),
          Output('axes-enable-button','children'),
          Input('interval-timer','n_intervals'),
          prevent_initial_call = True)
def update_table(n):
    data = beckhoff_plc.data['MOTION/STATUS']

    if beckhoff_plc.data['MOTION/CTR_ECHO']['AXESEN']:
        button_text =  'Disable Axes'
    else:
        button_text =  'Enable Axes'
    
    return  [{'Axis':'X','Position':f"{data['xPosOut']:.1f} mm",'Basin Min':f"{data['basinxMin']:.1f} mm",'Velocity':f"{data['xVelOut']:.1f} mm/s",'Basin Max':f"{data['basinxMax']:.1f} mm"},\
                        {'Axis':'Y','Position':f"{data['yPosOut']:.1f} mm",'Basin Min':f"{data['basinyMin']:.1f} mm",'Velocity':f"{data['yVelOut']:.1f} mm/s",'Basin Max':f"{data['basinyMax']:.1f} mm"},\
                        {'Axis':'Z','Position':f"{data['zPosOut']:.1f} mm",'Basin Min':f"{0:.1f} mm",'Velocity':f"{data['zVelOut']:.1f} mm/s",'Basin Max':f"{data['HardStopLocations'][2]:.1f} mm"}],\
                        button_text




@callback(Input('AXESRESET','n_clicks'),
          Input('CMDHOMEX','n_clicks'),
          Input('CMDHOMEY','n_clicks'),
          Input('CMDHOMEZ','n_clicks'),
          Input('CMDCOUPLE','n_clicks'),)
def actions(bt1,bt2,bt3,bt4,bt5):
    new_ctr_struct = beckhoff_plc.data['MOTION/CTR_ECHO'].copy()
    try:
        del new_ctr_struct['timestamp']
    except:
        pass
    
    which_button = dash.ctx.triggered_id

    if which_button == 'CMDCOUPLE': # CMD Couple toggles boolean value. 
        new_ctr_struct['CMDCOUPLE'] =  not new_ctr_struct['CMDCOUPLE']
    else:
        new_ctr_struct[which_button] = True  # All other set to True and the PLC will set back to False.
        # Convert the Dict to a properly JSON formatted string
    json_ctr = json.dumps(new_ctr_struct)

    # Publicsh the JSON to the "MOTION/CTR" topic over MQTT
    beckhoff_plc.client.publish(topic='MOTION/CTR',payload=json_ctr)

@callback(Output('POSX','value'),
          Output('POSY','value'),
          Output('POSZ','value'),
          Input('POSX','value'),
          Input('POSY','value'),
          Input('POSZ','value'),
          Input('SETXPOS','n_clicks'),
          Input('SETYPOS','n_clicks'),
          Input('SETZPOS','n_clicks')) 
def update_xyz_set(x,y,z,setx,sety,setz):
    new_ctr_struct = beckhoff_plc.data['MOTION/CTR_ECHO'].copy()
    try:
        del new_ctr_struct['timestamp']
    except:
        pass

    new_ctr_struct['POSX'] = float(x)
    new_ctr_struct['POSY'] = float(y)
    new_ctr_struct['POSZ'] = float(z)

    which_button = dash.ctx.triggered_id
    if which_button == 'SETXPOS':
        new_ctr_struct['SETXPOS'] = True
    elif which_button == 'SETYPOS':
        new_ctr_struct['SETYPOS'] = True
    elif which_button == 'SETZPOS':
        new_ctr_struct['SETZPOS'] = True

    json_ctr = json.dumps(new_ctr_struct)
        
    # Publicsh the JSON to the "MOTION/CTR" topic over MQTT
    beckhoff_plc.client.publish(topic='MOTION/CTR',payload=json_ctr)

    return x,y,z

@callback(Output('xpos','children'),
          Output('ypos','children'),
          Output('zpos','children'),
          Input('interval-timer','n_intervals'))
def update(n):
    return f'{beckhoff_plc.data['MOTION/STATUS']['xPosOut']:.1f}',\
           f'{beckhoff_plc.data['MOTION/STATUS']['yPosOut']:.1f}',\
           f'{beckhoff_plc.data['MOTION/STATUS']['zPosOut']:.1f}'


@callback(Output('enabled-status','color'),
          Input('interval-timer','n_intervals'))
def update_enabled_status_indicator(n):
    return safl.update_indicator_color(beckhoff_plc.data['MOTION/CTR_ECHO']['AXESEN'],"#7DDA20","#9B9B9B")

@callback(Input('axes-enable-button','n_clicks'))
def enable_disable_axes(n):
    beckhoff_plc.axes_enabled = not beckhoff_plc.axes_enabled

    new_ctr_struct = beckhoff_plc.data['MOTION/CTR_ECHO'].copy()
    try:
        del new_ctr_struct['timestamp']
    except:
        pass

    print(f"CTR_ECHO AXESEN':{new_ctr_struct['AXESEN']}")
    print(f"GUI Axes Enabled: {beckhoff_plc.axes_enabled}\n")
          
    
    if new_ctr_struct['AXESEN'] != beckhoff_plc.axes_enabled:
        new_ctr_struct['AXESEN'] = beckhoff_plc.axes_enabled
        print(f"Setting AXESEN to {beckhoff_plc.axes_enabled} and sending over MQTT")
        beckhoff_plc.client.publish(topic='MOTION/CTR',payload=json.dumps(new_ctr_struct))

    


    