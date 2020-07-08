# use the keras/tf1 image as base
FROM w251/keras:dev-tx2-4.3_b132-tf1

ARG URL=http://169.44.201.108:7002/jetpacks/4.3

RUN apt-get update && apt install -y build-essential cmake unzip

WORKDIR /tmp

RUN curl $URL/libopencv_3.3.1-2-g31ccdfe11_arm64.deb  -so libopencv_3.3.1-2-g31ccdfe11_arm64.deb

RUN curl $URL/libopencv-dev_3.3.1-2-g31ccdfe11_arm64.deb -so libopencv-dev_3.3.1-2-

RUN curl $URL/libopencv-python_3.3.1-2-g31ccdfe11_arm64.deb -so libopencv-python_3.3.1-2-g31ccdfe11_arm64.deb

RUN apt remove -y libopencv-calib3d-dev libopencv-core-dev

RUN apt install -y libcanberra-gtk-module libcanberra-gtk3-module libv4l-dev

RUN apt update

RUN dpkg -i *.deb

RUN rm -f /tmp/*.deb

# Get pip
RUN apt install -y software-properties-common \
  && apt install -y ffmpeg \
  && apt-get install -y llvm-9 llvm-9
RUN apt-get install -y libhdf5-serial-dev  

ENV LLVM_CONFIG /usr/bin/llvm-config-9

# Install PIP and numpy and cython
RUN pip3 install --upgrade pip \
     && pip3 install Cython 
RUN pip3 install -U py-cpuinfo psutil portpicker requests astor termcolor wrapt google-pasta
RUN apt-get install -y python3-pyqt5
RUN apt-get install -y build-essential gfortran libatlas-base-dev libfreetype6-dev
RUN apt-get update
RUN pip3 uninstall -y enum34
RUN pip3 install -U pesq==0.0.1 pystoi==0.2.2 scipy==1.3.0 
RUN pip3 install llvmlite

RUN pip3 install --ignore-installed joblib
RUN apt remove -y libtbb-dev
RUN pip3 install inflect \     
     && pip3 install librosa==0.7.0
RUN pip3 install lws==1.2.6 \
     && pip3 install Markdown==3.1.1 \
     && pip3 install matplotlib==3.1.1 \
     && pip3 install multiprocess

RUN pip3 install sounddevice==0.3.13 \
     && pip3 install SoundFile==0.10.2 \
     && pip3 install tensorboardX==2.0 \
     && pip3 install tensorflow-estimator==1.13.0

RUN apt install -y libopenblas-base libomp-dev
RUN pip3 install tqdm \
     && pip3 install Unidecode \
     && pip3 install visdom \
     && pip3 install webrtcvad \
     && pip3 install youtube-dl 
RUN git clone https://github.com/facebookresearch/faiss.git
WORKDIR /tmp/faiss

RUN ./configure --with-cuda=/usr/local/cuda-10.0 --with-python=/usr/local/lib/python3.6
RUN make 
RUN apt install -y swig
RUN cp makefile.inc makefile.inc.temp
RUN sed "s/PYTHONCFLAGS.*/PYTHONCFLAGS=-I\/usr\/include\/python3.6\/ -I\/usr\/local\/lib\/python3.6\/site-packages\/numpy\/core\/include/" makefile.inc.temp > makefile.inc

RUN make SWIG=/usr/bin/swig PYTHON=/usr/bin/python3.6 -C python
RUN make SWIG=/usr/bin/swig PYTHON=/usr/bin/python3.6 -C python install 

WORKDIR /tmp
RUN rm -rf /tmp/faiss
RUN pip3 install gpumap 

RUN wget https://nvidia.box.com/shared/static/mmu3xb3sp4o8qg9tji90kkxl1eijjfc6.whl -O torch-1.1.0-cp36-cp36m-linux_aarch64.whl
RUN apt-get install -y libopenblas-base libopenmpi-dev 
RUN pip3 install torch-1.1.0-cp36-cp36m-linux_aarch64.whl

# Install the mosquito business
RUN pip3 install paho-mqtt

RUN pip3 install attrs==19.1.0
RUN apt-get install -y llvm-7 llvm-7
 

ENV LLVM_CONFIG /usr/bin/llvm-config-7
RUN pip3 install numba==0.49.1

RUN pip3 install tensorflow-estimator==1.15.1

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


