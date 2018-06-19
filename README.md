# Autolive: AWS medialive automation

This core idea of this proyect is to offload video transcoding from a NGNIX-RTMP server to AWS Medialive.

NGINX RTMP: https://github.com/arut/nginx-rtmp-module

Video workflow:

  RTMP Encoder --> Nginx --> AWS Medialive --> CDN
