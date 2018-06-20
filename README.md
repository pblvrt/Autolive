# Autolive: AWS medialive automation

The core idea of this proyect is to offload video transcoding from a NGNIX-RTMP server to AWS Medialive.

NGINX RTMP: https://github.com/arut/nginx-rtmp-module

# How to make it work:

1) Install Nginx with rtmp module.
2) Git clone Autolive into preferred dir.
3) Set details in conf.py.
4) Simlink autolive to /usr/local/bin/autolive.
5) Change nginx.conf to trigger autolive. (using nginx-rtmp exec options)

# AWS resources needed:

1) DynamoDB table that defines channel details. (schema comming soon)
2) s3 bucket for trancoding output files.
3) CDN distribution. (optional)

# CLI options:

'-s', '--streamkey' --> (string) |
'-a', '--action' --> (string) | Define what action to perform: 'create', 'delete'
'-A', '--application' --> (string) | manually define Nginx rtmp application, default 'live'
       
# Notes:

ATM only pull channels are supported.
Lots of improvment needed but core functionality is working.
