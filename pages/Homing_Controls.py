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
            dcc.Button("STOP All Axes",className='button'),
            dcc.Button("ENABLE All Axes",className='button'),
            dcc.Button("RESET All Axes",className='button'),
        ],className='divHorizontal'),
        html.Br(),
        html.Div(children=[
        html.Div(children=[
            html.H2(children='Homing Controls'),
            dcc.Button("Home All Axes",id='home-all-button',className='button'),
            dcc.Button("Home X Axis",id='home-x-button',className='button'),
            dcc.Button("Home Y Axis",id='home-y-button',className='button'),
            dcc.Button("Home Z Axis",id='home-z-button',className='button')
        ],className='divBorder'),
        html.Div(children=[
            html.H2(children='Manually Set Position'),
            dcc.Button(children=['Couple/Decouple X Motors'],id='couple-decouple-button'),
            safl.indicator_display(title='X Motors Coupled',id='x-coupled-bool'),
            html.Div(children=[
                dcc.Input(type='number',debounce=True,min=0,max=100,step=0.01),
                dcc.Button("Set X Position",id='set-x-pos-button',className='button')
            ],className='divHorizontal'),
            html.Div(children=[
                dcc.Input(type='number',debounce=True),
                dcc.Button("Set Y Position",id='set-y-pos-button',className='button')
            ],className='divHorizontal'),
            html.Div(children=[
                dcc.Input(type='number',debounce=True),
                dcc.Button("Set Z Position",id='set-z-pos-button',className='button')
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

    return safl.update_indicator_color(beckhoff_plc.data['MOTION/STATUS']['xCoupled']         ,"#DA2020","#9B9B9B")

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