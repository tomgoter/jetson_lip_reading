# Online Inference

## Face Detector

All necessary code for face detection lives in `face_detector/`, including the Dockerfile to construct this container. 

The following docker commands can be used to create and run everything from the `face_detector/` folder:
```
> docker build -t fd_jlr -f Dockerfile.facedetector .                           # to build the image
> docker run -ti --name fd1 -e DISPLAY=$DISPLAY -e QOS=2 --privileged fd_jlr    # to start the container
> docker container stop fd1 && docker container rm fd1                          # to stop & remove container
```

Running the docker container will start up the face detection model and will read in images from the attached camera at video input 1. 

Credits for the face detection model go to the MTCNN Face Detection demo linked here: https://github.com/jkjung-avt/tensorrt_demos#demo-2-mtcnn


## Running the Synthesizer

