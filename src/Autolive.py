import argparse
import boto3
from Channel import Channel

#python3 script.py test "$(ffprobe -show_streams -print_format json rtmp://localhost:1935/live/test)"

def Autolive(Key, Data):
    with open ("testing.txt", "w") as f:
        f.write(Key + '\n')
        f.write(Data)

def create_channel():
    """ Create an AWS Medialive Channel """
    channel = Channel('test', 1080, 1920, 60, 7800, 192000)
    channel.create_channel()
    
if __name__ == "__main__":
    """
    parser = argparse.ArgumentParser(description='Test.')
    parser.add_argument('Key', type=str)
    parser.add_argument('Data', type=str)
    args = parser.parse_args()
    main(args.Key, args.Data)
    """
    create_channel()