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


## Fake Face Detector

To help with the development of the audio synthesizer (so there's nothing dependent on the actual face detector), we had the additional fake face detector for taking data preprocessed from YouTube videos (via the Lip2Wav's original preprocess.py script), which can be used to standardize input data and emulate the actual face detector logic. 

### Running the Container

All necessary code for the fake face detection lives in `fake_face_detector/`, including the Dockerfile used to construct this container.

The following docker commands can be used to create and run everything from the `face_Detector/` folder:
```
> docker build -t ffd_jlr -f Dockerfile.fakefacedetector .                                                            # to build the image
> docker run -ti --name ffd1 -e QOS=2 -e SOURCE_DIR="./Dataset/mini_sample/preprocessed/6DGPuhFoiJI/cut-0/" ffd_jlr   # to run the container with a single cut of data
> > docker run -ti --name ffd1 -e QOS=2 -e PUB_HOST "10.0.0.34" -e SOURCE_DIR="./Dataset/mini_sample/preprocessed/6DGPuhFoiJI/cut-0/" ffd_jlr # to run the container with multiple cuts of data (warning that this takes a while to process)
> docker container stop ffd1 && docker container rm ffd1                                                              # to stop & remove container
```

Be sure to have the preprocessed dataset in the `fake_face_detector/` directory, as it will search for the `SOURCE_DIR` relative to this location.


## Running the Synthesizer

### Running the Container

All necessary code for speech/audio synthesis lives in `audio_synthesizer/`, including the Dockerfile used to construct this container. 

The following docker commands can be used to create and run everything from the `audio_synthesizer/` folder:
```
> docker build -t as_jlr -f Dockerfile.audiosynthesizer .                       # to build the image                    
> docker run -ti --name as1 -e HOST="10.0.0.47" -e CHECKPOINT="<path-to-checkpoint>" -e PRESET="<path-to-preset>" --privileged as_jlr bash     # to start the container
> docker container stop as1 && docker container rm as1                          # to stop & remove container
```

Be sure that the you've included the presets you're interested in using in the folder `audio_synthesizer/synthesizer/presets/` and the weights you're interested in using in `audio_synthesizer/weights/` prior to building the container to ensure they will be available at container runtime. 

Running the docker container _____

python3 audio_synthesizer.py -d Dataset/mini_sample -r Dataset/mini_sample/test_results --preset synthesizer/presets/chem.json --checkpoint "weights/logs_chemistry/tacotron_model.ckpt-159000" --sub_client_name "jetson-face-receiver" --sub_mqtt_host $PUB_HOST --sub_mqtt_port 1883 --sub_qos $QOS --sub_topic $SUB_TOPIC

### References & Licenses

Credits for the work done for synthesizing the audio samples from images of faces goes to the research project Lip2Wav linked here: [https://github.com/Rudrabha/Lip2Wav](https://github.com/Rudrabha/Lip2Wav)

For licenses, citations, and acknowledgements, please refer to the links included below:
* [https://github.com/Rudrabha/Lip2Wav#license-and-citation](https://github.com/Rudrabha/Lip2Wav#license-and-citation)
* [https://github.com/Rudrabha/Lip2Wav#acknowledgements](https://github.com/Rudrabha/Lip2Wav#acknowledgements)

## Runing the Audio Player

### Running the Container

All necessary code for playing the synthesized speech/audio lives in `audio_synthesizer/`, including the Dockerfile used to construct this container. 

```
> docker build -t ap_jlr -f Dockerfile.audiosynthesizer .                                  # to build the image
> docker run -ti --name ap1 -e SUB_HOST="10.0.0.47" --privileged --device /dev/snd ap_jlr  # to start the container  
> docker container stop ap1 && docker container rm ap1                                     # to stop & remove container
```

 python3 audio_player.py "jetson/audio-receiver" "10.0.0.47" 1883 2 "jetson/audio"