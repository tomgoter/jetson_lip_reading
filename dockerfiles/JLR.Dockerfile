# use the cuda from lab 1 as the base image
FROM w251/cuda:dev-tx2-4.3_b132

ARG URL=http://169.44.201.108:7002/jetpacks/4.3

RUN apt-get update && apt install -y git pkg-config wget build-essential cmake unzip

WORKDIR /tmp

RUN curl $URL/libopencv_3.3.1-2-g31ccdfe11_arm64.deb  -so libopencv_3.3.1-2-g31ccdfe11_arm64.deb

RUN curl $URL/libopencv-dev_3.3.1-2-g31ccdfe11_arm64.deb -so libopencv-dev_3.3.1-2-

RUN curl $URL/libopencv-python_3.3.1-2-g31ccdfe11_arm64.deb -so libopencv-python_3.3.1-2-g31ccdfe11_arm64.deb

RUN apt remove -y libopencv-calib3d-dev libopencv-core-dev

RUN apt install -y libtbb-dev libavcodec-dev libavformat-dev libgstreamer1.0-dev libgstreamer-plugins-base1.0-dev libgtk2.0-dev libcanberra-gtk-module libcanberra-gtk3-module

RUN apt-get update

RUN apt-get install -y libswscale-dev libv4l-dev

RUN dpkg -i *.deb

RUN rm -f /tmp/*.deb

# Get pip
RUN apt-get update && apt-get install -y software-properties-common
RUN apt-get update && apt-get install -y python3-pip
RUN apt-get update && apt-get install -y ffmpeg
RUN apt-get install -y llvm-7 llvm-7
RUN apt-get install -y libhdf5-serial-dev hdf5-tools libhdf5-dev zlib1g-dev zip libjpeg8-dev

ENV LLVM_CONFIG /usr/bin/llvm-config-7

# Install PIP and numpy and cython
RUN pip3 install --upgrade pip \
     && pip3 install Cython 
RUN pip3 install -U numpy grpcio absl-py py-cpuinfo psutil portpicker six mock requests gast h5py astor termcolor protobuf keras-applications keras-preprocessing wrapt google-pasta
RUN apt-get install -y python3-pyqt5
RUN apt-get install -y build-essential gfortran libatlas-base-dev libfreetype6-dev
RUN apt-get update
RUN pip3 install -U pesq==0.0.1 pystoi==0.2.2 scikit-learn==0.21.2 scipy==1.3.0 
RUN pip3 install llvmlite

RUN apt remove -y libtbb-dev 
RUN pip3 install inflect \     
     && pip3 install librosa==0.7.
RUN pip3 install lws==1.2.6 \
     && pip3 install Markdown==3.1.1 \
     && pip3 install matplotlib==3.1.1 \
     && pip3 install multiprocess

RUN pip3 install sounddevice==0.3.13 \
     && pip3 install SoundFile==0.10.2 \
     && pip3 install tensorboard==1.13.1 \
     && pip3 install tensorboardX==2.0 \
     && pip3 install tensorflow-estimator==1.13.0
RUN pip3 install tensorflow-gpu==1.13.1 \
     && pip3 install tqdm \
     && pip3 install umap-learn \
     && pip3 install Unidecode \
     && pip3 install visdom \
     && pip3 install webrtcvad \
     && pip3 install youtube-dl \
     && pip3 install torch==1.1.0

# Install the mosquito business
RUN pip3 install paho-mqtt

# Change working directory
WORKDIR /

# Add CUDA to PATH
ENV PATH $PATH:/usr/local/cuda-10.0/bin

#
RUN ldconfig

# Add the python file to the container
#ADD face_detector.py /

# Run the face detecting python script
#CMD python3 face_detector.py


