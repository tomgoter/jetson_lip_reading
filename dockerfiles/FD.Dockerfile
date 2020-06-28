# use the cuda from lab 1 as the base image
FROM w251/tensorrt:dev-tx2-4.3_b132

ARG URL=http://169.44.201.108:7002/jetpacks/4.3

RUN apt-get update && apt install -y git pkg-config wget build-essential cmake unzip

WORKDIR /tmp

RUN curl $URL/libopencv_3.3.1-2-g31ccdfe11_arm64.deb  -so libopencv_3.3.1-2-g31ccdfe11_arm64.deb

RUN curl $URL/libopencv-dev_3.3.1-2-g31ccdfe11_arm64.deb -so libopencv-dev_3.3.1-2-

RUN curl $URL/libopencv-python_3.3.1-2-g31ccdfe11_arm64.deb -so libopencv-python_3.3.1-2-g31ccdfe11_arm64.deb

RUN apt remove -y libopencv-calib3d-dev libopencv-core-dev

RUN apt install -y  libtbb-dev libavcodec-dev libavformat-dev libgstreamer1.0-dev libgstreamer-plugins-base1.0-dev libgtk2.0-dev

RUN apt install -y libswscale-dev libv4l-dev

RUN dpkg -i *.deb

RUN rm -f /tmp/*.deb

RUN apt install -y libcanberra-gtk-module libcanberra-gtk3-module libgstreamer1.0-dev libgstreamer-plugins-base1.0-dev

# Get pip
RUN apt-get update && apt-get install -y     software-properties-common
RUN apt-get update && apt-get install -y python3-pip

# Install PIP and numpy and cython
RUN pip3 install --upgrade pip \
     && pip3 install --no-cache-dir numpy \
     && pip3 install Cython

# Install the mosquito business
RUN pip3 install paho-mqtt

# Change working directory
WORKDIR /

# Add CUDA to PATH
ENV PATH $PATH:/usr/local/cuda-10.0/bin

# Add Jetson Inference

RUN apt-get update
RUN apt-get install git cmake libpython3-dev python3-numpy
RUN git clone --recursive https://github.com/dusty-nv/jetson-inference
WORKDIR /jetson-inference/build
RUN cmake ../
RUN make -j$(nproc)
RUN make install

RUN apt install -y gstreamer1.0-plugins-good

WORKDIR /
#
RUN ldconfig



