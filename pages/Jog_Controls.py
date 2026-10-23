import dash
from dash import dcc, html, Input, Output, ALL, ctx, clientside_callback,callback,no_update
from Beckhoff_PLC import beckhoff_plc
import json
import SAFL_Dash_Toolbox as safl

dash.register_page(__name__,) # Registering the page

def create_momentary_button(index, label):
    # (Same helper function as before)
    return html.Div([
        html.Button(
            label,
            id={'type': 'momentary-btn', 'index': index}, 
            className="momentary-btn",
            style={'margin': '10px', 'padding': '10px 20px', 'user-select': 'none'}
        ),
        dcc.Store(id={'type': 'button-state', 'index': index}, data="released"),
    ], style={'display': 'inline-block'},id=label)

def add_warning_to_button(index,label):
    return html.Div([
        dcc.ConfirmDialogProvider([
        html.Button(
            label, 
            id={'type': 'momentary-btn', 'index': index}, 
            className="momentary-btn",
            style={'margin': '10px', 'padding': '10px 20px', 'user-select': 'none'}
            )]),
            dcc.Store(id={'type': 'button-state', 'index': index}, data="released"),
        ], style={'display': 'inline-block'},id=label)

layout = html.Div([
    dcc.Location(id='url-trigger', refresh=False),
    html.Div(children=[],id='confirm-dialog'),
    html.Div(children=[
        html.H3("Manual Jog Control"),
        html.Div(id='which-button-is-pressed', children="Stopped")
    ],className='divCenterItems'),
    html.Div(children=[
        safl.value_display(title='Currectly Selected Basin',id='jog-page-active-basin'),
    ],style={'display':'flex','flexDirection':'column','justifyContent':'center'}),
    html.Div(children=[
        dcc.Button(children='Toggle Selected Basin',id='jog-page-basin-toggle',className='button')
    ],style={'display':'flex','justifyContent':'center'}),
    html.Div(children=[
        html.Label('X-motors are NOT Coupled. Click Below to allow jogging on enclosure side x motor only.'),
        dcc.Checklist(options=['Allow X motion on enclosure side motor only'],id='x-override')
        ], id='x-motors-coupled',
        style={'display':'flex','justifyContent':'center'}),
    html.Div(children = [
    create_momentary_button(1, "Jog X-"),
    html.Label(id='current-x-pos',style={'width':'150px','alignContent':'center','textAlign':'center','backgroundColor':'black','color':"#00FF15",'fontFamily':'Consolas','height':'40px'}),
    create_momentary_button(2, "Jog X+")
    ],className='divJogButtons'),
    html.Div(children = [
    create_momentary_button(3, "Jog Y-"),
    html.Label(id='current-y-pos',style={'width':'150px','alignContent':'center','textAlign':'center','backgroundColor':'black','color':"#00FF15",'fontFamily':'Consolas','height':'40px'}),
    create_momentary_button(4, "Jog Y+")
    ],className='divJogButtons'),
    html.Div(children = [
    create_momentary_button(5, "Jog Z-"),
    html.Label(id='current-z-pos',style={'width':'150px','alignContent':'center','textAlign':'center','backgroundColor':'black','color':"#00FF15",'fontFamily':'Consolas','height':'40px'}),
    create_momentary_button(6, "Jog Z+")
    ],className='divJogButtons'),
    safl.value_display(title='X Range',            id='x-hardstops'),
    safl.value_display(title='Y Range',            id='y-hardstops'),
    safl.value_display(title='Z Range',            id='z-hardstops'),
    html.Br(),
    html.Div(children=[
        html.Div(children=[
            html.Label('Drive X to Position:',style={'minWidth':100}),
            html.Div(children=[
                dcc.Input(type='number',debounce=False,step=0.1,id='POSX_move',value=beckhoff_plc.data['MOTION/CTR_ECHO']['POSX']),
            ],style={'display':'flex','minWidth':200,'margin':'5px'}),
            html.Div(id='X-target',className='divHorizontal'),
            dcc.Button('Go!',id='Go-X')
        ],className='divJogButtons'),
        html.Div(children=[
                    html.Label('Drive Y to Position:',style={'minWidth':100}),
                    html.Div(children=[
                        dcc.Input(type='number',debounce=False,step=0.1,id='POSY_move',value=beckhoff_plc.data['MOTION/CTR_ECHO']['POSY']),
                    ],style={'display':'flex','minWidth':200,'margin':'5px'}),
                    html.Div(id='Y-target',className='divHorizontal'),
                    dcc.Button('Go!',id='Go-Y')
                ],className='divJogButtons'),
        html.Div(children=[
                    html.Label('Drive Z to Position:',style={'minWidth':100}),
                    html.Div(children=[
                        dcc.Input(type='number',debounce=False,step=0.1,id='POSZ_move',value=beckhoff_plc.data['MOTION/CTR_ECHO']['POSZ']),
                    ],style={'display':'flex','minWidth':200,'margin':'5px'}),
                    html.Div(id='Z-target',className='divHorizontal'),
                    dcc.Button('Go!',id='Go-Z')
                ],className='divJogButtons')
    ],style={'display':'flex','flexDirection':'column','justifyContent':'center'}),

    html.Div(children=[
        dcc.Graph(id='current-xy-pos',className='plots')
    ])
],className='divOverall')

