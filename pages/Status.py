from dash import Dash, dcc, html, callback, Input, Output ,dash_table,ctx,State
import dash
import dash_daq as daq
import plotly.graph_objects as go
from Beckhoff_PLC import beckhoff_plc
import SAFL_Dash_Toolbox as safl
import datetime


dash.register_page(__name__)

fig = go.Figure()
fig.add_trace(go.Scatter(x=[0],y=[0],name='current-xy'))
fig.update_xaxes(title_text='X (mm)',range=[-100,beckhoff_plc.data['MOTION/STATUS']["HardStopLocations"][0]+100])
fig.update_yaxes(scaleanchor='x',scaleratio=1,title_text='Y (mm)',range=[-100,beckhoff_plc.data['MOTION/STATUS']["HardStopLocations"][1]+100])

layout = html.Div(children= [
    html.Div(children=[        
        html.Div(children=[
            html.H3('Motion Status'),
            safl.indicator_display(title='Move Active',           id='moveactive-label'     ),
            safl.indicator_display(title='E Stop',                id='e-stop-label'         ),
            safl.indicator_display(title='Move Relative Error',   id='move-rel-err-label'   ),
            safl.indicator_display(title='Move Absolute Error',   id='move-abs-err-label'   ),
            safl.indicator_display(title='Power Error',           id='power-err-label'),
            safl.indicator_display(title='Halt Done',             id='halt-done-label'),
        ],className='divBorder'),
        html.Div(children=[
            html.H3('Configuration Status'),
            safl.indicator_display(title='Axes Located',          id='axes-located-label'      ),
            safl.indicator_display(title='Hard Stop Location',    id='hard-stop-loc-label'  ),
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
            html.Div(children=[
                safl.value_display(title='X Position',id='x-pos-label'),
                safl.value_display(title='X Velocity',id='x-vel-label')
            ],style={'display':'flex','flexdirection':'row','border':'1px solid black'}),
            html.Div(children=[
                safl.value_display(title='Y Position',id='y-pos-label'),
                safl.value_display(title='Y Velocity',id='y-vel-label')
            ],style={'display':'flex','flexdirection':'row','alignItems':'center'}),
            html.Div(children=[
                safl.value_display(title='Z Position',id='z-pos-label'),
                safl.value_display(title='Z Velocity',id='z-vel-label')
            ],style={'display':'flex','flexdirection':'row'})

        ],className='divBorder',style={'display':'flex','width':'75%'})
    ],style={'display':'flex','flexDirection':'row'})


@callback(Output('moveactive-label',     'color'),
          Output('e-stop-label'         ,'color'),
          Output('move-rel-err-label'   ,'color'),
          Output('move-abs-err-label'   ,'color'),
          Output('power-err-label'      ,'color'),
          Output('halt-done-label'      ,'color'),
          Output('axes-located-label'   ,'color'),
          Output('hard-stop-loc-label'  ,'color'),
          Output('x-coupled-label'      ,'color'),
          Output('script-open-err-label','color'),
          Output('script-read-err-label','color'),          
          Output('curr-instr-label'     ,'children'),
          Output('next-instr-label'     ,'children'),
          Output('run-index-label'      ,'children'),
          Output('x-pos-label','children'),
          Output('x-vel-label','children'),
          Output('y-pos-label','children'),
          Output('y-vel-label','children'),
          Output('z-pos-label','children'),
          Output('z-vel-label','children'),
        #   Output('stored_variables','data'),
          Input('interval-timer','n_intervals'),
          prevent_initial_call =True)
def update_status_display(n):

    return  safl.update_indicator_color(beckhoff_plc.data['MOTION/STATUS']['MoveActive']       ,"#DA2020","#9B9B9B"),\
            safl.update_indicator_color(beckhoff_plc.data['MOTION/STATUS']['eStop']            ,"#DA2020","#9B9B9B"), \
            safl.update_indicator_color(beckhoff_plc.data['MOTION/STATUS']['Move_Rel_Err']     ,"#DA2020","#9B9B9B"), \
            safl.update_indicator_color(beckhoff_plc.data['MOTION/STATUS']['Move_Abs_Err']     ,"#DA2020","#9B9B9B"), \
            safl.update_indicator_color(beckhoff_plc.data['MOTION/STATUS']['PowerError']       ,"#DA2020","#9B9B9B"), \
            safl.update_indicator_color(beckhoff_plc.data['MOTION/STATUS']['HaltDone']         ,"#DA2020","#9B9B9B"), \
            safl.update_indicator_color(beckhoff_plc.data['MOTION/STATUS']['AxesLocated']      ,"#DA2020","#9B9B9B"), \
            safl.update_indicator_color(beckhoff_plc.data['MOTION/STATUS']['HardStopLocations'],"#DA2020","#9B9B9B"),\
            safl.update_indicator_color(beckhoff_plc.data['MOTION/STATUS']['xCoupled']         ,"#DA2020","#9B9B9B"),\
            safl.update_indicator_color(beckhoff_plc.data['MOTION/STATUS']['Script_Open_Err']  ,"#DA2020","#9B9B9B"), \
            safl.update_indicator_color(beckhoff_plc.data['MOTION/STATUS']['Script_Read_Err']  ,"#DA2020","#9B9B9B"), \
            f"{beckhoff_plc.data['MOTION/STATUS']['CurInstr']}", \
            f"{beckhoff_plc.data['MOTION/STATUS']['NextInstr']}", \
            f"{beckhoff_plc.data['MOTION/STATUS']['RUN_INDEX']}",\
            f"{beckhoff_plc.data['MOTION/STATUS']['xPosOut']} mm",\
            f"{beckhoff_plc.data['MOTION/STATUS']['xVelOut']} mm/s",\
            f"{beckhoff_plc.data['MOTION/STATUS']['yPosOut']} mm",\
            f"{beckhoff_plc.data['MOTION/STATUS']['yVelOut']} mm/s",\
            f"{beckhoff_plc.data['MOTION/STATUS']['zPosOut']} mm",\
            f"{beckhoff_plc.data['MOTION/STATUS']['zVelOut']} mm/s",\
                         
    
@callback(Output('current-xy-pos','figure'),
          Input('interval-timer','n_intervals'))
def update_xy_pos_figure(n):
    fig.update_traces(x=[beckhoff_plc.data['MOTION/STATUS']['xPosOut']],y=[beckhoff_plc.data['MOTION/STATUS']['yPosOut']],selector={'name':'current-xy'})
    fig.layout.annotations = () # deletes existing annotations before adding new ones.
    fig.add_annotation(x=beckhoff_plc.data['MOTION/STATUS']['xPosOut'],y=beckhoff_plc.data['MOTION/STATUS']['yPosOut'],text=f'x={beckhoff_plc.data['MOTION/STATUS']['xPosOut']:.1f}mm<br>y={beckhoff_plc.data['MOTION/STATUS']['yPosOut']:.1f}mm')

    fig.layout.shapes = () # remove the shapes before we add more
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

    fig.update_layout(margin=dict(t=0, b=0, l=0, r=0))

    return fig
