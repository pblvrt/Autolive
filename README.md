# Autolive: AWS medialive automation

The core idea of this proyect is to offload video transcoding from an NGNIX-RTMP server to AWS Medialive, replacing FFMPEG for transcoding and reducing server load from NGINX server.

NGINX RTMP: https://github.com/arut/nginx-rtmp-module

## How to make it work:

1) Install Nginx with rtmp module.
2) Git clone Autolive into preferred dir.
3) Set AWS details in conf.py.
4) Simlink autolive to /usr/local/bin/autolive.
5) Change nginx.conf to trigger autolive. (using nginx-rtmp exec options)

## AWS resources needed:

* DynamoDB table that defines channel details. (schema comming soon)
* s3 bucket for AWS medalive outputs.
* CDN distribution. (optional)

## CLI options:

* '-s', '--streamkey' --> (string) | Define streamkey. Streamkey should reference dynamodb table.
* '-a', '--action' --> (string) | Define what action to perform: 'create', 'delete'.
* '-A', '--application' --> (string) | manually define Nginx rtmp application, default 'live'.
       
## Notes:

ATM only pull channels are supported.
Lots of improvment needed but core functionality is working.
