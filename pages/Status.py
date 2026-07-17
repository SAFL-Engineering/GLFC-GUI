from dash import Dash, dcc, html, callback, Input, Output ,dash_table,ctx,State
import dash
import dash_daq as daq
import plotly.graph_objects as go
from Beckhoff_PLC import beckhoff_plc
import SAFL_Dash_Toolbox as safl
import datetime
import pandas as pd


dash.register_page(__name__,path='/')

fig = go.Figure()
fig.add_trace(go.Scatter(x=[0],y=[0],name='current-xy'))
fig.update_xaxes(title_text='X (mm)',range=[-100,beckhoff_plc.data['MOTION/STATUS']["HardStopLocations"][0]+100])
fig.update_yaxes(scaleanchor='x',scaleratio=1,title_text='Y (mm)',range=[-100,beckhoff_plc.data['MOTION/STATUS']["HardStopLocations"][1]+100])

table_dict = {
    "Axis":["X","Y","Z"],
    "Position":[0,0,0],
    "Velocity":[0,0,0]
}
table_df = pd.DataFrame(table_dict)

extents_table_dict = {
    "Axis":['X','Y'],
    "Min":[0,0],
    "Max":[0,0]
}

extents_table_df = pd.DataFrame(extents_table_dict)

layout = html.Div(children= [
    html.Div(children=[        
        html.Div(children=[
            html.H3('Motion Status'),
            safl.indicator_display(title='Move Active',           id='moveactive-label'     ),
            safl.indicator_display(title='E Stop',                id='e-stop-label'         ),
            safl.indicator_display(title='Halt Done',             id='halt-done-label'),
            html.Br(),
            dash_table.DataTable(columns = [{"name": i, "id": i} for i in table_df.columns], 
                                 data=table_df.to_dict('records'), 
                                 id='pos-vel-table',
                                 style_table={
                                     'maxWidth':'450px'
                                 },
                                 style_cell={
                                     'fontFamily':'Arial, sans-serif',
                                     'textAlign':'center'
                                 },
                                 style_header={
                                     'fontWeight': 'bold'
                                 },
                                 style_data={'pointer-events':'none'})
        ],className='divBorder'),
        html.Div(children=[
            html.H3('Configuration Status'),
            safl.indicator_display(title='Axes Located',          id='axes-located-label'      ),
            safl.indicator_display(title='X Drives Coupled',      id='x-coupled-label'      )      

        ],className='divBorder'),

        html.Div(children=[
            html.H3('Script Status'),
            safl.indicator_display(title='Script Open Error',     id='script-open-err-label'),
            safl.indicator_display(title='Script Read Error',     id='script-read-err-label'),
            safl.value_display(title='Current Instruction',   id='curr-instr-label'     ),
            safl.value_display(title='Next Instruction',      id='next-instr-label'     ),
            safl.value_display(title='Run Index',             id='run-index-label'      )
            
        ],className='divBorder'),
    ]),
        html.Div(children=[
            html.H3('Current Position',style={'textAlign':'center'}),
            dcc.Graph(id='current-xy-pos',className='plots'),
            html.Br(),
            html.H3('Basin Extents'),
            html.Div(children=[
                html.Label("Currently Selected Basin: ",style={'fontWeight':'bold',"marginRight":"10px"}),
                html.Label(id='current-basin-label')
            ],style={'display':'flex','flexdirection':'row'}),
            html.Div(children=[
            dash_table.DataTable(columns = [{"name": i, "id": i} for i in extents_table_df.columns], 
                                 data=extents_table_df.to_dict('records'), 
                                 id='basin-extents-table',
                                 style_table={
                                     'maxWidth':'450px'
                                 },
                                 style_cell={
                                     'fontFamily':'Arial, sans-serif',
                                     'textAlign':'center'
                                 },
                                 style_header={
                                     'fontWeight': 'bold'
                                 },
                                 style_data={'pointer-events':'none'})
            ],className='grid-container')


        ],className='divBorder_75percWidth')
    ],style={'display':'flex','flexDirection':'row'})


@callback(Output('moveactive-label',     'color'),
          Output('e-stop-label'         ,'color'),
          Output('halt-done-label'      ,'color'),
          Output('axes-located-label'   ,'color'),
          Output('x-coupled-label'      ,'color'),
          Output('script-open-err-label','color'),
          Output('script-read-err-label','color'),          
          Output('curr-instr-label'     ,'children'),
          Output('next-instr-label'     ,'children'),
          Output('run-index-label'      ,'children'),
          Output('pos-vel-table','data'),
          Output('current-basin-label','children'),
          Output('basin-extents-table','data'),
        #   Output('stored_variables','data'),
          Input('interval-timer','n_intervals'),
          prevent_initial_call =True)
