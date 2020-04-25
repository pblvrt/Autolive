
import json

""" This file defines all cutom errors to be thrown by Autolive """

class MissingStreamError(Exception):
    def __init__(self, input_data=None):
        self.error_message = "Currently only two streams inputs are supported."
        self.input_data = input_data
        self.message = "{message}\ninput data:\n{input_data}"\
                        .format(message=self.error_message, input_data=json.dumps(self.input_data, indent=4, sort_keys=True))
    def __str__(self):
        return str(self.message)

class WrongCodecError(Exception):
    def __init__(self, input_data=None):
        self.error_message = "Currently only aac and h264 codecs are supported"
        self.input_data = input_data
        self.message = "{message}\ninput data:\n{input_data}"\
                        .format(message=self.error_message, input_data=input_data)
    def __str__(self):
        return str(self.message)