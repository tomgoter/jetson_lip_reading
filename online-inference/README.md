# Online Inference

## Face Detector

### Running the Container

All necessary code for face detection lives in `face_detector/`, including the Dockerfile used to construct this container. 

The following docker commands can be used to create and run everything from the `face_detector/` folder:
```
> docker build -t fd_jlr -f Dockerfile.facedetector .                           # to build the image
> docker run -ti --name fd1 -e DISPLAY=$DISPLAY -e QOS=2 --privileged fd_jlr    # to start the container
> docker container stop fd1 && docker container rm fd1                          # to stop & remove container
```

Running the docker container will start up the camera at video input 1 and face detection model and will read in images and crop out the first identified face in each frame. These faces will then be published to the topic specified in the Dockerfile. 

### References & Licenses

Credits for the face detection model go to the MTCNN Face Detection demo linked here: [https://github.com/jkjung-avt/tensorrt_demos#demo-2-mtcnn](https://github.com/jkjung-avt/tensorrt_demos#demo-2-mtcnn)

The referenced demo references source code of [NVIDIA/TensorRT](https://github.com/NVIDIA/TensorRT) samples to develop most of the demos in its repository. Those NVIDIA samples are under [Apache License 2.0](https://github.com/NVIDIA/TensorRT/blob/master/LICENSE).

## Running the Synthesizer



