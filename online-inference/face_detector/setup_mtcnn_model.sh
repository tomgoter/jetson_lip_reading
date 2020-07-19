#!/bin/bash

# do prep work in mtcnn folder
cd mtcnn
make
./create_engines

# do prep work in main face_detector folder
cd ..
make

exec "$@"
