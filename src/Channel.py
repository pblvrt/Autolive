import uuid
import boto3
from LadderGenerator import LadderGenerator


class Channel:
    def __init__(self, stream_key, input_width, input_height, input_fps, input_bitrate, input_audio_bitrate):
        self.channel_id = str(uuid.uuid4())
        self.input_stream_key = stream_key
        self.input_width = input_width
        self.input_height = input_height
        self.input_bitrate = input_bitrate
        self.input_fps = input_fps
        self.input_audio_bitrate = input_audio_bitrate
        
        generator = LadderGenerator()
        self.ladder = generator.generate(self.input_width, self.input_bitrate, self.input_audio_bitrate, self.input_fps, [])
        self.S3_output_bucket = 's3://medialivetests'
  
    def generateAudioDescriptions(self):
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
    
    def generateVideDescriptions(self):
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
      
    def generateOutputgroupsOutputs(self):
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
        client = boto3.client('medialive')
        response = client.create_channel(
            ChannelClass = 'SINGLE_PIPELINE',
            #An Amazon S3 bucket, serving as an origin server that a CDN such as Amazon CloudFront can pull from.
            Destinations = [
                {
                    'Id': self.channel_id + '-output',
                    'Settings': [
                        {
                            'Url': self.S3_output_bucket + '/' + self.input_stream_key + '/' + self.input_stream_key + '-1'
                        }
                    ]
                },
            ],
            EncoderSettings = {
                'AudioDescriptions': self.generateAudioDescriptions(),
                'VideoDescriptions': self.generateVideDescriptions(),
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
                                    'DestinationRefId': self.channel_id + '-output'
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
                        'Outputs': self.generateOutputgroupsOutputs()
                    }
                ],
                "TimecodeConfig": {
                    "Source": "EMBEDDED"
                },
            },
            InputAttachments = [
                {
                    'InputAttachmentName': 'dev',
                    'InputId': '3511215'         
                }
            ],
            InputSpecification = {
                'Codec': 'AVC',
                'MaximumBitrate': 'MAX_10_MBPS',
                'Resolution': 'HD'
            },
            LogLevel = 'ERROR',
            Name = self.channel_id,
            RoleArn = 'arn:aws:iam::707435100420:role/MediaLiveAccessRole'
        )
        print(response)

"""
# Tests
channel = Channel("test", 1080, 1920, 60, 7800, 192000)
#print(channel.generateVideDescriptions())
#print(channel.generateAudioDescriptions())
#print(channel.generateOutputgroupsOutputs())
channel.create_channel()
"""