# Online Inference

## Running Face Detector

All necessary code for face detection lives in `face_detector/`. 

The following docker commands can be used to create and run everything:
```
> docker build -t fd_jlr -f Dockerfile.facedetector .                                                   # to build the image
> docker run -ti --name fd1 -e DISPLAY=$DISPLAY -e QOS=2 --privileged  fd_jlr                           # to start the container
> docker container stop fd1 && docker container rm fd1                                                  # to stop & remove container
```

