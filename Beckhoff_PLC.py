import MQTT_Client
import time
from credentials import mqtt_broker_address, mqtt_broker_port

beckhoff_plc = MQTT_Client.mqtt_client(mqtt_broker_address,mqtt_broker_port,subscriptions=['MOTION/#'])


if __name__=='__main__':
    import time
    try:
        while True:
            print(beckhoff_plc.data.keys())
            time.sleep(1)
    
    except KeyboardInterrupt:
        print('Stopping')
        beckhoff_plc.client.loop_stop()
        beckhoff_plc.client.disconnect()