# Use clientside_callback directly (no "app." prefix)
clientside_callback(
    """
    function(ids) {
        if (!ids) return window.dash_clientside.no_update;
        if (!window.buttonStates) { window.buttonStates = {}; }

        ids.forEach(id => {
            const dashId = JSON.stringify(id, Object.keys(id).sort());
            const btn_element = document.getElementById(dashId);
            
            if (btn_element && !btn_element.getAttribute('data-listener-set')) {
                window.buttonStates[id.index] = "released";

                const setState = (newState) => {
                    if (window.buttonStates[id.index] !== newState) {
                        window.buttonStates[id.index] = newState;
                        dash_clientside.set_props(
                            {type: 'button-state', index: id.index}, 
                            {data: newState}
                        );
                    }
                };

                btn_element.addEventListener('mousedown', () => setState('pressed'));
                btn_element.addEventListener('mouseup', () => setState('released'));
                btn_element.addEventListener('mouseleave', () => setState('released'));
                
                btn_element.setAttribute('data-listener-set', 'true');
            }
        });
        return window.dash_clientside.no_update;
    }
    """,
    Output({'type': 'momentary-btn', 'index': ALL}, 'id'), 
    Input({'type': 'momentary-btn', 'index': ALL}, 'id')
)

# Standard python callback also uses dash.callback or @callback from dash
@callback(
    Output('which-button-is-pressed', 'children'),
    Input({'type': 'button-state', 'index': ALL}, 'data'),
    prevent_initial_call=True
)
def update_ui(states):
    pressed_indices = [
        item['id']['index'] 
        for item, state in zip(ctx.inputs_list[0], states) 
        if state == 'pressed'
    ]

    index_dict = {1:'Jogging X -',2:'Jogging X +',3:'Jogging Y -',4:'Jogging Y +',5:'Jogging Z -',6:'Jogging Z +'}

    if not pressed_indices:
        msg = "Stopped"
    else:
        # print(pressed_indices)
        msg = f"{index_dict[pressed_indices[0]]}"
    
    # This will now ONLY print when a button is actually pressed or released
    # print(f"Callback Triggered: {msg}") 


    new_ctr_struct = beckhoff_plc.data['MOTION/CTR_ECHO']
    if 'timestamp' in new_ctr_struct:
        del new_ctr_struct['timestamp']

    if not pressed_indices:
        new_ctr_struct['XJOGBW'] = False
        new_ctr_struct['XJOGFW'] = False
        new_ctr_struct['YJOGBW'] = False
        new_ctr_struct['YJOGFW'] = False
        new_ctr_struct['ZJOGBW'] = False
        new_ctr_struct['ZJOGFW'] = False
    else: 
        if pressed_indices[0] == 1:
            new_ctr_struct['XJOGBW'] = True
        elif pressed_indices[0] == 2:
            new_ctr_struct['XJOGFW'] = True
        elif pressed_indices[0] == 3:
            new_ctr_struct['YJOGBW'] = True
        elif pressed_indices[0] == 4:
            new_ctr_struct['YJOGFW'] = True
        elif pressed_indices[0] == 5:
            new_ctr_struct['ZJOGBW'] = True
        elif pressed_indices[0] == 6:
            new_ctr_struct['ZJOGFW'] = True
        else:
            new_ctr_struct['XJOGBW'] = False
            new_ctr_struct['XJOGFW'] = False
            new_ctr_struct['YJOGBW'] = False
            new_ctr_struct['YJOGFW'] = False
            new_ctr_struct['ZJOGBW'] = False
            new_ctr_struct['ZJOGFW'] = False

    # Convert the Dict to a properly JSON formatted string
    json_ctr = json.dumps(new_ctr_struct)

    # Publicsh the JSON to the "MOTION/CTR" topic over MQTT
    beckhoff_plc.client.publish(topic='MOTION/CTR',payload=json_ctr)

    return msg

