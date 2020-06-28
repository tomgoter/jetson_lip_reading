FROM ubuntu:18.04

# Following docker file from w251/keras - started with install of unbuntu
ARG URL=http://169.44.201.108:7002/jetpacks/4.3

ENV DEBIAN_FRONTEND=noninteractive

RUN apt-get update \
 && apt-get install -y qemu-user-static gnupg2 apt-utils \
                       lbzip2 curl sudo unp python python3 \
                       libegl1 libx11-6 libxext6 libgles2 \
                       libwayland-egl1 libxkbcommon0 libasound2 \
                       libglib2.0 libgstreamer1.0 libgstreamer-plugins-bad1.0 \
                       libgstreamer-plugins-base1.0 libevdev2 libinput10 \
                       libunwind8 device-tree-compiler

WORKDIR /tmp
RUN curl -sL $URL/Jetson_Linux_R32.3.1_aarch64.tbz2 | tar xvfj -
RUN chown root /etc/passwd /etc/sudoers /usr/lib/sudo/sudoers.so /etc/sudoers.d/README
RUN sed -i "s/LDK_NV_TEGRA_DIR}\/config.tbz2/LDK_NV_TEGRA_DIR}\/config.tbz2 --exclude=etc\/hosts --exclude=etc\/hostname/g"  /tmp/Linux_for_Tegra/apply_binaries.sh
RUN sed -i 's/install --owner=root --group=root "${QEMU_BIN}"/#install --owner=root --group=root "${QEMU_BIN}"/g' /tmp/Linux_for_Tegra/nv_tegra/nv-apply-debs.sh
RUN sed -i 's/LC_ALL=C chroot . mount -t proc/#LC_ALL=C chroot . mount -t proc/g' /tmp/Linux_for_Tegra/nv_tegra/nv-apply-debs.sh
RUN sed -i 's/umount ${L4T_ROOTFS_DIR}\/proc/#umount ${L4T_ROOTFS_DIR}\/proc/g' /tmp/Linux_for_Tegra/nv_tegra/nv-apply-debs.sh
RUN /tmp/Linux_for_Tegra/apply_binaries.sh -r / && rm -fr /tmp/*
RUN rm /etc/apt/sources.list.d/nvidia-l4t-apt-source.list
RUN curl $URL/cuda-repo-l4t-10-0-local-10.0.326_1.0-1_arm64.deb -so cuda-repo-l4t_arm64.deb
RUN curl $URL/libcudnn7_7.6.3.28-1+cuda10.0_arm64.deb -so libcudnn_arm64.deb
RUN curl $URL/libcudnn7-dev_7.6.3.28-1+cuda10.0_arm64.deb -so libcudnn-dev_arm64.deb
RUN dpkg -i /tmp/cuda-repo-l4t_arm64.deb
RUN apt-key add /var/cuda-repo-10-0-local-10.0.326/7fa2af80.pub
RUN apt-get update && apt-get install -y cuda-toolkit-10.0
RUN dpkg -i /tmp/libcudnn_arm64.deb
RUN dpkg -i /tmp/libcudnn-dev_arm64.deb
RUN apt-get update
RUN apt-get install -y libxext-dev libx11-dev x11proto-gl-dev git automake autoconf libtool python pkg-config
RUN git clone https://github.com/NVIDIA/libglvnd.git
WORKDIR /tmp/libglvnd
RUN ./autogen.sh
RUN ./configure
RUN make -j 6
RUN make install
RUN rm -fr /tmp/libglvnd
WORKDIR /
RUN rm -f /usr/lib/aarch64-linux-gnu/libGL.so
RUN ln -s /usr/lib/aarch64-linux-gnu/libGLU.so /usr/lib/aarch64-linux-gnu/libGL.so
RUN ln -s /usr/lib/aarch64-linux-gnu/libcuda.so /usr/lib/aarch64-linux-gnu/libcuda.so.1
RUN ln -s /usr/lib/aarch64-linux-gnu/tegra/libnvidia-ptxjitcompiler.so.32.3.1 /usr/lib/aarch64-linux-gnu/tegra/libnvidia-ptxjitcompiler.so.1
ENV LD_LIBRARY_PATH=:/usr/lib/aarch64-linux-gnu/tegra
ENV PATH=/usr/local/cuda-10.0/bin:/usr/local/sbin:/usr/local/bin:/usr/sbin:/usr/bin:/sbin:/bin
RUN apt -y autoremove
RUN rm -f /tmp/*.deb
WORKDIR /tmp
RUN apt update
RUN  curl $URL/libnvinfer6_6.0.1-1+cuda10.0_arm64.deb -so /tmp/libnvinfer6_6.0.1-1+cuda10.0_arm64.deb
RUN curl $URL/libnvinfer-dev_6.0.1-1+cuda10.0_arm64.deb -so /tmp/libnvinfer-dev_6.0.1-1+cuda10.0_arm64.deb
RUN curl $URL/libnvinfer-samples_6.0.1-1+cuda10.0_all.deb -so /tmp/libnvinfer-samples_6.0.1-1+cuda10.0_all.deb
RUN curl $URL/tensorrt_6.0.1.10-1+cuda10.0_arm64.deb -so /tmp/tensorrt_6.0.1.10-1+cuda10.0_arm64.deb
RUN curl $URL/python3-libnvinfer_6.0.1-1+cuda10.0_arm64.deb -so /tmp/python3-libnvinfer_6.0.1-1+cuda10.0_arm64.deb
RUN curl $URL/python3-libnvinfer-dev_6.0.1-1+cuda10.0_arm64.deb -so /tmp/python3-libnvinfer-dev_6.0.1-1+cuda10.0_arm64.deb
RUN curl $URL/libnvinfer-plugin6_6.0.1-1+cuda10.0_arm64.deb -so /tmp/libnvinfer-plugin6_6.0.1-1+cuda10.0_arm64.deb
RUN curl $URL/libnvinfer-plugin-dev_6.0.1-1+cuda10.0_arm64.deb -so /tmp/libnvinfer-plugin-dev_6.0.1-1+cuda10.0_arm64.deb
RUN curl $URL/libnvparsers6_6.0.1-1+cuda10.0_arm64.deb -so /tmp/libnvparsers6_6.0.1-1+cuda10.0_arm64.deb
RUN curl $URL/libnvparsers-dev_6.0.1-1+cuda10.0_arm64.deb -so /tmp/libnvparsers-dev_6.0.1-1+cuda10.0_arm64.deb
RUN curl $URL/libnvonnxparsers6_6.0.1-1+cuda10.0_arm64.deb -so /tmp/libnvonnxparsers6_6.0.1-1+cuda10.0_arm64.deb
RUN curl $URL/libnvonnxparsers-dev_6.0.1-1+cuda10.0_arm64.deb -so /tmp/libnvonnxparsers-dev_6.0.1-1+cuda10.0_arm64.deb
RUN curl $URL/libnvinfer-doc_6.0.1-1+cuda10.0_all.deb -so /tmp/libnvinfer-doc_6.0.1-1+cuda10.0_all.deb
RUN curl $URL/libnvinfer-bin_6.0.1-1+cuda10.0_arm64.deb -so /tmp/libnvinfer-bin_6.0.1-1+cuda10.0_arm64.deb
RUN apt install -y /tmp/*.deb
RUN apt install -y tensorrt 
RUN rm /tmp/*.deb
RUN rm -fr /tmp/* /var/cache/apt/* && apt-get clean
RUN apt update && apt install -y python3-pip
RUN apt install -y libhdf5-serial-dev hdf5-tools libhdf5-dev zlib1g-dev zip libjpeg8-dev
RUN pip3 install Cython
RUN pip3 install -U numpy==1.16.1 future==0.17.1 mock==3.0.5 h5py==2.9.0 keras_preprocessing==1.0.5 keras_applications==1.0.8 gast==0.2.2 enum34 futures protobuf
RUN pip3 uninstall -y enum34
RUN pip3 install -U pip
RUN pip3 install --pre --extra-index-url https://developer.download.nvidia.com/compute/redist/jp/v43 "tensorflow-gpu<2"
RUN apt update
RUN apt install -y libsm6 libxext6 libxrender-dev libgtk2.0-dev libavcodec-dev libavformat-dev libswscale-dev wget
RUN apt install -y python3-sklearn
RUN pip3 install keras
RUN apt-get update && apt install -y build-essential cmake unzip

# Get the Open CV Libraries
RUN curl $URL/libopencv_3.3.1-2-g31ccdfe11_arm64.deb  -so libopencv_3.3.1-2-g31ccdfe11_arm64.deb
RUN curl $URL/libopencv-dev_3.3.1-2-g31ccdfe11_arm64.deb -so libopencv-dev_3.3.1-2-
RUN curl $URL/libopencv-python_3.3.1-2-g31ccdfe11_arm64.deb -so libopencv-python_3.3.1-2-g31ccdfe11_arm64.deb
RUN apt remove -y libopencv-calib3d-dev libopencv-core-dev
RUN apt install -y libcanberra-gtk-module libcanberra-gtk3-module libv4l-dev
RUN apt update
RUN dpkg -i *.deb
RUN rm -f /tmp/*.deb

# This is where the Lip2Wav specific install starts
RUN apt install -y software-properties-common \
  && apt install -y ffmpeg \
  && apt-get install -y llvm-7 llvm-7  

ENV LLVM_CONFIG /usr/bin/llvm-config-7
RUN apt remove -y libtbb-dev
RUN pip3 install numba==0.49.1

# Install PIP and numpy and cython
RUN pip3 install --upgrade pip 
RUN pip3 install -U py-cpuinfo psutil portpicker requests astor termcolor wrapt google-pasta
RUN apt-get install -y python3-pyqt5
RUN apt-get install -y gfortran libatlas-base-dev libfreetype6-dev
RUN apt-get update
RUN pip3 install -U pesq==0.0.1 pystoi==0.2.2 scipy==1.3.0 
RUN pip3 install --ignore-installed joblib

RUN pip3 install inflect \     
     && pip3 install librosa==0.7.0
RUN pip3 install lws==1.2.6 \
     && pip3 install Markdown==3.1.1 \
     && pip3 install matplotlib==3.1.1 \
     && pip3 install multiprocess
RUN pip3 install sounddevice==0.3.13 \
     && pip3 install SoundFile==0.10.2 \
     && pip3 install tensorboardX==2.0 \
     && pip3 install tensorflow-estimator==1.15.1
RUN pip3 install tqdm \
     && pip3 install Unidecode \
     && pip3 install visdom \
     && pip3 install webrtcvad \
     && pip3 install youtube-dl 

# This is necessary to get to umap-learn or gpumap but is not needed for inference.
#RUN git clone https://github.com/facebookresearch/faiss.git

# This is needed for the gpumap - but not available on apt
#WORKDIR /tmp/faiss

#RUN ./configure --with-cuda=/usr/local/cuda-10.0 --with-python=/usr/local/lib/python3.6
#RUN make 
#RUN apt install -y swig
#RUN cp makefile.inc makefile.inc.temp
#RUN sed "s/PYTHONCFLAGS.*/PYTHONCFLAGS=-I\/usr\/include\/python3.6\/ -I\/usr\/local\/lib\/python3.6\/site-packages\/numpy\/core\/include/" makefile.inc.temp > makefile.inc

#RUN make SWIG=/usr/bin/swig PYTHON=/usr/bin/python3.6 -C python
#RUN make SWIG=/usr/bin/swig PYTHON=/usr/bin/python3.6 -C python install 

#WORKDIR /tmp
#RUN rm -rf /tmp/faiss
#RUN pip3 install gpumap 

# Torch only used for face detection during preprocessing. May not need for inference.
RUN wget https://nvidia.box.com/shared/static/mmu3xb3sp4o8qg9tji90kkxl1eijjfc6.whl -O torch-1.1.0-cp36-cp36m-linux_aarch64.whl
RUN pip3 install torch-1.1.0-cp36-cp36m-linux_aarch64.whl

# Install the mosquito business
RUN pip3 install paho-mqtt

RUN pip3 install attrs==19.1.0

# Install profiler https://pypi.org/project/profilehooks/
RUN pip3 install profilehooks

# Change working directory
WORKDIR /

# Add CUDA to PATH
ENV PATH $PATH:/usr/local/cuda-10.0/bin

#
RUN ldconfig
