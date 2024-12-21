sudo apt-get update
sudo apt-get upgrade -y
docker
pwd
ls
scp -i '/Users/gimgeon/Documents/gun/coding/suno-homebrew/newkey.pem' -r /Users/gimgeon/Documents/gun/coding/suno-homebrew/* ubuntu@52.78.115.224:/home/ubuntu/
exit
docker
sudo apt-get install -y git
sudo apt-get install -y docker.io
sudo usermod -aG docker $USER
sudo apt-get install -y nvidia-container-toolkit
sudo systemctl restart docker
newgrp docker
exit
ㄷ턋
exit
docker ps
ls
df -hT
sudo resize2fs /dev/root
df -hT
sudo resize2fs /dev/root
lsblk
sudo growpart /dev/nvme0n1 1
sudo resize2fs /dev/nvme0n1p1
df -h
docker build -t suno-homebrew .
docker run --gpus all suno-homebrew
docker ps
docker run --gpus all suno-homebrew
nvidia-smi
# NVIDIA Container Toolkit 설치
distribution=$(. /etc/os-release;echo $ID$VERSION_ID)     && curl -fsSL https://nvidia.github.io/libnvidia-container/gpgkey | sudo gpg --dearmor -o /usr/share/keyrings/nvidia-container-toolkit-keyring.gpg     && curl -s -L https://nvidia.github.io/libnvidia-container/$distribution/libnvidia-container.list |     sed 's#deb https://#deb [signed-by=/usr/share/keyrings/nvidia-container-toolkit-keyring.gpg] https://#g' |     sudo tee /etc/apt/sources.list.d/nvidia-container-toolkit.list
sudo apt-get update
sudo apt-get install -y nvidia-container-toolkit
sudo nvidia-ctk runtime configure --runtime=docker
sudo systemctl restart docker
docker run --gpus all suno-homebrew
nvidia-smi
lspci | grep -i nvidia
sudo apt update
sudo apt install -y ubuntu-drivers-common
ubuntu-drivers devices
ls
# NVIDIA 패키지 저장소 설정
curl -fsSL https://nvidia.github.io/libnvidia-container/gpgkey | sudo gpg --dearmor -o /usr/share/keyrings/nvidia-container-toolkit-keyring.gpg
curl -s -L https://nvidia.github.io/libnvidia-container/stable/deb/nvidia-container-toolkit.list |     sed 's#deb https://#deb [signed-by=/usr/share/keyrings/nvidia-container-toolkit-keyring.gpg] https://#g' |     sudo tee /etc/apt/sources.list.d/nvidia-container-toolkit.list
# 패키지 업데이트 및 설치
sudo apt-get update
sudo apt-get install -y nvidia-container-toolkit
sudo nvidia-ctk runtime configure --runtime=docker
sudo systemctl restart docker
sudo ubuntu-drivers autoinstall
sudo reboot
docker ps
nvidia smi
nvidia-smi
docker run --gpus all suno-homebrew
docker ps
docker container
docker container ls
docker run --gpus all suno-homebrew
docker build -t suno-homebrew .
docker run --gpus all suno-homebrew
docker ps
docker stop 92aaa23ab6fd
docker ps
docker run -d --gpus all suno-homebrew
docker ps
docker build -t suno-homebrew .
docker run -d --gpus all -v /home/ubuntu/your_project:/app suno-homebrew
docker ps
docker logs -f 2ce5b4c93249
docker ps
docker stop 2ce5b4c93249
docker build -t suno-homebrew .
docker ps
docker run -d --gpus all -v /home/ubuntu/your_project:/app suno-homebrew
docker ps
docker run --gpus all -v /home/ubuntu/your_project:/app suno-homebrew
docker build -t suno-homebrew .
docker run --gpus all -v /home/ubuntu/your_project:/app suno-homebrew
docker build -t suno-homebrew .
docker ps
docker run --gpus all -v /home/ubuntu:/app suno-homebrew
docker build -t suno-homebrew .
docker run --gpus all -v /home/ubuntu:/app suno-homebrew
docker run --gpus all -p 8000:8000 -v /home/ubuntu:/app suno-homebrew
docker build -t suno-homebrew .
docker run --gpus all -p 8000:8000 -v /home/ubuntu:/app suno-homebrew
pwd
ls
cd temp
ls
cd test/
ls
docker run --gpus all -p 8000:8000   -v /home/ubuntu:/app   -v /app/rvc_models   suno-homebrew
docker ps
docker logs -f 0dab0f1ad8ea
docker run --gpus all -p 8000:8000   -v /home/ubuntu:/app   -v /app/rvc_models   suno-homebrew
docker ps
docker logs -f 0dab0f1ad8ea
docker ps
docker stop 0dab0f1ad8ea
docker run --gpus all -p 8000:8000 -v /home/ubuntu:/app suno-homebrew
docker run --gpus all -p 8000:8000   -v /home/ubuntu:/app   -v /app/rvc_models   suno-homebrew
docker ps
docker run --gpus all -p 8000:8000   -v /home/ubuntu:/app   -v /app/rvc_models   -e PYTHONUNBUFFERED=1 \  # 이 줄 추가
docker run --gpus all -p 8000:8000   -v /home/ubuntu:/app   -v /app/rvc_models   -e PYTHONUNBUFFERED=1 \ 
docker run --gpus all -p 8000:8000   -v /home/ubuntu:/app   -v /app/rvc_models   -e PYTHONUNBUFFERED=1   suno-homebrew
docker build -t suno-homebrew .
docker ps
docker build -t suno-homebrew .
docker run --gpus all -p 8000:8000   -v /home/ubuntu:/app   -v /app/rvc_models   -e PYTHONUNBUFFERED=1   suno-homebrew
docker build -t suno-homebrew .
docker run --gpus all -p 8000:8000   -v /home/ubuntu:/app   -v /app/rvc_models   -e PYTHONUNBUFFERED=1   suno-homebrew
docker build -t suno-homebrew .
docker run --gpus all -p 8000:8000   -v /home/ubuntu:/app   -v /app/rvc_models   -e PYTHONUNBUFFERED=1   suno-homebrew
docker rmi f87d24b95b1a a3d11948d64e ecec336815b6 18771bdfd59f 8e84ccaa7dd6 913082d3d280 18a8dfc04ba7 db808eab7c7b 0cdc28956489 6e482ed01480 a9ca1bd83932 ab69d50beea9 20740366c5e9
docker build -t suno-homebrew .
docker run --gpus all -p 8000:8000   -v /home/ubuntu:/app   -v /app/rvc_models   -e PYTHONUNBUFFERED=1   suno-homebrew
docker build -t suno-homebrew .
docker run --gpus all -p 8000:8000   -v /home/ubuntu:/app   -v /app/rvc_models   -e PYTHONUNBUFFERED=1   suno-homebrew
docker build -t suno-homebrew .
docker build -t suno-homebrew .
docker img ls
docker image ls
docker rmi f87d24b95b1a a3d11948d64e ecec336815b6 18771bdfd59f 8e84ccaa7dd6 913082d3d280 18a8dfc04ba7 db808eab7c7b 0cdc28956489 6e482ed01480 a9ca1bd83932 ab69d50beea9 20740366c5e9
docker rm $(docker ps -a -q)
docker run --gpus all -p 8000:8000   -v /home/ubuntu:/app   -v /app/rvc_models   -e PYTHONUNBUFFERED=1   suno-homebrew
docker image ls
docker build -t suno-homebrew .
docker system prune -a
docker build -t suno-homebrew .
docker run --gpus all -p 8000:8000   -v /home/ubuntu:/app   -v /app/rvc_models   -e PYTHONUNBUFFERED=1   suno-homebrew
docker build -t suno-homebrew .
docker system prune -a
docker build -t suno-homebrew .
docker run --gpus all -p 8000:8000   -v /home/ubuntu:/app   -v /app/rvc_models   -e PYTHONUNBUFFERED=1   suno-homebrew
docker system prune -a
docker build -t suno-homebrew .
docker run --gpus all -p 8000:8000   -v /home/ubuntu:/app   -v /app/rvc_models   -e PYTHONUNBUFFERED=1   suno-homebrew
docker build -t suno-homebrew .
docker system prune -a
docker build -t suno-homebrew .
docker run --gpus all -p 8000:8000   -v /home/ubuntu:/app   -v /app/rvc_models   -e PYTHONUNBUFFERED=1   suno-homebrew
docker build -t suno-homebrew .
docker run --gpus all -p 8000:8000   -v /home/ubuntu:/app   -v /app/rvc_models   -e PYTHONUNBUFFERED=1   suno-homebrew
docker build -t suno-homebrew .
docker run --gpus all -p 8000:8000   -v /home/ubuntu:/app   -v /app/rvc_models   -e PYTHONUNBUFFERED=1   suno-homebrew
docker build -t suno-homebrew .
docker run --gpus all -p 8000:8000   -v /home/ubuntu:/app   -v /app/rvc_models   -e PYTHONUNBUFFERED=1   suno-homebrew
docker ps
docker stop 6eefe7684bfe
docker run --gpus all -p 8000:8000   -v /home/ubuntu:/app   -v /app/rvc_models   -e PYTHONUNBUFFERED=1   suno-homebrew
docker ps
docker stop a4dcbc502317
docker run --gpus all -p 8000:8000   -v /home/ubuntu:/app   -v /app/rvc_models   -e PYTHONUNBUFFERED=1   suno-homebrew
export CUDA_VISIBLE_DEVICES=0
docker run --gpus all ...
docker run --gpus all -p 8000:8000   -v /home/ubuntu:/app   -v /app/rvc_models   -e PYTHONUNBUFFERED=1   suno-homebrewexport CUDA_VISIBLE_DEVICES=0
docker run --gpus all     -p 8000:8000     -v /home/ubuntu:/app     -v /app/rvc_models     -e PYTHONUNBUFFERED=1     -e CUDA_VISIBLE_DEVICES=0     suno-homebrew
docker ps
docker stop 3fca16a952c1
docker build -t suno-homebrew .
docker run --gpus all     -p 8000:8000     -v /home/ubuntu:/app     -v /app/rvc_models     -e PYTHONUNBUFFERED=1     -e CUDA_VISIBLE_DEVICES=0     suno-homebrew
docker build -t suno-homebrew .
docker system prune -a
docker build -t suno-homebrew .
docker run --gpus all     -p 8000:8000     -v /home/ubuntu:/app     -v /app/rvc_models     -e PYTHONUNBUFFERED=1     -e CUDA_VISIBLE_DEVICES=0     suno-homebrew
docker build -t suno-homebrew .
docker run --gpus all     -p 8000:8000     -v /home/ubuntu:/app     -v /app/rvc_models     -e PYTHONUNBUFFERED=1     -e CUDA_VISIBLE_DEVICES=0     suno-homebrew
docker ps
docker stop 683fc23eafc8
docker build -t suno-homebrew .
docker run --gpus all -p 8000:8000   -v /home/ubuntu:/app   -v /app/rvc_models   -e PYTHONUNBUFFERED=1   suno-homebrew
docker build -t suno-homebrew .
docker system prune --filter "until=24h" --volumes --filter "label!=cache"
docker container prune
docker image prune
docker build -t suno-homebrew .
docker image ps
docker image ls
df -h
lsblk
sudo fdisk -l
docker ps
docker stop 739d893eeb8c
df -h
lsblk
sudo growpart /dev/nvme1n1 1
sudo resize2fs /dev/nvme1n1p1
docker ps
docker stop d75d05aa34a1
df -h
docker build -t suno-homebrew .
docker run --gpus all     -p 8000:8000     -v /home/ubuntu:/app     -v /app/rvc_models     -e PYTHONUNBUFFERED=1     -e CUDA_VISIBLE_DEVICES=0     suno-homebrew
docker ps
docker build -t suno-homebrew .
docker system prune -a
docker build -t suno-homebrew .
docker run --gpus all     -p 8000:8000     -v /home/ubuntu:/app     -v /app/rvc_models     -e PYTHONUNBUFFERED=1     -e CUDA_VISIBLE_DEVICES=0     suno-homebrew
docker run --gpus all     -p 8000:8000     -v /home/ubuntu:/app     -v /app/rvc_models     -e PYTHONUNBUFFERED=1     -e CUDA_VISIBLE_DEVICES=0     suno-homebrew
docker build -t suno-homebrew .
docker run --gpus all     -p 8000:8000     -v /home/ubuntu:/app     -v /app/rvc_models     -e PYTHONUNBUFFERED=1     -e CUDA_VISIBLE_DEVICES=0     suno-homebrew
docker build -t suno-homebrew .
docker run --gpus all     -p 8000:8000     -v /home/ubuntu:/app     -v /app/rvc_models     -e PYTHONUNBUFFERED=1     -e CUDA_VISIBLE_DEVICES=0     suno-homebrew
curl -s https://registry.hub.docker.com/v2/repositories/nvidia/cuda/tags?page_size=100 | grep -i "12.1.*ubuntu22.04"
docker pull nvidia/cuda:12.1.0-base-ubuntu22.04
docker pull nvidia/cuda:12.1.0-cudnn9-devel-ubuntu22.04
docker build -t suno-homebrew .
docker run --gpus all     -p 8000:8000     -v /home/ubuntu:/app     -v /app/rvc_models     -e PYTHONUNBUFFERED=1     -e CUDA_VISIBLE_DEVICES=0     suno-homebrew
docker ps
docker stop 9e58530e5595
docker ps
docker run --gpus all     -p 8000:8000     -v /home/ubuntu:/app     -v /app/rvc_models     -e PYTHONUNBUFFERED=1     -e CUDA_VISIBLE_DEVICES=0     suno-homebrew
docker ps
docker run --gpus all     --shm-size=8g     -p 8000:8000     -v /home/ubuntu/data:/app/data     -v /home/ubuntu/models:/app/models     -v /home/ubuntu/temp:/app/temp     -e PYTHONUNBUFFERED=1     -e CUDA_VISIBLE_DEVICES=0     --ipc=host     suno-homebrew
docker system prune -a
docker build -t suno-homebrew .
docker run --gpus all     --shm-size=8g     -p 8000:8000     -v /home/ubuntu/data:/app/data     -v /home/ubuntu/models:/app/models     -v /home/ubuntu/temp:/app/temp     -e PYTHONUNBUFFERED=1     -e CUDA_VISIBLE_DEVICES=0     --ipc=host     suno-homebrew
docker ps
docker stop 8dbc3b87981c
docker run --gpus all     --shm-size=8g     -p 8000:8000     -v /home/ubuntu/data:/app/data     -v /home/ubuntu/models:/app/models     -v /home/ubuntu/temp:/app/temp     -e PYTHONUNBUFFERED=1     -e CUDA_VISIBLE_DEVICES=0     --ipc=host     suno-homebrew
docker build -t suno-homebrew .
docker run --gpus all     --shm-size=8g     -p 8000:8000     -v /home/ubuntu/data:/app/data     -v /home/ubuntu/models:/app/models     -v /home/ubuntu/temp:/app/temp     -e PYTHONUNBUFFERED=1     -e CUDA_VISIBLE_DEVICES=0     --ipc=host     suno-homebrew
docker ps
docker stop b11bd15bdb80
docker build -t suno-homebrew .
docker run --gpus all     --shm-size=8g     -p 8000:8000     -v /home/ubuntu/data:/app/data     -v /home/ubuntu/models:/app/models     -v /home/ubuntu/temp:/app/temp     -e PYTHONUNBUFFERED=1     -e CUDA_VISIBLE_DEVICES=0     --ipc=host     suno-homebrew
docker build -t suno-homebrew .
docker run --gpus all     --shm-size=8g     -p 8000:8000     -v /home/ubuntu/data:/app/data     -v /home/ubuntu/models:/app/models     -v /home/ubuntu/temp:/app/temp     -e PYTHONUNBUFFERED=1     -e CUDA_VISIBLE_DEVICES=0     --ipc=host     suno-homebrew
docker build -t suno-homebrew .
docker run --gpus all     --shm-size=8g     -p 8000:8000     -v /home/ubuntu/data:/app/data     -v /home/ubuntu/models:/app/models     -v /home/ubuntu/temp:/app/temp     -e PYTHONUNBUFFERED=1     -e CUDA_VISIBLE_DEVICES=0     --ipc=host     suno-homebrew
docker ps
docker logs -f 98d820994d69
docker stop 98d820994d69
docker run --gpus all     --shm-size=8g     -p 8000:8000     -v /home/ubuntu/data:/app/data     -v /home/ubuntu/models:/app/models     -v /home/ubuntu/temp:/app/temp     -e PYTHONUNBUFFERED=1     -e CUDA_VISIBLE_DEVICES=0     --ipc=host     suno-homebrew
docker ps
docker stop 959cec28d5c0
docker build -t suno-homebrew .
docker system prune -a
docker build -t suno-homebrew .
docker run --gpus all     --shm-size=8g     -p 8000:8000     -v /home/ubuntu/data:/app/data     -v /home/ubuntu/models:/app/models     -v /home/ubuntu/temp:/app/temp     -e PYTHONUNBUFFERED=1     -e CUDA_VISIBLE_DEVICES=0     --ipc=host     suno-homebrew
docker ps
docker stop de3345082759
docker run --gpus all \ --shm-size=16g \ --memory=32g \ --memory-swap=64g \ --ulimit memlock=-1 \ -p 8000:8000 \ -v /home/ubuntu/data:/app/data \ -v /home/ubuntu/models:/app/models \ -v /home/ubuntu/temp:/app/temp \ -e PYTHONUNBUFFERED=1 \ -e CUDA_VISIBLE_DEVICES=0 \ -e PYTORCH_CUDA_ALLOC_CONF=expandable_segments:True,max_split_size_mb:128,garbage_collection_threshold:0.8 \ --ipc=host \ --runtime=nvidia \ suno-homebrew
docker run --gpus all     --shm-size=16g     --memory=32g     --memory-swap=64g     --ulimit memlock=-1     -p 8000:8000     -v /home/ubuntu/data:/app/data     -v /home/ubuntu/models:/app/models     -v /home/ubuntu/temp:/app/temp     -e PYTHONUNBUFFERED=1     -e CUDA_VISIBLE_DEVICES=0     -e PYTORCH_CUDA_ALLOC_CONF=expandable_segments:True,max_split_size_mb:128,garbage_collection_threshold:0.8     --ipc=host     --runtime=nvidia     suno-homebrew
docker ps
docker stop f5bdef02c822
docker run --gpus all     --shm-size=16g     --memory=32g     --memory-swap=64g     --ulimit memlock=-1     -p 8000:8000     -v /home/ubuntu/data:/app/data     -v /home/ubuntu/models:/app/models     -v /home/ubuntu/temp:/app/temp     -e PYTHONUNBUFFERED=1     -e CUDA_VISIBLE_DEVICES=0     -e PYTORCH_CUDA_ALLOC_CONF=expandable_segments:True,max_split_size_mb:128,garbage_collection_threshold:0.8     --ipc=host     --runtime=nvidia     suno-homebrew
docker ps
docker stop db311080fdbb
docker build -t suno-homebrew .
docker run --gpus all     --shm-size=8g     -p 8000:8000     -v /home/ubuntu/data:/app/data     -v /home/ubuntu/models:/app/models     -v /home/ubuntu/temp:/app/temp     -e PYTHONUNBUFFERED=1     -e CUDA_VISIBLE_DEVICES=0     --ipc=host     suno-homebrew
docker build -t suno-homebrew .
docker run --gpus all     --shm-size=8g     -p 8000:8000     -v /home/ubuntu/data:/app/data     -v /home/ubuntu/models:/app/models     -v /home/ubuntu/temp:/app/temp     -e PYTHONUNBUFFERED=1     -e CUDA_VISIBLE_DEVICES=0     --ipc=host     suno-homebrew
docker build -t suno-homebrew .
docker run --gpus all     --shm-size=8g     -p 8000:8000     -v /home/ubuntu/data:/app/data     -v /home/ubuntu/models:/app/models     -v /home/ubuntu/temp:/app/temp     -e PYTHONUNBUFFERED=1     -e CUDA_VISIBLE_DEVICES=0     --ipc=host     suno-homebrew
docker run --gpus all     --shm-size=16g     --memory=32g     --memory-swap=64g     --ulimit memlock=-1     -p 8000:8000     -v /home/ubuntu/data:/app/data     -v /home/ubuntu/models:/app/models     -v /home/ubuntu/temp:/app/temp     -e PYTHONUNBUFFERED=1     -e CUDA_VISIBLE_DEVICES=0     -e PYTORCH_CUDA_ALLOC_CONF=expandable_segments:True,max_split_size_mb:128,garbage_collection_threshold:0.8     --ipc=host     --runtime=nvidia     suno-homebrew
docker ps
docker stop 8930fd4b5481
docker run --gpus all     --shm-size=16g     --memory=32g     --memory-swap=64g     --ulimit memlock=-1     -p 8000:8000     -v /home/ubuntu/data:/app/data     -v /home/ubuntu/models:/app/models     -v /home/ubuntu/temp:/app/temp     -e PYTHONUNBUFFERED=1     -e CUDA_VISIBLE_DEVICES=0     -e PYTORCH_CUDA_ALLOC_CONF=expandable_segments:True,max_split_size_mb:128,garbage_collection_threshold:0.8     --ipc=host     --runtime=nvidia     suno-homebrew
docker ps
docker run --gpus all     --shm-size=16g     --memory=32g     --memory-swap=64g     --ulimit memlock=-1     -p 8000:8000     -v /home/ubuntu/data:/app/data     -v /home/ubuntu/models:/app/models     -v /home/ubuntu/temp:/app/temp     -e PYTHONUNBUFFERED=1     -e CUDA_VISIBLE_DEVICES=0     -e PYTORCH_CUDA_ALLOC_CONF=expandable_segments:True,max_split_size_mb:128,garbage_collection_threshold:0.8     --ipc=host     --runtime=nvidia     suno-homebrew
docker run --gpus all     --shm-size=16g     --memory=32g     --memory-swap=64g     --ulimit memlock=-1     -p 8000:8000     -v /home/ubuntu/data:/app/data     -v /home/ubuntu/models:/app/models     -v /home/ubuntu/temp:/app/temp     -v /home/ubuntu/src:/app/src \  # 코드 디렉토리 마운트 추가
docker run --gpus all     --shm-size=16g     --memory=32g     --memory-swap=64g     --ulimit memlock=-1     -p 8000:8000     -v /home/ubuntu/data:/app/data     -v /home/ubuntu/models:/app/models     -v /home/ubuntu/temp:/app/temp     -v /home/ubuntu/src:/app/src \  # 코드 디렉토리 마운트 추가
docker run --gpus all     --shm-size=16g     --memory=32g     --memory-swap=64g     --ulimit memlock=-1     -p 8000:8000     -v /home/ubuntu/data:/app/data     -v /home/ubuntu/models:/app/models     -v /home/ubuntu/temp:/app/temp     -v /home/ubuntu/src:/app/src     -e PYTHONUNBUFFERED=1     -e CUDA_VISIBLE_DEVICES=0     -e PYTORCH_CUDA_ALLOC_CONF=expandable_segments:True,max_split_size_mb:128,garbage_collection_threshold:0.8     --ipc=host     --runtime=nvidia     suno-homebrew
docker ps
docker stop 2e446f2149bc
docker ps
docker run --gpus all     --shm-size=16g     --memory=32g     --memory-swap=64g     --ulimit memlock=-1     -p 8000:8000     -v /home/ubuntu/data:/app/data     -v /home/ubuntu/models:/app/models     -v /home/ubuntu/temp:/app/temp     -v /home/ubuntu/src:/app/src     -e PYTHONUNBUFFERED=1     -e CUDA_VISIBLE_DEVICES=0     -e PYTORCH_CUDA_ALLOC_CONF=expandable_segments:True,max_split_size_mb:128,garbage_collection_threshold:0.8     --ipc=host     --runtime=nvidia     suno-homebrew
docker ps
docker run --gpus all     --shm-size=16g     --memory=32g     --memory-swap=64g     --ulimit memlock=-1     -p 8000:8000     -v /home/ubuntu/data:/app/data     -v /home/ubuntu/models:/app/models     -v /home/ubuntu/temp:/app/temp     -v /home/ubuntu/src:/app/src     -e PYTHONUNBUFFERED=1     -e CUDA_VISIBLE_DEVICES=0     -e PYTORCH_CUDA_ALLOC_CONF=expandable_segments:True,max_split_size_mb:128,garbage_collection_threshold:0.8     --ipc=host     --runtime=nvidia     suno-homebrew
docker run --gpus all     --shm-size=16g     --memory=32g     --memory-swap=64g     --ulimit memlock=-1     -p 8000:8000     -v /home/ubuntu:/app     -e PYTHONUNBUFFERED=1     -e CUDA_VISIBLE_DEVICES=0     -e PYTORCH_CUDA_ALLOC_CONF=expandable_segments:True,max_split_size_mb:128,garbage_collection_threshold:0.8     --ipc=host     --runtime=nvidia     suno-homebrew
docker build -t suno-homebrew .
docker run --gpus all     --shm-size=16g     --memory=32g     --memory-swap=64g     --ulimit memlock=-1     -p 8000:8000     -v /home/ubuntu:/app     -e PYTHONUNBUFFERED=1     -e CUDA_VISIBLE_DEVICES=0     -e PYTORCH_CUDA_ALLOC_CONF=expandable_segments:True,max_split_size_mb:128,garbage_collection_threshold:0.8     --ipc=host     --runtime=nvidia     suno-homebrew
docker build -t suno-homebrew .
docker run --gpus all     --shm-size=16g     --memory=32g     --memory-swap=64g     --ulimit memlock=-1     -p 8000:8000     -v /home/ubuntu:/app     -e PYTHONUNBUFFERED=1     -e CUDA_VISIBLE_DEVICES=0     -e PYTORCH_CUDA_ALLOC_CONF=expandable_segments:True,max_split_size_mb:128,garbage_collection_threshold:0.8     --ipc=host     --runtime=nvidia     suno-homebrew
git push
git push --set-upstream origin master
git config --global http.postBuffer 524288000
git config --global http.maxRequestBuffer 100M
git config --global core.compression 9
git config --global http.version HTTP/1.1
git push --set-upstream origin master
git add .
git commit -m "0410"
git push --set-upstream origin master
git add .
git commit -m "0416"
git push
git push --set-upstream origin master
exit
