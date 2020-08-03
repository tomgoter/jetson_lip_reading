#!/bin/bash

apt-get install -y python3-gi gstreamer-1.0

exec "$@"
