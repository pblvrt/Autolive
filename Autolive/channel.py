import uuid
import boto3
import time
import json
import urllib

from .ladder_generator import Ladder_generator


class Channel:
    def __init__(self, stream_key, input_width, input_height, input_fps, input_bitrate, input_audio_bitrate, input_type):

        self.input_stream_key = stream_key
        self.input_width = input_width
        self.input_height = input_height
        self.input_bitrate = input_bitrate
        self.input_fps = input_fps
        self.input_audio_bitrate = input_audio_bitrate
        self.input_type = input_type
        
        generator = Ladder_generator()
        self.ladder = generator.generate(self.input_height, self.input_bitrate, self.input_audio_bitrate, self.input_fps, [])
        
        self.S3_output_bucket = 's3://medialivetests'
        self.client = boto3.client('medialive')
        
        self.input_id = None
        self.channel_id = None
        
    
    def generate_audio_descriptions(self):
        audioDescriptions = []
        for item in self.ladder:
            description = {
               "AudioSelectorName": "Default",
               "CodecSettings": {
                 "AacSettings": {
                   "InputType": "NORMAL",
                   "Bitrate": item['audio_bitrate'],
                   "CodingMode": "CODING_MODE_2_0",
                   "RawFormat": "NONE",
                   "Spec": "MPEG4",
                   "Profile": "LC",
                   "RateControlMode": "CBR",
                   "SampleRate": 48000
                 }
               },
               "AudioTypeControl": "FOLLOW_INPUT",
               "LanguageCodeControl": "FOLLOW_INPUT",
               "Name": str(item['width']) + "_audio"
            }
            audioDescriptions.append(description)

        return audioDescriptions
    
    def generate_vide_descriptions(self):
        videoDescriptions = []
        for item in self.ladder:
            description = {
                "CodecSettings": {
                  "H264Settings": {
                    "AfdSignaling": "NONE",
                    "ColorMetadata": "INSERT",
                    "AdaptiveQuantization": "HIGH",
                    "Bitrate": item['bitrate']*1000,
                    "EntropyEncoding": "CABAC",
                    "FlickerAq": "ENABLED",
                    "FramerateControl": "SPECIFIED",
                    "FramerateNumerator": item['fps'],
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
                "Height": item['height'],
                "Width": item['width'],
                "Name": str(item['width']) + "_" + str(item['bitrate']),
                "RespondToAfd": "NONE",
                "Sharpness": 100,
                "ScalingBehavior": "DEFAULT",
            }
            videoDescriptions.append(description)
        return videoDescriptions
      
    def generate_output_groups_outputs(self):
        outputs = []
        for item in self.ladder:            
            result = {
                "OutputSettings": {
                    "HlsOutputSettings": {
                    "NameModifier": str(item['width']) + "_" + str(item['bitrate']),
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
                "VideoDescriptionName": str(item['width']) + "_" + str(item['bitrate']),
                "AudioDescriptionNames": [ str(item['width']) + "_audio" ]
            }
            outputs.append(result)
        return outputs
    
    def create_channel(self):
        """
            Create AWS Media live channel.
            Requires an AWS Media live channel input to already be created so if input_id is None,
            we will always call the create_channel_input() function to generate one.
            This function depends on generate_audio_descriptions(), generate_vide_descriptions() and
            generateOutputgroupsOutputs(), if any of these fails the creation of the channel will fail.
        """
        
        if self.input_id == None:
            self.create_channel_input()
        
        search = next((item for item in self.client.list_channels()['Channels'] if item["Name"] == self.input_stream_key), False)
        if search:
            self.channel_id = search['Id']
            return
        
        response = self.client.create_channel(
            ChannelClass = 'SINGLE_PIPELINE',
            #An Amazon S3 bucket, serving as an origin server that a CDN such as Amazon CloudFront can pull from.
            Destinations = [
                {
                    'Id': self.input_stream_key + '-output',
                    'Settings': [
                        {
                            'Url': self.S3_output_bucket + '/' + self.input_stream_key + '/' + self.input_stream_key + '-1'
                        }
                    ]
                },
            ],
            EncoderSettings = {
                'AudioDescriptions': self.generate_audio_descriptions(),
                'VideoDescriptions': self.generate_vide_descriptions(),
                'OutputGroups': [
                    {
                        'Name': "OutputGroup",
                        'OutputGroupSettings': {
                            'HlsGroupSettings': {
                                'CaptionLanguageSetting': 'OMIT',
                                'ClientCache':'ENABLED',
                                'CodecSpecification': 'RFC_4281',
                                'DirectoryStructure': 'SINGLE_DIRECTORY',
                                'Destination': {
                                    'DestinationRefId': self.input_stream_key + '-output'
                                },
                                'HlsCdnSettings': {
                                    'HlsBasicPutSettings': {
                                        'ConnectionRetryInterval': 30,
                                        'FilecacheDuration': 300,
                                        'NumRetries': 5,
                                        'RestartDelay': 5
                                    },
                                },
                                'IFrameOnlyPlaylists': 'DISABLED',
                                'InputLossAction': 'PAUSE_OUTPUT',
                                'KeepSegments': 21,
                                'ManifestCompression': 'NONE',
                                'ManifestDurationFormat': 'FLOATING_POINT',
                                'Mode': 'LIVE',
                                'OutputSelection': 'MANIFESTS_AND_SEGMENTS',
                                'ProgramDateTime': 'INCLUDE',
                                'ProgramDateTimePeriod': 600,
                                'RedundantManifest': 'DISABLED',
                                'SegmentationMode': 'USE_SEGMENT_DURATION',
                                'SegmentsPerSubdirectory': 10000,
                                'StreamInfResolution': 'INCLUDE',
                                'TimedMetadataId3Frame': 'PRIV',
                                'TimedMetadataId3Period': 10,
                                'TsFileMode': 'SEGMENTED_FILES'
                            },
                        },
                        'Outputs': self.generate_output_groups_outputs()
                    }
                ],
                "TimecodeConfig": {
                    "Source": "EMBEDDED"
                },
            },
            InputAttachments = [
                {
                    'InputAttachmentName': self.input_stream_key,
                    'InputId': self.input_id         
                }
            ],
            InputSpecification = {
                'Codec': 'AVC',
                'MaximumBitrate': 'MAX_10_MBPS',
                'Resolution': 'HD'
            },
            LogLevel = 'ERROR',
            Name = self.input_stream_key,
            RoleArn = 'arn:aws:iam::707435100420:role/MediaLiveAccessRole'
        )
        #print(json.dumps(response, indent=4, sort_keys=True))
        self.channel_id = response['Channel']['Id']

    def create_channel_input(self):
        search = next((item for item in self.client.list_inputs()['Inputs'] if item["Name"] == self.input_stream_key), False)
        if search:
            self.input_id = search['Id']
            return

        # Check server IP to create Sources URL and to create Sec. group for input.
        getIp = urllib.request.urlopen('https://api.ipify.org?format=json').read()
        ip = json.loads(getIp)['ip']        

        if self.input_type == 'Pull':
            response = self.client.create_input(
                            Sources=[
                                {
                                    'Url': "rtmp://{ip}/pool/{key}".format(ip=ip, key=self.input_stream_key)
                                },
                            ],
                            Name=self.input_stream_key,
                            Type='RTMP_PULL',
                        )
            print(response)
        else:
            secGroupId = self.client.create_input_security_group(
                        WhitelistRules=[
                            {
                                'Cidr': '{ip}/32'.format(ip=ip)
                            },
                        ]
                    )['SecurityGroup']['Id']
            response = self.client.create_input(
                            Destinations=[
                                {
                                    'StreamName': "{key}/{key}".format(key=self.input_stream_key)
                                },
                            ],
                            InputSecurityGroups=[
                                secGroupId
                            ],
                            Name=self.input_stream_key,
                            Type='RTMP_PUSH',
                        )
        
        self.input_id = response['Input']['Id']
        status = response['Input']['State']
        while status  == 'CREATING':
            time.sleep(1)
            status = self.client.describe_input(InputId=self.input_id)['State']
         
    def start_channel(self):
        return
    
    def delete_channel(self):
        return
    
    def check_status(self):
        if self.channel_id == None:
            search = next((item for item in self.client.list_channels()['Channels'] if item["Name"] == self.input_stream_key), False)
            if search:
                self.channel_id = search['Id']
            else:
                return None  
        response = self.client.describe_channel(
                        ChannelId=self.channel_id
                    )
        return response['State']
    

"""
# Tests
channel = Channel("5345346-345", 1080, 1920, 60, 7800, 192000, 'Push')
#print(channel.generateVideDescriptions())
#print(channel.generateAudioDescriptions())
#print(channel.generateOutputgroupsOutputs())
#channel.create_channel_input()
#channel.create_channel()
#channel.check_status()
channel.create_channel_input()
"""