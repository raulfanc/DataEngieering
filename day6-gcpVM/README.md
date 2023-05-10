# Day 6 GCP

#### 1. Generating SSH keys refer to [link](https://cloud.google.com/compute/docs/connect/create-ssh-keys#create_an_ssh_key_pair)
#### 2. Creating a `virtual machine` on GCP --> `Metadata`(side bar) --> add `SSH key` (`cat` the public key in bash)
![](../Pictures/Pasted%20image%2020230505105036.png)
- select region, zone, machine type, boot disk
![](../Pictures/Pasted%20image%2020230505110018.png)
![](../Pictures/Pasted%20image%2020230505110219.png)

#### 3. Connecting to the VM with SSH key (in bash)
```bash
ssh -i ~/.ssh/gcp rex@<replace with the VM eternal ip from GCP>
```

![](../Pictures/Pasted%20image%2020230505111056.png)
```bash
htop
```
to check the machine in terminal
![](../Pictures/Pasted%20image%2020230505111150.png)

![](../Pictures/Pasted%20image%2020230505111319.png)
#### 4. Installing Anaconda on the GCP VM
- refer to anaconda installer [page](https://www.anaconda.com/download#downloads)
- `wget` to download the desired version: 64-bit(x86) in this case
```bash
wget https://repo.anaconda.com/archive/Anaconda3-2023.03-1-Linux-x86_64.sh
```
- `bash` to run the installer(have it installed)
```bash
bash Anaconda3-2023.03-1-Linux-x86_64.sh
```

![](../Pictures/Pasted%20image%2020230505112051.png)
if happy with the installation directory, press Enter.

#### 5. Creating SSH config file
- go to .ssh folder and `nano config` file, I've already had this file, if you dont, use `touch config` to create one.
```nano
Home gcp-de-learning            # alias name for easier access from SSH
    HostName <replace with the VM eternal ip from GCP>
    User rex
    IdentityFile ~/.ssh/gcp
```
- logout and login (when login, use `ssh <the alias of the Host in .ssh/config>`)
![](../Pictures/Pasted%20image%2020230505113715.png)
- validate the anacoda to see if working
![](../Pictures/Pasted%20image%2020230505114142.png)

#### 6. Accessing the remote machine with `Pycharm` and SSH remote, [link](https://www.jetbrains.com/help/pycharm/creating-a-remote-server-configuration.html)
![](../Pictures/Pasted%20image%2020230505115948.png)

![](../Pictures/Pasted%20image%2020230505131151.png)

#### 7. Installing Docker
- bash update the apt-get
```bash
sudo apt-get update
```
- install docker
```bash
sudo apt-get install docker.io
```
- check the docker version
```bash
docker --version
```
If encountering below:**following steps to run docker without sudo** [link](https://github.com/sindresorhus/guides/blob/main/docker-without-sudo.md)
![](../Pictures/Pasted%20image%2020230505122038.png)
- docker run 
```bash
docker run -it ubuntu bash
```

#### 8. Installing docker-compose
- download docker composer, go to docker's github releases page, [link](https://github.com/docker/compose/releases), download `docker-compose-linux-x86_64`
![](../Pictures/Pasted%20image%2020230505122542.png)
- run bash to install
```bash
wget https://github.com/docker/compose/releases/download/v2.17.3/docker-compose-linux-x86_64 -O docker-compose
```

- make the `docker-compose` file executable if it is not.
```bash
chmod +x docker-compose
```
![](../Pictures/Pasted%20image%2020230505123831.png)

![](../Pictures/Pasted%20image%2020230505123902.png)

- export to Path (to make it executable from anywhere), `nano ~/.bashrc`
```nano
export PATH="$[HOME}/bin:${PATH}"
```

- use `source .bashrc` to excute the change, otherwise have to restart the terminal to make the change work. see below, now we can do it anywhere.
![](../Pictures/Pasted%20image%2020230505125229.png)

**finally**, we can use the GCP machine to do the samething we did in day1 and day2, as long as we download the git from the github.
![](../Pictures/Pasted%20image%2020230505125513.png)

#### 9. Installing pgcli

#### 10. Port-forwarding with Pycharm: connecting to pgAdmin and Jupyter from the local computer
Use the following command to set up port forwarding for Jupyter. Replace `<username>`, `<path_to_private_key>`, and `<GCP_VM_IP>` with your specific values:
- Jupyter Notebook
```bash
ssh -i <path_to_private_key> -L 8888:localhost:8888 <username>@<GCP_VM_IP>
```

- Pgadmin
``` bash
ssh -i <path_to_private_key> -L 5432:localhost:5432 <username>@<GCP_VM_IP>
```

#### 11. Installing Terraform
```bash
# download terraform
wget https://releases.hashicorp.com/terraform/1.4.6/terraform_1.4.6_linux_amd64.zip
```

```bash
# install unzip
sudo apt-get install unzip
```

```bash
# unzip terraform.zip file
unzip terraform_1.4.6_linux_amd64.zip
```


#### 12. Using sftp for putting the credentials to the remote machine
since the `confidential file` and `variables.tf` file are not uploaded to git, we use `SFTP` to have files transftered to remote disk
![](../Pictures/Pasted%20image%2020230505150613.png)
- cd to where the files are located
```bash
cd /Users/admin/DataEngineer/DataEngeering/day5-terraform_gcp
```
- connect to SFTP
```bash
sftp gcp-de-learning
```
![](../Pictures/Pasted%20image%2020230505150736.png)

- create a folder to restore sensitive files
```bash
mkdir .gc
```
![](../Pictures/Pasted%20image%2020230505150922.png)

- paste file into the remote
```bash
put de-learning-20190409-89318d7d2315.json
```
![](../Pictures/Pasted%20image%2020230505151525.png)

- environment point to the json file
```bash
export GOOGLE_APPLICATION_CREDENTIALS="/home/rex/.gc/de-learning-20190409-89318d7d2315.json"
```
and then authenticate:
```bash
gcloud auth activate-service-account --key-file=$GOOGLE_APPLICATION_CREDENTIALS
```

![](../Pictures/Pasted%20image%2020230505152441.png)

**Finally**, from there, we can do samething again as [day5](../day5-terraform_gcp)

**Note**: see [terraform best practice with example](terraform_best_practice.md)
#### 13. Shutting down and removing the instance
either use bash or google cloud console to shut down
```bash
sudo shutdown now
```
when you shut down a Google Cloud Platform (GCP) VM instance and start it again later, the external IP address is likely to change if you are using an ephemeral IP address. Ephemeral external IP addresses are assigned to instances temporarily and can change when an instance is stopped and started again.

1. start the vm from gcp console 
2. nano the config file with the new ip address
3. then use ssh to connect the alias name again