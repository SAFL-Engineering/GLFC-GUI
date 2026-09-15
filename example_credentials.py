import secrets

credentials = {'username':'password'}
token = secrets.token_urlsafe(32)

mqtt_broker_address = '127.0.0.1'
mqtt_broker_port = 1883