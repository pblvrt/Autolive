#!/usr/local/bin/python3.6
import sys
from models import Channel_settings
from config import Config

''' Get input streamkey '''
try:
    input_key=sys.argv[1]
except:
    print("please provide streamkey")
    sys.exit(0)

''' init config, channel '''
config = Config(input_key)
data = config.load_data()

try:
    the_list = []
    for i in data['logs']:
        the_list.append(float(i))
    max_number = max(the_list)
    last = data['logs'][str(max_number)]
    status = last['Status']
except:
    status = ''

channel = Channel_settings(input_key, data['channel_id'], data['medialive_id'],
          data['user_id'], data['name'], data['fps'], data['input_bitrate'],
          data['input_resolution'], status, config.medialive, config.dynamodb)

print("stopping channel")
channel.stop_medialive_channel()
