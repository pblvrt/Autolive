from datetime import datetime
import time, os

class Logger:
    def __init__(self, channel_id, user_id, dynamodb):
        self.channel_id = channel_id
        self.user_id = user_id
        self.dynamodb = dynamodb

    def log(self, status, message):
        """ log to server log, dynamodb and console
            date - channel_id - status - message
            medialive: CREATING, RUNNING, FAILED, STOPPING, DELETED // server: INFO, ERROR"""
        with open(os.path.abspath('../autolive.log'), 'a+') as f:
            print(time.asctime( time.localtime(time.time()) ) + ' - ' +self.channel_id \
            + ': ' + status + ' ' + message, file=f)

        """ Output to console """
        print(time.asctime( time.localtime(time.time()) ) + ' - ' +self.channel_id \
        + ': ' + status + ' ' + message)

        if status not in ['INFO', 'ERROR']:
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
