#global var
import boto3, requests, json
import os, time, sys

class Config:
    def __init__(self, streamkey):
        self.streamkey = streamkey
        self.rtmp_url = None
        self.livestream_output = os.environ['S3_BUCKET']
        self.livestream_record = os.environ['S3_BUCKET']
        self.input_sec_group = os.environ['INPUT_SEC_GROUP']
        self.channel_prefix = 'channel/'
        self.logs_prefix = 'logs/'
        self.arn = os.environ['ARN']
        self.medialive = boto3.client(
                'medialive',
                aws_access_key_id= os.environ['ACCESS'],
                aws_secret_access_key=os.environ['SECRET'],
                region_name='eu-west-1',
            )
        self.dynamodb = None
        self.load_dynamodb()
        self.load_public_ip()

    def load_dynamodb(self):
        dynamo = boto3.resource(
                'dynamodb',
                aws_access_key_id= os.environ['ACCESS'],
                aws_secret_access_key=os.environ['SECRET'],
                region_name='eu-west-1',
        )
        self.dynamodb = dynamo.Table('channels_table')

    def load_data(self):
        response = self.dynamodb.scan(
            ScanFilter={
                'streamkey': {
                'AttributeValueList': [self.streamkey],
                'ComparisonOperator': 'EQ'}})
        try:
            self.channel_id = response['Items'][0]['channel_id']
            self.user_id = response['Items'][0]['user_id']
            return response['Items'][0]
        except Exception as e:
            print("channel creation failed: channel was not found")
            sys.exit(0)

    def load_public_ip(self):
        get_ip = requests.get('http://jsonip.com')
        json_ip = json.loads(get_ip.text)
        self.rtmp_url = 'rtmp://' + json_ip['ip'] + '/medialive'
