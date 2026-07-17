import dash
from dash import dcc, html, Input, Output, ALL, ctx, clientside_callback,callback
from Beckhoff_PLC import beckhoff_plc
import json
import SAFL_Dash_Toolbox as safl

dash.register_page(__name__,) # Registering the page

layout = html.Div(children=[
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
            dcc.Input(type='number',debounce=True),
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

],className='divHorizontal')

@callback(Output('x-coupled-bool','color'),
          Input('interval-timer','n_intervals'),
          prevent_initial_call =True)
def update_homing(n):

    return safl.update_indicator_color(beckhoff_plc.data['MOTION/STATUS']['xCoupled']         ,"#DA2020","#9B9B9B")