@callback (Output('current-x-pos','children'),
           Output('current-y-pos','children'),
           Output('current-z-pos','children'),
           Output('x-hardstops',           'children'),
           Output('y-hardstops',           'children'),
           Output('z-hardstops',           'children'),
           Output('jog-page-active-basin','children'),
           Input('interval-timer','n_intervals')
           )
def update_position_displays(n):
    which_basin = beckhoff_plc.data['MOTION/STATUS']['basinstate']
        
    if which_basin == 0:
        basin= "A"
    elif which_basin == 1:
        basin= "B"
    else: 
        basin = "Unknown"

    if f"{beckhoff_plc.data['MOTION/STATUS']['xPosOut']:,.1f}" == "-999,999.0":
        x_pos = "Outside Basin Extents"
    else:
        x_pos = f"{beckhoff_plc.data['MOTION/STATUS']['xPosOut']:,.1f} mm"

    if f"{beckhoff_plc.data['MOTION/STATUS']['yPosOut']:,.1f}" == "-999,999.0":
        y_pos = "Outside Basin Extents"
    else:
        y_pos = f"{beckhoff_plc.data['MOTION/STATUS']['yPosOut']:,.1f} mm"

    if f"{beckhoff_plc.data['MOTION/STATUS']['zPosOut']:,.1f}" == "-999,999.0":
        z_pos = "Outside Basin Extents"
    else:
        z_pos = f"{beckhoff_plc.data['MOTION/STATUS']['zPosOut']:,.1f} mm"
    
    
    return  x_pos,\
            y_pos,\
            z_pos,\
            f"{beckhoff_plc.data['MOTION/STATUS']['CARRIAGE_OFFSETS'][0]:.1f} to {beckhoff_plc.data['MOTION/STATUS']["HardStopLocations"][0]:.1f} mm",\
            f"{beckhoff_plc.data['MOTION/STATUS']['basinyMin']:.1f} to {beckhoff_plc.data['MOTION/STATUS']['basinyMax']:.1f} mm",\
            f"{beckhoff_plc.data['MOTION/STATUS']['CARRIAGE_OFFSETS'][2]:.1f} to {beckhoff_plc.data['MOTION/STATUS']["HardStopLocations"][2]:.1f} mm",\
            basin

@callback(Input("jog-page-basin-toggle","n_clicks"))
def set_basin(n):
        # Build the CTR Structure to send the CMDADD command
    new_ctr_struct = beckhoff_plc.data['MOTION/CTR_ECHO'].copy()
    try:
        del new_ctr_struct['timestamp']
    except:
        pass

    command = True 

    new_ctr_struct['BASINCTR'] = command
    beckhoff_plc.client.publish(topic='MOTION/CTR',payload=json.dumps(new_ctr_struct))


@callback(Output({'type': 'momentary-btn', 'index': 2},'disabled'),
          Output({'type': 'momentary-btn', 'index': 1},'disabled'),
        #   Output('x-motors-coupled','children'),
          Output('x-motors-coupled','style'),
          Input('interval-timer','n_intervals'),
          Input('x-override','value'))
def add_confirm_dialog(n,override):
    # print(override)
    if beckhoff_plc.data['MOTION/STATUS']['xCoupled']:
        # print('motors are coupled')
        return False,False,{'display':'none'}

    elif override==['Allow X motion on enclosure side motor only']: 
        return False,False,{'display':'flex','justifyContent':'center','flexDirection':'column','alignItems': 'center'}
    
    else:
        # print('motors are un-coupled')

        return True,True,{'display':'flex','justifyContent':'center','flexDirection':'column','alignItems': 'center'}

@callback(Input('POSX_move','value'),
          Input('POSY_move','value'),
          Input('POSZ_move','value'))
def set_move_target(x,y,z):
    new_ctr_struct = beckhoff_plc.data['MOTION/CTR_ECHO'].copy()
    try:
        del new_ctr_struct['timestamp']
    except:
        pass
    if x is not None:
        new_ctr_struct['POSX'] = float(x)
    if y is not None:
        new_ctr_struct['POSY'] = float(y)
    if z is not None:
        new_ctr_struct['POSZ'] = float(z)

    # Publicsh the JSON to the "MOTION/CTR" topic over MQTT
    beckhoff_plc.client.publish(topic='MOTION/CTR',payload=json.dumps(new_ctr_struct))

