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

### Running the Container

All necessary code for face detection lives in `audio_synthesizer/`, including the Dockerfile used to construct this container. 

The following docker commands can be used to create and run everything from the `audio_synthesizer/` folder:
```
> docker build -t as_jlr -f Dockerfile.audiosynthesizer .                       # to build the image
> docker run -ti --name as1 -e QOS=2 as_jlr                                     # to start the container
> docker run -ti --name as1 -e QOS=2 -v ~/repos/jetson_lip_reading/online-inference/audio_synthesizer/:/audio_synthesizer/ as_jlr bash              

> docker container stop as1 && docker container rm as1                          # to stop & remove container
```

Running the docker container _____

python3 audio_synthesizer.py -d Dataset/mini_sample -r Dataset/mini_sample/test_results --preset synthesizer/presets/chem.json --checkpoint "weights/logs_chemistry/tacotron_model.ckpt-159000" --sub_client_name "jetson-face-receiver" --sub_mqtt_host $PUB_HOST --sub_mqtt_port 1883 --sub_qos $QOS --sub_topic $SUB_TOPIC

### References & Licenses

Credits for the work done for synthesizing the audio samples from images of faces goes to the research project Lip2Wav linked here: [https://github.com/Rudrabha/Lip2Wav](https://github.com/Rudrabha/Lip2Wav)

For licenses, citations, and acknowledgements, please refer to the links included below:
* [https://github.com/Rudrabha/Lip2Wav#license-and-citation](https://github.com/Rudrabha/Lip2Wav#license-and-citation)
* [https://github.com/Rudrabha/Lip2Wav#acknowledgements](https://github.com/Rudrabha/Lip2Wav#acknowledgements)



