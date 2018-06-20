#!/usr/bin/python3
from config import Config
from resource import Channel_settings
from logger import Logger
# cli.py
from optparse import OptionParser
import sys

def create_channel(channel, status, config, log):
    if status == "RUNNING":
        log.log('ERROR', 'Channel already running. Exiting ...')
        sys.exit(0)

    if status == "CREATING":
        log.log('ERROR', 'Channel is being created. Exiting ...')
        sys.exit(0)

    if status == "STOPPING":
        log.log('Error', 'Channel is being stopped. Exiting ...')

        sys.exit(0)

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

    log.log('INFO', 'Creating channel input ...')
    channel.create_medialive_input(config.rtmp_url, config.input_sec_group)

    log.log('INFO', 'creating channel ...')
    channel.create_medialive_channel(config.livestream_output, config.livestream_record, \
    config.arn)

    log.log('INFO', 'Channel is starting up ...')
    channel.start_medialive_channel()

def  stop_channel(channel, status, config, log):
    if status == "STOPPING":
        log.log('ERROR', 'Channel is being stopped. Exiting ...')
        sys.exit(0)
    print("stopping channel")
    channel.stop_medialive_channel()

def main(streamkey, action):
    ''' init config, channel '''
    config = Config(streamkey)
    data = config.load_data()
    log = Logger(data['channel_id'], data['user_id'], config.dynamodb)
    # from channel logs load last status if empty load empty
    try:
        the_list = []
        for i in data['logs']:
            the_list.append(float(i))
        max_number = max(the_list)
        last = data['logs'][str(max_number)]
        status = last['Status']
    except:
        status = ''

    channel = Channel_settings(streamkey, data['channel_id'], data['medialive_id'],
              data['user_id'], data['name'], data['fps'], data['input_bitrate'],
              data['input_resolution'], status, config.medialive, config.dynamodb, log)

    if action == "create":
        create_channel(channel, status, config, log)

    elif action == "delete":
        stop_channel(channel, status, config, log)

    else:
        log.logs('ERROR', 'Wrong action specified')

if __name__ == "__main__":
    parser = OptionParser()

    parser.add_option(
        "-s", "--streamkey", dest="streamkey",
        help="Streamkey of Medialive channel")

    parser.add_option("-a", "--action", dest="action", help="function to call")

    (options, args) = parser.parse_args(sys.argv)

    main(options.streamkey, options.action)
