# Real-Time Lip Reading on a Jetson TX2
## W251 - Summer 2020 - Final Project
### Goter - Iftimie - Pflaum





### Preparing GPU and Training Procedure for Personal Dataset
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
9. Train the model
 - From Scratch (write model checkpoints to secondary disk)
```
python train.py <model_name> --data_root /jlrdata/ --preset synthesizer/presets/tom.json --restore False --models_dir /data/saved_models
# Additional Command Line Options
    --mode, default="synthesis", help="mode for synthesis of tacotron after training") 
    --GTA, default="True", help="Ground truth aligned synthesis, defaults to True, only considered in Tacotron synthesis mode")
    --summary_interval", type=int, default=2500, help="Steps between running summary ops")
    --embedding_interval, type=int, default=1000000000, help="Steps between updating embeddings projection visualization")
    --checkpoint_interval, type=int, default=1000, help="Steps between writing checkpoints")
    --eval_interval, type=int, default=1000, help="Steps between eval on test data")
    --tacotron_train_steps, type=int, default=100000, help="total number of tacotron training steps")
    --tf_log_level, type=int, default=1, help="Tensorflow C++ log level.")
# Note other training parameters such as teacher forcing options controlled in synthesizer/hparams.py file.
```
- Restart training (write model checkpoints to secondary disk). First update the eval checkpoint path in the synthesizer/hparams file then
```
python train.py <new_model_name> --data_root /jlrdata/ --preset synthesizer/presets/tom.json --restore True --models_dir /data/saved_models
```
10. Monitor with tensorboard
- Log into the same VSI using another terminal.
- Jump into the docker container with `docker exec -ti jlrapp /bin/bash`
- Run tensorboard `tensorboard --logdir=/data/saved_models/logs-<model_name>`
- Use public ip with port 6006 to view in browser window
11. Following or during training copy desired checkpoint files to object store for eventual use in inference
`cp /data/saved_models/logs-<model_name>/tacotron_pretrained/tacotron*<step_number>* /jlrdata/<folder for model>`

### Inference on Jetson
1. Download model from object store and save to backup disk on jetson (i.e., '/data'): refer to the path to this model as <model_path>
2. Download test data from object store (if not already present) and save to backup disk on jetson (i.e., '/data'). This should include the preprocessed folder and all of the subfolders for the videos listed in test.txt. Record the path to the root directory (directory which contains test.txt and preprocessed/) as <data_path>
3. Clone this respository `git clone https://github.com/tomgoter/jetson_lip_reading.git`
3. Create docker image for inference (if not already existing): 
```
cd /path/to/jetson_lip_reading
docker build -t jlr -f dockerfiles/JLRTF1_scratch.Dockerfile .`
```
4. Run docker image interactively:
```
docker run --rm --privileged -v /home/tom/w251/jetson_lip_reading:/jetson_lip_reading -v /data:/data -ti jlr bash
```
5. From with in the docker container, run the inference as:
```
python3 complete_test_generate_tpg.py -d <data_path> -r <output_path> --checkpoint <model_path> --preset synthesizer/presets/tom.json
#
Example for chemistry speaker: 
python3 complete_test_generate_tpg.py \
             -d /data/jlr_data/chem \
             -r /data/jlr_data/chem \
             --checkpoint /data/jlr_model/chem/tacotron_model.ckpt-159000 \
             --preset synthesizer/presets/chem.json
```
**Note** The above example uses the complete_test_generate_tpg.py script for inference which uses tensorflow to perform the MEL-to-WAV inversion, as opposed to doing this with Librosa. This was implemented to reduce inference time on the Jetson.
