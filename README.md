# Real-Time Lip Reading on a Jetson TX2
## W251 - Summer 2020 - Final Project
### Goter - Iftimie - Pflaum





#### Preparing GPU and Training Procedure for Personal Dataset
1. Requisition GPU from IBM Cloud Storage: For this step, we load from image a VS instance on a V100 GPU. This is done through the IBM Cloud Portal. Once recquisitioned we log on through our jump node with the following command: `ssh root@public.ip.address.of.vsi`
2. Harden the VSI: Modify security configuration to prohibit password login to root on our instance. 
- This is done by modifying the /etc/ssh/sshd_config file (using vi) in the following manner:
```
PermitRootLogin prohibit-password
PasswordAuthentication no
```
- Following the modification of the sshd_config file, restart the ssh daemon with the following command `service sshd restart`
3. The next step is to make sure our secondary disk with 2TB of storage is mounted properly. This is what we will use to hold our dockerfiles, image data and model checkpoints. If you started with an image that had Docker installed on a secondary disk, simply `ls /data`. You should see a 'docker' and a 'lost+found' directory. If you do not have your second disk mounted, proceed with the following: 
```
fdisk -l
mkdir -m 777 /data
mkfs.ext4 /dev/xvdc

# edit /etc/fstab and all this line:
/dev/xvdc /data                   ext4    defaults,noatime        0 0

mount /data

service docker stop
cd /var/lib
cp -r docker /data
rm -fr docker
ln -s /data/docker ./docker
service docker start

docker run hello-world
```
4. Install s3fs-fuse to connect to object storage. In order to do this, simply follow the commands below:

```
sudo apt-get update
sudo apt-get install -y automake autotools-dev g++ git libcurl4-openssl-dev libfuse-dev libssl-dev libxml2-dev make pkg-config
git clone https://github.com/s3fs-fuse/s3fs-fuse.git
ls
cd s3fs-fuse
./autogen.sh
./configure
make
sudo make install

Substitue your values for <Access_Key_ID> and <Secret_Access_Key> in the below command.
echo " <Access_Key_ID>:<Secret_Access_Key>" > $HOME/.cos_creds
chmod 600 $HOME/.cos_creds

# /mnt/jlrdata is location of mounted object storage
# jlrdata is name of bucket in cloud storage
# Change endpoint depending on where your data is stored
sudo mkdir -m 777 /mnt/jlrdata
sudo s3fs jlrdata /mnt/jlrdata -o passwd_file=$HOME/.cos_creds -o sigv2 -o use_path_request_style -o url=https://s3.us-east.objectstorage.softlayer.net
```
If this is done correctly, a `ls /mnt/jlrdata` will list the contents of the jlrdata bucket in object store.
5. Copy data from object store to secondary disk (this will take a while if you have a lot of files):
```
rsync -rP /mnt/jlrdata/preprocessed /data/
cp /mnt/jlrdata/*.txt /data/
```
6. Clone this repository: `git clone https://github.com/tomgoter/jetson_lip_reading.git`
7. Create the docker image for training. This will install all requirements and clone the original Lip2Wav Repository. 
```
cd jetson_lip_reading
docker build -t jlrapp -f dockerfiles/Dockerfile.lip_reading .

# Check image exists
docker image ls
```
8. Launch the docker container interactively in a bash shell, with gpu support, passing in our second disk, object store, and exposing port 6006 to enable use of tensorboard.
```
docker run --rm -it --runtime=nvidia -v /root/jetson_lip_reading:/jetson_lip_reading -v /mnt/jlrdata:/jlrdata -v /data:/data -p 6006:6006 jlrapp bash
```
9a. Train from Scratch (write model checkpoints to secondary disk
```
python train.py baseline --data_root /jlrdata/ --preset synthesizer/presets/tom.json --restore False --models_dir /data/saved_models
```
9b. Restart training (write model checkpoints to secondary disk). First update the eval checkpoint path in the synthesizer/hparams file then
```
python train.py <new_model_name> --data_root /jlrdata/ --preset synthesizer/presets/tom.json --restore True --models_dir /data/saved_models
```
