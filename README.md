# Real-Time Lip Reading on a Jetson TX2
## W251 - Summer 2020 - Final Project
### Goter - Iftimie - Pflaum





#### Training Procedure for Personal Dataset
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
echo "9160f42c3afb425b95c81461b099c255:89522e8d17448890f9d004fcea1bffb04ed0a2dbf7c1645b" > $HOME/.cos_creds
chmod 600 $HOME/.cos_creds

sudo mkdir -m 777 /mnt/jlrdata
sudo s3fs jlrdata /mnt/jlrdata -o passwd_file=$HOME/.cos_creds -o sigv2 -o use_path_request_style -o url=https://s3.us-east.objectstorage.softlayer.net
```
