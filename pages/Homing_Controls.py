import dash
from dash import dcc, html, Input, Output, ALL, ctx, clientside_callback,callback,dash_table
from Beckhoff_PLC import beckhoff_plc
import json
import SAFL_Dash_Toolbox as safl
import pandas as pd

dash.register_page(__name__,) # Registering the page

pos_table_dict = {
    "Axis":["X","Y","Z"],
    "Basin Min":[0,0,0],
    "Position":[0,0,0],
    "Basin Max":[0,0,0],
    "Velocity":[0,0,0]
}
pos_table_df = pd.DataFrame(pos_table_dict) 

layout = html.Div(children=[
        html.Div(children=[
            dcc.Button("STOP All Axes",className='button',  id='AXESHALT'),
            dcc.Button("ENABLE All Axes",className='button',id='AXESEN'),
            dcc.Button("RESET All Axes",className='button', id='AXESRESET'),
        ],className='divHorizontal'),
        html.Br(),
        html.Div(children=[
        html.Div(children=[
            html.H2(children='Homing Controls'),
            dcc.Button("Home All Axes",className='button',  id='CMDHOME'),
            dcc.Button("Home X Axis",className='button',    id='CMDHOMEX'),
            dcc.Button("Home Y Axis",className='button',    id='CMDHOMEY'),
            dcc.Button("Home Z Axis",className='button',    id='CMDHOMEZ')
        ],className='divBorder'),
        html.Div(children=[
            html.H2(children='Manually Set Position'),
            dcc.Button(children=['Couple/Decouple X Motors'],id='CMDCOUPLE'),
            safl.indicator_display(title='X Motors Coupled',id='x-coupled-bool'),
            html.Div(children=[
                dcc.Input(type='number',debounce=True,step=0.1,id='POSX',value=0),
                dcc.Button("Set X Position",id='SETXPOS',className='button')
            ],className='divHorizontal'),
            html.Div(children=[
                dcc.Input(type='number',debounce=True,step=0.1,id='POSY',value=0),
                dcc.Button("Set Y Position",id='SETYPOS',className='button')
            ],className='divHorizontal'),
            html.Div(children=[
                dcc.Input(type='number',debounce=True,step=0.1,id='POSZ',value=0),
                dcc.Button("Set Z Position",id='SETZPOS',className='button')
            ],className='divHorizontal')
        ],className='divBorder')

    ],className='divHorizontal'),
    html.Br(),
    html.Div(children=[
        html.Div(children=[
                    html.Label("Currently Selected Basin: ",style={'fontWeight':'bold',"marginRight":"10px"}),
                    html.Label(id='current-basin-lbl')
                ],style={'display':'flex','flexdirection':'row'})],className='divHorizontal'),
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
          Input('interval-timer','n_intervals'),
          prevent_initial_call =True)
def update_homing(n):

    return safl.update_indicator_color(beckhoff_plc.data['MOTION/STATUS']['xCoupled'],"#DA2020","#9B9B9B")

@callback(Output('pos-vel-extents-table','data'),
          Output('current-basin-lbl','children'),
          Input('interval-timer','n_intervals'))
def update_table(n):
    data = beckhoff_plc.data['MOTION/STATUS']

    if beckhoff_plc.data['MOTION/CTR_ECHO']['BASINCTR'] == True:
        selected_basin = 'A',
    elif beckhoff_plc.data['MOTION/CTR_ECHO']['BASINCTR'] == False:
        selected_basin = 'B'
    else:
        selected_basin = 'Unknown'
    
    return  [{'Axis':'X','Position':f"{data['xPosOut']:.1f} mm",'Basin Min':f"{data['basinxMin']:.1f} mm",'Velocity':f"{data['xVelOut']:.1f} mm/s",'Basin Max':f"{data['basinxMax']:.1f} mm"},\
             {'Axis':'Y','Position':f"{data['yPosOut']:.1f} mm",'Basin Min':f"{data['basinyMin']:.1f} mm",'Velocity':f"{data['yVelOut']:.1f} mm/s",'Basin Max':f"{data['basinyMax']:.1f} mm"},\
             {'Axis':'Z','Position':f"{data['zPosOut']:.1f} mm",'Basin Min':f"{0:.1f} mm",'Velocity':f"{data['zVelOut']:.1f} mm/s",'Basin Max':f"{data['HardStopLocations'][2]:.1f} mm"}],\
             selected_basin

@callback(Input('AXESHALT','n_clicks'),
          Input('AXESEN','n_clicks'),
          Input('AXESRESET','n_clicks'),
          Input('CMDHOME','n_clicks'),
          Input('CMDHOMEX','n_clicks'),
          Input('CMDHOMEY','n_clicks'),
          Input('CMDHOMEZ','n_clicks'),
          Input('CMDCOUPLE','n_clicks'),
          Input('SETXPOS','n_clicks'),
          Input('SETYPOS','n_clicks'),
          Input('SETZPOS','n_clicks'))
def actions(bt1,bt2,bt3,bt4,bt5,bt6,bt7,bt8,bt9,bt10,bt11):
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

@callback(Input('POSX','value'),
          Input('POSY','value'),
          Input('POSZ','value'))
def update_xyz_set(x,y,z):
    new_ctr_struct = beckhoff_plc.data['MOTION/CTR_ECHO'].copy()
    try:
        del new_ctr_struct['timestamp']
    except:
        pass

    which_value = dash.ctx.triggered_id

    if which_value == 'POSX':
        new_ctr_struct['POSX'] = x
    elif which_value == 'POSY':
        new_ctr_struct['POSY'] = y
    elif which_value == 'POSZ':
        new_ctr_struct['POSZ'] = z

    json_ctr = json.dumps(new_ctr_struct)
        
    # Publicsh the JSON to the "MOTION/CTR" topic over MQTT
    beckhoff_plc.client.publish(topic='MOTION/CTR',payload=json_ctr)
