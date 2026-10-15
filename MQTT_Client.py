import paho.mqtt.client as mqtt
import json
import numpy as np
import datetime
import pandas as pd
import threading

class mqtt_client():
    def __init__(self,broker_address,broker_port,subscriptions):
        self.client = mqtt.Client(mqtt.CallbackAPIVersion.VERSION2)
        self.client.on_message = self.on_message
        try:
            self.client.connect(broker_address,broker_port,60)
        except Exception as e:
            print('\nError Connecting to MQTT Broker! Fatal Error. Closing GUI.\n\n')
            raise e
        
        for sub in subscriptions:
            self.client.subscribe(sub)

        self.client.loop_start()

        self.data = {}
        self.scan_data = {}

        self.time_of_last_status = 'No Data Recieved Yet'
        self.counter = 0

        self.script = pd.DataFrame(columns=['MotionCommand','SetXPosition','SetXVelocity','SetXAccel','SetYPosition','SetYVelocity','SetYAccel','SetZPosition','SetZVelocity','PauseTime','Comment','index'])
        self.time_of_last_script_receipt = datetime.datetime.now()
        self.last_index = 0

        self.files = []

    def on_message(self,client,userdata,msg):
        self.data[msg.topic] = {}
        # print(msg.topic)
        if msg.topic == 'MOTION/STATUS':
            self.time_of_last_message = datetime.datetime.now()

        msg_dict = json.loads(msg.payload.decode('utf-8'))
        self.data[msg.topic]['timestamp'] = datetime.datetime.now()
        for key in  list(msg_dict.keys()):
            self.data[msg.topic][key] = json.loads(msg.payload.decode('utf-8'))[key]

        time_since_last_scriptsend = datetime.datetime.now() - self.time_of_last_script_receipt

        if time_since_last_scriptsend.seconds >=1: # if its been more than 1 second since we have received 
            self.script = pd.DataFrame(columns=['MotionCommand','SetXPosition','SetXVelocity','SetXAccel','SetYPosition','SetYVelocity','SetYAccel','SetZPosition','SetZVelocity','PauseTime','Comment','index'])

        if msg.topic == 'MOTION/SCRIPTSEND':
            self.time_of_last_script_receipt = datetime.datetime.now()

            self.scriptsend_payload = json.loads(msg.payload.decode('utf-8'))

            self.script.loc[self.scriptsend_payload['index']] = list(self.scriptsend_payload.values())

            self.script = self.script.sort_values('index')

            if self.scriptsend_payload['index'] == 0:
                size_diff = len(self.script) - (self.last_index + 1)
                self.script.drop(self.script.tail(size_diff).index,inplace=True)

            self.last_index = self.scriptsend_payload['index']

        if msg.topic == 'MOTION/SCRIPTNAMES':
            payload = json.loads(msg.payload.decode('utf-8'))

            if payload['start'] == True:
                self.files = []
                self.files.append(payload['payload'])
            else:
                self.files.append(payload['payload'])

            print(f"Files received: {self.files}")

            