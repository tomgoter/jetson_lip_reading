# Real-Time Lip Reading on a Jetson TX2
## W251 - Summer 2020 - Final Project
### Goter - Iftimie - Pflaum





#### Training Procedure for Personal Dataset
1. Requisition GPU from IBM Cloud Storage: For this step, we load from image a VS instance on a V100 GPU. This is done through the IBM Cloud Portal. Once recquisitioned we log on through our jump node with the following command: `ssh root@public.ip.address.of.vsi`
2. Harden the VSI: Modify security configuration to prohibit password login to root on our instance. 
- This is done by modifying the /etc/ssh/sshd_config file (using vi) in the following manner:
`PermitRootLogin prohibit-password
PasswordAuthentication no`
- Following the modification of the sshd_config file, restart the ssh daemon with the following command `service sshd restart`
3. The next step is to make sure our secondary disk with 2TB of storage is mounted properly. This is what we will use to hold our dockerfiles, image data and model checkpoints. If you started with an image that had Docker installed on a secondary disk, simply `ls /data`. You should see a 'docker' and a 'lost+found' directory. If you do not have your second disk mounted, proceed with the following: 
```fdisk -l
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

docker run hello-world```
