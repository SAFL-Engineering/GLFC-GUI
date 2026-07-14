from dash import Dash, dcc, html, callback, Input, Output ,dash_table,ctx,State
import dash
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
            safl.value_display(title='Move Active',           id='moveactive-label'     ),
            safl.value_display(title='E Stop',                id='e-stop-label'         ),
            safl.value_display(title='Move Relative Error',   id='move-rel-err-label'   ),
            safl.value_display(title='Move Absolute Error',   id='move-abs-err-label'   ),
            safl.value_display(title='Power Error',           id='power-err-label'),
            safl.value_display(title='Halt Done',             id='halt-done-label'),
        ],className='divBorder'),
        html.Div(children=[
            html.H3('Configuration Status'),
            
            safl.value_display(title='Axes Located',          id='axes-located-label'      ),
            safl.value_display(title='Hard Stop Location',    id='hard-stop-loc-label'  ),
            safl.value_display(title='X Drives Coupled',      id='x-coupled-label'      ),
            safl.value_display(title='Basin Set Error',       id='basin-set-err-label')         

        ],className='divBorder'),

        html.Div(children=[
            html.H3('Script Status'),
            safl.value_display(title='Script Open Error',     id='script-open-err-label'),
            safl.value_display(title='Script Read Error',     id='script-read-err-label'),
            safl.value_display(title='Current Instruction',   id='curr-instr-label'     ),
            safl.value_display(title='Next Instruction',      id='next-instr-label'     ),
            safl.value_display(title='Run Index',             id='run-index-label'      )
            
        ],className='divBorder'),
    ]),
        html.Div(children=[
            html.H3('Current Position',style={'textAlign':'center'}),
            dcc.Graph(id='current-xy-pos',className='plots')
        ],className='divBorder')
    ],className='divHorizontal')


@callback(Output('moveactive-label','children'),
          Output('e-stop-label'         ,'children'),
          Output('move-rel-err-label'   ,'children'),
          Output('move-abs-err-label'   ,'children'),
          Output('power-err-label'   ,'children'),
          Output('halt-done-label'   ,'children'),
          Output('axes-located-label'      ,'children'),
          Output('hard-stop-loc-label'  ,'children'),
          Output('x-coupled-label'      ,'children'),
          Output('basin-set-err-label'      ,'children'),
          Output('script-open-err-label','children'),
          Output('script-read-err-label','children'),          
          Output('curr-instr-label'     ,'children'),
          Output('next-instr-label'     ,'children'),
          Output('run-index-label'      ,'children'),
          

        #   Output('stored_variables','data'),
          Input('interval-timer','n_intervals'),
          prevent_initial_call =True)
def update_status_display(n):

    return  safl.LED_Img_Off_Green(beckhoff_plc.data['MOTION/STATUS']['MoveActive']), \
            safl.LED_Img_Red_Green(beckhoff_plc.data['MOTION/STATUS']['eStop']), \
            safl.LED_Img_Off_Red(beckhoff_plc.data['MOTION/STATUS']['Move_Rel_Err']), \
            safl.LED_Img_Off_Red(beckhoff_plc.data['MOTION/STATUS']['Move_Abs_Err']), \
            safl.LED_Img_Off_Red(beckhoff_plc.data['MOTION/STATUS']['PowerError']), \
            safl.LED_Img_Off_Green(beckhoff_plc.data['MOTION/STATUS']['HaltDone']), \
            safl.LED_Img_Off_Green(beckhoff_plc.data['MOTION/STATUS']['AxesLocated']), \
            safl.LED_Img_Off_Green(beckhoff_plc.data['MOTION/STATUS']['HardStopLocations']),\
            safl.LED_Img_Off_Green(beckhoff_plc.data['MOTION/STATUS']['xCoupled']),\
            safl.LED_Img_Off_Red(beckhoff_plc.data['MOTION/STATUS']['Basin_Set_Err']),\
            safl.LED_Img_Off_Red(beckhoff_plc.data['MOTION/STATUS']['Script_Open_Err']), \
            safl.LED_Img_Off_Red(beckhoff_plc.data['MOTION/STATUS']['Script_Read_Err']), \
            f"{beckhoff_plc.data['MOTION/STATUS']['CurInstr']}", \
            f"{beckhoff_plc.data['MOTION/STATUS']['NextInstr']}", \
            f"{beckhoff_plc.data['MOTION/STATUS']['RUN_INDEX']}"               
    
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
