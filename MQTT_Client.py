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

    def on_message(self,client,userdata,msg):
        self.data[msg.topic] = {}
        # print(msg.topic)
        self.time_of_last_message = datetime.datetime.now()

        msg_dict = json.loads(msg.payload.decode('utf-8'))
        self.data[msg.topic]['timestamp'] = datetime.datetime.now()
        for key in  list(msg_dict.keys()):
            self.data[msg.topic][key] = json.loads(msg.payload.decode('utf-8'))[key]

        if msg.topic == 'DAQ/DATA':
            with threading.Lock():
                if 'DATA_INDEX' in msg_dict.keys() and 'DATA_INDEX' in self.scan_data.keys():
                    if msg_dict['DATA_INDEX']<self.scan_data['DATA_INDEX'][-1]: # If the latest received DATA_INDEX is less than the last one already logged, then this must be a new scan.
                        self.scan_data = {} # Clear the scan_data array for a new one. 

                for key in  list(msg_dict.keys()):
                    if key not in self.scan_data:
                        self.scan_data[key] = [json.loads(msg.payload.decode('utf-8'))[key]]
                        
                    else:
                        self.scan_data[key].append(json.loads(msg.payload.decode('utf-8'))[key])

                # print(self.scan_data)