@callback(Input('Go-X','n_clicks'),
          Input('Go-Y','n_clicks'),
          Input('Go-Z','n_clicks'))
def start_move(nx,ny,nz):
    new_ctr_struct = beckhoff_plc.data['MOTION/CTR_ECHO'].copy()
    try:
        del new_ctr_struct['timestamp']
    except:
        pass

    which_button = dash.ctx.triggered_id
    # Check that the target position is not the current position.  If it is, no move will occur when the button is pressed, BUT moition will occur as soon as a new target is entered.
    if which_button == 'Go-X' and f"{beckhoff_plc.data['MOTION/CTR_ECHO']['POSX']:.1f}" != f"{beckhoff_plc.data['MOTION/STATUS']['xPosOut']:.1f}":
        new_ctr_struct['MOVEX'] = True 
    elif which_button == 'Go-Y' and f"{beckhoff_plc.data['MOTION/CTR_ECHO']['POSY']:.1f}" != f"{beckhoff_plc.data['MOTION/STATUS']['yPosOut']:.1f}":
        new_ctr_struct['MOVEY'] = True
    elif which_button == 'Go-Z' and f"{beckhoff_plc.data['MOTION/CTR_ECHO']['POSZ']:.1f}" != f"{beckhoff_plc.data['MOTION/STATUS']['zPosOut']:.1f}":
        new_ctr_struct['MOVEZ'] = True

    # Publicsh the JSON to the "MOTION/CTR" topic over MQTT
    beckhoff_plc.client.publish(topic='MOTION/CTR',payload=json.dumps(new_ctr_struct))

@callback(Output('Go-X','disabled'),
          Output('Go-Y','disabled'),
          Output('Go-Z','disabled'),
          Input('interval-timer','n_intervals'))
def disable_buttons(n):

    if beckhoff_plc.data['MOTION/STATUS']['xPosOut'] == -999999 or beckhoff_plc.data['MOTION/STATUS']['yPosOut'] == -999999 or beckhoff_plc.data['MOTION/STATUS']['zPosOut'] == -999999:
        outside_basin = True
    else:
        outside_basin = False

    if beckhoff_plc.data['MOTION/STATUS']['MoveActive'] or outside_basin:
        return True,True,True
    else:
        return False,False,False

@callback(Output('POSX_move','min'),
          Output('POSX_move','max'),
          Output('POSY_move','min'),
          Output('POSY_move','max'),
          Output('POSZ_move','min'),
          Output('POSZ_move','max'),
          Output('X-target','children'),
          Output('Y-target','children'),
          Output('Z-target','children'),
          Input('interval-timer','n_intervals'))
def update_minmax(n):
    mins =  beckhoff_plc.data['MOTION/STATUS']['CARRIAGE_OFFSETS']
    maxs = beckhoff_plc.data['MOTION/STATUS']['HardStopLocations']

    x_target_div = [html.Label('X Target: ',style={'padding':'2px'}),
                    html.Label(f"{beckhoff_plc.data['MOTION/CTR_ECHO']['POSX']:,.1f} mm",style={'padding':'2px'})]
    y_target_div = [html.Label('Y Target: ',style={'padding':'2px'}),
                        html.Label(f"{beckhoff_plc.data['MOTION/CTR_ECHO']['POSY']:,.1f} mm",style={'padding':'2px'})]
    z_target_div = [html.Label('Z Target: ',style={'padding':'2px'}),
                        html.Label(f"{beckhoff_plc.data['MOTION/CTR_ECHO']['POSZ']:,.1f} mm",style={'padding':'2px'})]

    return mins[0]+1,\
            beckhoff_plc.data['MOTION/STATUS']['basinxMax']-1,\
            beckhoff_plc.data['MOTION/STATUS']['basinyMin']+1,\
            beckhoff_plc.data['MOTION/STATUS']['basinyMax']-1,\
            mins[2]+1,\
            maxs[2]-1,\
            x_target_div,\
            y_target_div,\
            z_target_div

@callback(Output('POSX_move','value'),
          Output('POSY_move','value'),
          Output('POSZ_move','value'),
          Input('url-trigger','pathname'))
def update_targets(path):
    print(f"Pathname : {path}")
    if path == '/jog-controls':
        print('Updating Input Values')
        return  beckhoff_plc.data['MOTION/CTR_ECHO']['POSX'],\
                beckhoff_plc.data['MOTION/CTR_ECHO']['POSY'],\
                beckhoff_plc.data['MOTION/CTR_ECHO']['POSZ']
    else:
        return no_update