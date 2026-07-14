import dash
from dash import dcc, html, Input, Output, ALL, ctx, clientside_callback,callback
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
    ], style={'display': 'inline-block'})

layout = html.Div([
    html.H3("Manual Jog Control"),
    html.Div(id='which-button-is-pressed', children="Stopped"),
    html.Div(children = [
    create_momentary_button(1, "Jog X-"),
    html.Label(id='current-x-pos',style={'width':'150px','alignContent':'center','textAlign':'center','backgroundColor':'black','color':"#00FF15",'fontFamily':'Consolas','height':'40px'}),
    create_momentary_button(2, "Jog X+")
    ],className='divHorizontal'),
    html.Div(children = [
    create_momentary_button(3, "Jog Y-"),
    html.Label(id='current-y-pos',style={'width':'150px','alignContent':'center','textAlign':'center','backgroundColor':'black','color':"#00FF15",'fontFamily':'Consolas','height':'40px'}),
    create_momentary_button(4, "Jog Y+")
    ],className='divHorizontal'),
    html.Div(children = [
    create_momentary_button(5, "Jog Z-"),
    html.Label(id='current-z-pos',style={'width':'150px','alignContent':'center','textAlign':'center','backgroundColor':'black','color':"#00FF15",'fontFamily':'Consolas','height':'40px'}),
    create_momentary_button(6, "Jog Z+")
    ],className='divHorizontal'),
    safl.value_display(title='X Range',            id='x-hardstops'),
    safl.value_display(title='Y Range',            id='y-hardstops'),
    safl.value_display(title='Z Range',            id='z-hardstops'),
    dcc.Graph(id='current-xy-pos',className='plots')
])

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
    print(f"Callback Triggered: {msg}") 


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
           Input('interval-timer','n_intervals')
           )
def update_position_displays(n):
    return  f"{beckhoff_plc.data['MOTION/STATUS']['xPosOut']:,.2f} mm",\
            f"{beckhoff_plc.data['MOTION/STATUS']['yPosOut']:,.2f} mm",\
            f"{beckhoff_plc.data['MOTION/STATUS']['zPosOut']:,.2f} mm",\
            f"{0} to {beckhoff_plc.data['MOTION/STATUS']["HardStopLocations"][0]:.1f} mm",\
            f"{0} to {beckhoff_plc.data['MOTION/STATUS']["HardStopLocations"][1]:.1f} mm",\
            f"{0} to {beckhoff_plc.data['MOTION/STATUS']["HardStopLocations"][2]:.1f} mm"