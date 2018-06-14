#!/usr/bin/python3
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

if status == "RUNNING":
    print("Channel is already running. Exiting ...")
    sys.exit(0)

if status == "CREATING":
    print("Channel is being created. Exiting ...")
    sys.exit(0)

if status == "STOPPING":
    print("Channel is being stopped. Exiting ...")
    sys.exit(0)

channel = Channel_settings(input_key, data['channel_id'], data['medialive_id'],
          data['user_id'], data['name'], data['fps'], data['input_bitrate'],
          data['input_resolution'], status, config.medialive, config.dynamodb)

'''Create response array and append return value from channel_details() method '''
item = []
item.append(channel.get_item())
all_outputs = channel.output_settings()
for n in all_outputs:
    bitrate_item = channel.set_medialive_bitrates\
    (all_outputs[n][0], all_outputs[n][2])
    resolution_item = channel.set_medialive_resolutions\
    (all_outputs[n][0], all_outputs[n][1], all_outputs[n][2])
    audio_item = channel.set_medialive_audio\
    (all_outputs[n][1])
    item.append(bitrate_item)
    item.append(resolution_item)
    item.append(audio_item)

channel.video_1 = item[1]
channel.bitrate_1 = item[2]
channel.audio_1 = item[3]
channel.video_2 = item[4]
channel.bitrate_2 = item[5]
channel.audio_2 = item[6]
channel.video_3 = item[7]
channel.bitrate_3 = item[8]
channel.audio_3 = item[9]
channel.video_4 = item[10]
channel.bitrate_4 = item[11]
channel.audio_4 = item[12]

''' create input channel '''
print ("creating channel input ...")
channel.create_medialive_input(config.rtmp_url, config.input_sec_group)

''' create channel '''
print("creating channel ...")
channel.create_medialive_channel(config.livestream_output, config.livestream_record, \
config.arn)


''' start channel '''
print("channel is starting up ...")
channel.start_medialive_channel()
