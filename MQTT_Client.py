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
        self.client.connect(broker_address,broker_port,60)
        for sub in subscriptions:
            self.client.subscribe(sub)

        self.client.loop_start()

        self.data = {}
        self.scan_data = {}

        self.time_of_last_status = 'No Data Recieved Yet'
        self.counter = 0

        self.script_array = []

    def on_message(self,client,userdata,msg):
        self.data[msg.topic] = {}
        # print(msg.topic)
        if msg.topic == 'MOTION/STATUS':
            self.time_of_last_message = datetime.datetime.now()

        msg_dict = json.loads(msg.payload.decode('utf-8'))
        self.data[msg.topic]['timestamp'] = datetime.datetime.now()
        for key in  list(msg_dict.keys()):
            self.data[msg.topic][key] = json.loads(msg.payload.decode('utf-8'))[key]

        if msg.topic == 'MOTION/SCRIPTSEND':
            self.scriptsend_payload = json.loads(msg.payload.decode('utf-8'))
     

            if self.scriptsend_payload['index'] == 0:
                self.script_array = []
                self.script_array.append(self.scriptsend_payload)

            else:
                self.script_array.append(self.scriptsend_payload)
                # print(self.script_array)