def update_status_display(n):

    if beckhoff_plc.data['MOTION/CTR_ECHO']['BASINCTR'] == True:
        selected_basin = 'A',
    elif beckhoff_plc.data['MOTION/CTR_ECHO']['BASINCTR'] == False:
        selected_basin = 'B'
    else:
        selected_basin = 'Unknown'

    return  safl.update_indicator_color(beckhoff_plc.data['MOTION/STATUS']['MoveActive']       ,"#DA2020","#9B9B9B"),\
            safl.update_indicator_color(beckhoff_plc.data['MOTION/STATUS']['eStop']            ,"#DA2020","#9B9B9B"), \
            safl.update_indicator_color(beckhoff_plc.data['MOTION/STATUS']['HaltDone']         ,"#DA2020","#9B9B9B"), \
            safl.update_indicator_color(beckhoff_plc.data['MOTION/STATUS']['AxesLocated']      ,"#DA2020","#9B9B9B"), \
            safl.update_indicator_color(beckhoff_plc.data['MOTION/STATUS']['xCoupled']         ,"#DA2020","#9B9B9B"),\
            safl.update_indicator_color(beckhoff_plc.data['MOTION/STATUS']['Script_Open_Err']  ,"#DA2020","#9B9B9B"), \
            safl.update_indicator_color(beckhoff_plc.data['MOTION/STATUS']['Script_Read_Err']  ,"#DA2020","#9B9B9B"), \
            f"{beckhoff_plc.data['MOTION/STATUS']['CurInstr']}", \
            f"{beckhoff_plc.data['MOTION/STATUS']['NextInstr']}", \
            f"{beckhoff_plc.data['MOTION/STATUS']['RUN_INDEX']}",\
            [{'Axis':'X','Position':f"{beckhoff_plc.data['MOTION/STATUS']['xPosOut']:.1f} mm",'Velocity':f"{beckhoff_plc.data['MOTION/STATUS']['xVelOut']:.1f} mm/s"},\
             {'Axis':'Y','Position':f"{beckhoff_plc.data['MOTION/STATUS']['yPosOut']:.1f} mm",'Velocity':f"{beckhoff_plc.data['MOTION/STATUS']['yVelOut']:.1f} mm/s"},\
             {'Axis':'Z','Position':f"{beckhoff_plc.data['MOTION/STATUS']['zPosOut']:.1f} mm",'Velocity':f"{beckhoff_plc.data['MOTION/STATUS']['zVelOut']:.1f} mm/s"}],\
            selected_basin,\
            [{'Axis':'X','Min':f"{beckhoff_plc.data['MOTION/STATUS']['basinxMin']:.1f} mm",'Max':f'{beckhoff_plc.data['MOTION/STATUS']['basinxMax']} mm'},\
             {'Axis':'Y','Min':f"{beckhoff_plc.data['MOTION/STATUS']['basinyMin']:.1f} mm",'Max':f'{beckhoff_plc.data['MOTION/STATUS']['basinyMax']} mm'}]
                         
    
@callback(Output('current-xy-pos','figure'),
          Input('interval-timer','n_intervals'))
def update_xy_pos_figure(n):
    fig.update_traces(x=[beckhoff_plc.data['MOTION/STATUS']['xPosOut']],y=[beckhoff_plc.data['MOTION/STATUS']['yPosOut']],selector={'name':'current-xy'})
    fig.layout.annotations = () # deletes existing annotations before adding new ones.
    fig.add_annotation(x=beckhoff_plc.data['MOTION/STATUS']['xPosOut'],y=beckhoff_plc.data['MOTION/STATUS']['yPosOut'],text=f'x={beckhoff_plc.data['MOTION/STATUS']['xPosOut']:.1f}mm<br>y={beckhoff_plc.data['MOTION/STATUS']['yPosOut']:.1f}mm')

    fig.layout.shapes = () # remove the shapes before we add more

    # Add the hardstops box
    fig.add_shape(
        type="rect",
        x0=0,  # Start x-coordinate
        y0=0,  # Start y-coordinate
        x1=beckhoff_plc.data['MOTION/STATUS']["HardStopLocations"][0],  # End x-coordinate
        y1=beckhoff_plc.data['MOTION/STATUS']["HardStopLocations"][1],  # End y-coordinate
        line=dict(
            color="Black",
            width=2,
        ),
        fillcolor="LightSkyBlue",
        opacity=0.5,
        layer="below" # Draw the shape behind the data points
    )

    # Draw an active basins box
    fig.add_shape(
        type="rect",
        x0=beckhoff_plc.data['MOTION/STATUS']['basinxMin'],
        y0=beckhoff_plc.data['MOTION/STATUS']['basinyMin'],
        x1=beckhoff_plc.data['MOTION/STATUS']['basinxMax'],
        y1=beckhoff_plc.data['MOTION/STATUS']['basinyMax'],
        line=dict(
            color="Black",
            width=2,
        ),
        fillcolor="#63FD77",
        opacity=0.5,
        layer="below" # Draw the shape behind the data points
    )

    fig.update_layout(margin=dict(t=0, b=0, l=0, r=0))

    return fig
