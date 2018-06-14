from datetime import datetime
import random, string, os, json, time, decimal, sys
from collections import OrderedDict

class Channel_settings:
    def __init__(self, streamkey, channel_id, medialive_id, user_id, channel_name, \
                fps, input_bitrate, input_resolution, status, \
                medialive, dynamodb):
        ''' Set output video and audio resolutions depending on input VIDEO
        resolution specified.
        Set the bitrate for each output depending on input bitrate specified.
        All bitrates available:
        ["10000k", "9000k", "8000k", "7000k", "5000k", "4000k",
        "3500k", "3000k", "2000k", "1500k", "750k" '''

        self.medialive_id = medialive_id
        self.channel_id = channel_id
        self.user_id = user_id
        self.input_id = input_id
        self.channel_name = channel_name
        self.fps = int(fps)
        self.input_resolution = input_resolution
        self.input_bitrate = input_bitrate
        self.streamkey = streamkey
        self.status = status
        self.medialive = medialive
        self.dynamodb = dynamodb
        self.video_1 = None
        self.video_2 = None
        self.video_3 = None
        self.video_4 = None
        self.audio_1 = None
        self.audio_2 = None
        self.audio_3 = None
        self.audio_4 = None
        self.bitrate_1 = None
        self.bitrate_2 = None
        self.bitrate_3 = None
        self.bitrate_4 = None
        self.init_settings()

    def log(self, status, message):
        item = {'logs': {
                    'Message': message,
                    'Status': status,
                    'Source': 'NGINX',
                    'Pipleine': 'Main'
                    },
                }
        self.status=status
        try:
            response = self.dynamodb.update_item(
                Key = {'channel_id': self.channel_id,
                       'user_id': self.user_id},
                UpdateExpression='SET logs.#k1 = :logs',
                ExpressionAttributeNames= {'#k1': str(time.time()*1000)},
                ExpressionAttributeValues={':logs': item['logs']})
            return response

        except Exception as e:
            print(e)
            if e.response['Error']['Code'] == 'ValidationException':
                response = self.dynamodb.update_item(
                    Key = {'channel_id': self.channel_id,
                           'user_id': self.user_id},
                    UpdateExpression='SET #attr = :logs',
                    ExpressionAttributeNames={'#attr': 'logs'},
                    ExpressionAttributeValues={
                    ':logs':{
                        str(time.time()*1000): item['logs']}}
                )
            return response

    def get_item(self):
        item = {
            'channel_id': self.channel_id,
            'user_id': self.user_id,
            'medialive_id': self.medialive_id,
            'name': self.channel_name,
            'fps': self.fps,
            'input_bitrate': self.input_bitrate,
            'input_resolution': self.input_resolution,
            'streamkey': self.streamkey,
            'createdAt': int(time.time() * 1000),
            'updatedAt': int(time.time() * 1000)
                }
        return item

    def init_settings(self):
        if self.input_resolution == "1080" and int(self.input_bitrate) <= 5000:
            self.video_1 = "1080_1"
            self.video_2 = "720_1"
            self.video_3 = "480_1"
            self.video_4 = "240_1"
            self.audio_1 = "Audio_high_1"
            self.audio_2 = "Audio_high_2"
            self.audio_3 = "Audio_low_1"
            self.audio_4 = "Audio_low_2"

        if self.input_resolution == "720":
            self.video_1 = "720_1"
            self.video_2 = "720_2"
            self.video_3 = "480_1"
            self.video_4 = "240_1"
            self.audio_1 = "Audio_high_1"
            self.audio_2 = "Audio_high_2"
            self.audio_3 = "Audio_low_1"
            self.audio_4 = "Audio_low_2"

        if self.input_bitrate == "1000":
            self.bitrate_1 = "1000"
            self.bitrate_2 = "1000"
            self.bitrate_3 = "750"
            self.bitrate_4 = "500"

        if self.input_bitrate == "2000":
            self.bitrate_1 = "2000"
            self.bitrate_2 = "1500"
            self.bitrate_3 = "1000"
            self.bitrate_4 = "750"

        if self.input_bitrate == "3000":
            self.bitrate_1 = "3000"
            self.bitrate_2 = "2000"
            self.bitrate_3 = "1500"
            self.bitrate_4 = "750"

        if self.input_bitrate == "4000":
            self.bitrate_1 = "4000"
            self.bitrate_2 = "3000"
            self.bitrate_3 = "1500"
            self.bitrate_4 = "750"

        if self.input_bitrate == "5000":
            self.bitrate_1 = "5000"
            self.bitrate_2 = "3500"
            self.bitrate_3 = "1500"
            self.bitrate_4 = "750"

    def output_settings(self):
        '''Generate dict to be used by dynamodbClient put_item method. Groups
           resolution, audio and bitrate to one key by using a list inside dict.
           Can be accessed as dict[key][indice]'''
        result = {'output_1':[self.video_1, self.audio_1, self.bitrate_1] ,\
                  'output_2':[self.video_2, self.audio_2, self.bitrate_2],\
                  'output_3':[self.video_3, self.audio_3, self.bitrate_3],\
                  'output_4':[self.video_4, self.audio_4, self.bitrate_4]}
        return result

    def set_medialive_bitrates(self, resolution, bitrate):
        bitrate_clean = resolution[:3]
        bitrate_clean_2 = resolution[:4]
        if bitrate_clean_2 == "1080":
            Height = 1080
            Sharpness = 50
            ScalingBehavior = "DEFAULT"
            Widht = 1920
        if bitrate_clean == "720":
            Height = 720
            Sharpness = 100
            ScalingBehavior = "DEFAULT"
            Widht = 1280
        if bitrate_clean == "480":
            Height = 480
            Sharpness = 100
            ScalingBehavior = "STRETCH_TO_OUTPUT"
            Widht = 640
        if bitrate_clean == "240":
            Height = 240
            Sharpness = 100
            ScalingBehavior = "STRETCH_TO_OUTPUT"
            Widht = 320
        result = {
                "CodecSettings": {
                  "H264Settings": {
                    "AfdSignaling": "NONE",
                    "ColorMetadata": "INSERT",
                    "AdaptiveQuantization": "HIGH",
                    "Bitrate": int(bitrate)*1000,
                    "EntropyEncoding": "CABAC",
                    "FlickerAq": "ENABLED",
                    "FramerateControl": "SPECIFIED",
                    "FramerateNumerator": self.fps,
                    "FramerateDenominator": 1,
                    "GopBReference": "ENABLED",
                    "GopClosedCadence": 1,
                    "GopNumBFrames": 3,
                    "GopSize": 60,
                    "GopSizeUnits": "FRAMES",
                    "ScanType": "PROGRESSIVE",
                    "Level": "H264_LEVEL_AUTO",
                    "LookAheadRateControl": "HIGH",
                    "NumRefFrames": 3,
                    "ParControl": "INITIALIZE_FROM_SOURCE",
                    "Profile": "HIGH",
                    "RateControlMode": "CBR",
                    "Syntax": "DEFAULT",
                    "SceneChangeDetect": "ENABLED",
                    "Slices": 1,
                    "SpatialAq": "ENABLED",
                    "TemporalAq": "ENABLED",
                    "TimecodeInsertion": "DISABLED"
                  }
                },
                "Height": Height,
                "Name": resolution + "_" + bitrate,
                "RespondToAfd": "NONE",
                "Sharpness": Sharpness,
                "ScalingBehavior": ScalingBehavior,
                "Width": Widht
              }
        return result

    def set_medialive_resolutions(self, resolution, audio, bitrate):
        result = {
                    "OutputSettings": {
                      "HlsOutputSettings": {
                        "NameModifier": 'mod' + resolution + "_" + bitrate,
                        "HlsSettings": {
                          "StandardHlsSettings": {
                            "M3u8Settings": {
                              "AudioFramesPerPes": 4,
                              "AudioPids": "492-498",
                              "EcmPid": "8182",
                              "PcrControl": "PCR_EVERY_PES_PACKET",
                              "PmtPid": "480",
                              "ProgramNum": 1,
                              "Scte35Pid": "500",
                              "Scte35Behavior": "NO_PASSTHROUGH",
                              "TimedMetadataBehavior": "NO_PASSTHROUGH",
                              "VideoPid": "481"
                            },
                            "AudioRenditionSets": "PROGRAM_AUDIO"
                          }
                        }
                      }
                    },
                    "VideoDescriptionName": resolution + "_" + bitrate,
                    "AudioDescriptionNames": [ audio ],
                    "CaptionDescriptionNames": []
                  }
        return result

    def set_medialive_audio(self, audio):
        input_audio = audio[:10]
        if input_audio == "Audio_high":
            audio_bitrate = int('128000')
            audio_samplerate = int('48000')
        if input_audio == "Audio_low_":
            audio_bitrate = int('192000')
            audio_samplerate = int('48000')
        result = {
               "AudioSelectorName": "Default",
               "CodecSettings": {
                 "AacSettings": {
                   "InputType": "NORMAL",
                   "Bitrate": audio_bitrate,
                   "CodingMode": "CODING_MODE_2_0",
                   "RawFormat": "NONE",
                   "Spec": "MPEG4",
                   "Profile": "LC",
                   "RateControlMode": "CBR",
                   "SampleRate": audio_samplerate
                 }
               },
               "AudioTypeControl": "FOLLOW_INPUT",
               "LanguageCodeControl": "FOLLOW_INPUT",
               "Name": audio
             }
        return result

    def create_medialive_input(self, rtmp_url, input_sec_group):
        print(self.status)
        try:
            create_input = self.medialive.create_input(
                InputSecurityGroups=[ input_sec_group ], Name= self.channel_id + "_main_pull",
                Sources=[{'Url': rtmp_url}  , {'Url': rtmp_url}],
                Type="RTMP_PULL"
            )
            self.input_id = create_input['Input']['Id']
            self.log("CREATING", "Channel input created")
            print("Channel input created: Input ID: " + self.input_id)
        except Exception as e:
            self.log("FAILED", "Channel creation failed: create_input()")
            print("Channel input creation failed: " + e)
            print("Exiting")
            sys.exit(0)

    def create_medialive_channel(self, output, record, arn):
        try:
            create_channel = self.medialive.create_channel(
                Destinations = [
                    {"Id": "destination1", "Settings": [
                    {"Url": output + self.streamkey + "/" + self.streamkey + "-1", \
                    "Username": "", "PasswordParam": ""},
                    {"Url": record + self.streamkey + "/" + self.streamkey + "-2", \
                    "Username": "", "PasswordParam": ""}
                   ]}],
                EncoderSettings = {
                    "AudioDescriptions": [self.audio_1, self.audio_2, \
                    self.audio_3, self.audio_4],
                    "CaptionDescriptions": [],
                    "OutputGroups": [
                    {
                        "OutputGroupSettings": {
                          "HlsGroupSettings": {
                            "AdMarkers": [],
                            "CaptionLanguageSetting": "OMIT",
                            "CaptionLanguageMappings": [],
                            "HlsCdnSettings": {
                              "HlsBasicPutSettings": {
                                "NumRetries": 10,
                                "ConnectionRetryInterval": 1,
                                "RestartDelay": 15,
                                "FilecacheDuration": 300
                              }
                            },
                            "InputLossAction": "PAUSE_OUTPUT",
                            "ManifestCompression": "NONE",
                            "Destination": {
                              "DestinationRefId": "destination1"
                            },
                            "IvInManifest": "INCLUDE",
                            "IvSource": "FOLLOWS_SEGMENT_NUMBER",
                            "ClientCache": "ENABLED",
                            "TsFileMode": "SEGMENTED_FILES",
                            "ManifestDurationFormat": "INTEGER",
                            "SegmentationMode": "USE_SEGMENT_DURATION",
                            "OutputSelection": "MANIFESTS_AND_SEGMENTS",
                            "StreamInfResolution": "INCLUDE",
                            "IndexNSegments": 10,
                            "ProgramDateTime": "EXCLUDE",
                            "ProgramDateTimePeriod": 600,
                            "KeepSegments": 21,
                            "SegmentLength": 6,
                            "TimedMetadataId3Frame": "PRIV",
                            "TimedMetadataId3Period": 10,
                            "CodecSpecification": "RFC_4281",
                            "DirectoryStructure": "SUBDIRECTORY_PER_STREAM",
                            "SegmentsPerSubdirectory": 10000,
                            "Mode": "LIVE"
                          }
                        },
                        "Name": "HD",
                        "Outputs": [self.bitrate_1, self.bitrate_2, self.bitrate_3, self.bitrate_4],
                      }
                    ],
                    "TimecodeConfig": {
                        "Source": "EMBEDDED"
                      },
                    "VideoDescriptions": [self.video_1, self.video_2, \
                    self.video_3, self.video_4],
                    },
                InputAttachments=[
                    {
                      "InputId": self.input_id,
                      "InputSettings": {
                        "NetworkInputSettings": {
                          "ServerValidation": "CHECK_CRYPTOGRAPHY_AND_VALIDATE_NAME"
                        },
                        "SourceEndBehavior": "CONTINUE",
                        "InputFilter": "AUTO",
                        "FilterStrength": 1,
                        "DeblockFilter": "DISABLED",
                        "DenoiseFilter": "DISABLED",
                        "AudioSelectors": [],
                        "CaptionSelectors": [
                          {
                            "SelectorSettings": {
                              "EmbeddedSourceSettings": {
                                "Source608ChannelNumber": 1,
                                "Source608TrackNumber": 1,
                                "Convert608To708": "DISABLED",
                                "Scte20Detection": "OFF"
                              }
                            },
                            "Name": "EmbeddedSelector"
                          }
                        ]
                      }
                    }
                  ],
                InputSpecification={
                        "Codec": "AVC",
                        "Resolution": "HD",
                        "MaximumBitrate": "MAX_10_MBPS"
                        },
                Name= self.channel_name,
                RoleArn=arn,
                )
            channel_Arn = create_channel['Channel']['Arn']
            self.log("CREATING", "Medialive Channel created succesfully")
            self.medialive_id = channel_Arn[49:]
            put_medialive_id = self.dynamodb.update_item(
                Key={'channel_id': self.channel_id,
                      'user_id': self.user_id},
                UpdateExpression="SET medialive_id = :val1",
                ExpressionAttributeValues={":val1": self.medialive_id}
            )
            print('Channel created succesfully')
        except Exception as e:
            self.log("FAILED", "Medialive Channel creation failed: create_channel()")
            print('Creating channel failed: ' + e + ' Exiting ...')
            self.stop_medialive_channel()
            sys.exit(0)

    def start_medialive_channel(self):
        describe_channel = self.medialive.describe_channel(ChannelId=self.medialive_id)
        channel_status = describe_channel['State']
        while channel_status != "IDLE":
            time.sleep(15)
            try:
                describe_channel = self.medialive.describe_channel(ChannelId=self.medialive_id)
                channel_status = describe_channel['State']
            except Exception as e:
                print("Something went wrong at startup. Exiting ...")
                channel_status = "IDLE"
                self.log("FAILED", "Channel startup failed: start_channel()")
                self.stop_medialive_channel()
        self.log("CREATING", "Channel is IDLE and starting up")
        print('channel is IDLE and starting up')

        start_channel = self.medialive.start_channel(ChannelId=self.medialive_id)
        while channel_status != "RUNNING":
            time.sleep(15)
            try:
                describe_channel = self.medialive.describe_channel(ChannelId=self.medialive_id)
                channel_status = describe_channel['State']
            except Exception as e:
                print("Something went wrong at startup. Exiting ...")
                channel_status = "IDLE"
                self.log("FAILED", "Channel startup failed: start_channel()")
                self.stop_medialive_channel()

        self.log("RUNNING", "Channel is running")
        print('channel is RUNNING')

    def stop_medialive_channel(self):
        if self.status == "STOPPING":
            print("Channel is stopping. Exiting ...")
            sys.exit(0)

        stop_channel = self.medialive.stop_channel(ChannelId=self.medialive_id)
        channel_status = self.status
        while channel_status != "IDLE":
            time.sleep(15)
            try:
                describe_channel = self.medialive.describe_channel(ChannelId=self.medialive_id)
                channel_status = describe_channel['State']
            except Exception as e:
                channel_status = "IDLE"
                self.log("FAILED", "Stopping channel failed: stop_channel()")
                print("Something went wrong when stopping. Exiting ...")
        self.log("STOPPING", "Channel is stopping")
        print('channel is stopping')

        delete_channel = self.medialive.delete_channel(ChannelId=self.medialive_id)
        channel_status = self.status
        while channel_status != "DELETED":
            time.sleep(15)
            try:
                describe_channel = self.medialive.describe_channel(ChannelId=self.medialive_id)
                channel_status = describe_channel['State']
            except Exception as e:
                channel_status = "DELETED"
                self.log("FAILED", "Stopping channel failed: stop_channel()")
                print("Something went wrong when stopping. Exiting ...")
        remove_input = self.medialive.delete_input(InputId= self.input_id)
        self.log("DELETED", "Channel has been deleted succesfully")
        print('channel has been deleted')
        sys.exit(0)
