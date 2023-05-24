<h1 align="center">ISON: Detector and Tracking<br>Event Generator & Simulator Visualization</h1>

<p align="center">
  <img src="assets/ison_logo.png" alt="text" width="number" height="200px" width="600px"/>
</p>

<p align="center">
    이종진</a><sup>1*</sup> &emsp;&emsp;
    고대관</a><sup>2*</sup> &emsp;&emsp;
    김성근</a><sup>3*</sup> &emsp;&emsp;
</p>

<p align="center">
    ISON Project by SNUAILAB-dev
</p>
<p align="center">
    <a href="https://github.com/snuailab-biz/ison-dev">Demo</a>
</p>

---

## Code and Data
- [x] 📣 Detector Server **highly!**
- [x] 📣 Event Generator
- [x] 📣 RTSP Server
- [x] 📣 C# 3D Simulator. **highly!**
- [x] Docker image for ISON Project. 
- [x] Automatically run at desktop startup
- [ ] Release of the ISON Site

# Installation
<p align="justify"> ISON 터널 관제 시스템에 필요한 설치 프로세스는 다음과 같이 진행한다. 납품할 Desktop의 경우 HP miniPC를 사용하며 miniPC에는 기본적으로 다음과 같은 스펙을 갖는다. </p>

## Specification
HP-Z2-Mini-G9-Workstation-Desktop-PC
- Kernel : x86_64 Linux 5.15.0-58-generic
- CPU : 12th Gen Intel Core i9-12900K @ 24x 3.9GHz
- GPU : NVIDIA RTX A2000 (6GB)
- RAM : 32GB
- DISK : 1TB
- OS : Ubuntu 20.04 focal
- NVIDIA DRIVER : 470.161.03
- CUDA : cuda 11.4

## 환경 셋팅

Desktop(Mini PC)에는 기본적으로 Nvidia-driver, CUDA등 설치 및 설정이 완료되어 있다.
하지만 ISON-Simulator & Event generator를 실행하기 위해서는 추가적으로 docker, docker-compose, docker nvidia를 설치해야한다.

docker를 통해 실행환경 관리하며, docker-compose를 통해 각각의 docker image, container를 관리한다.

또한 docker내부에서 desktop의 gpu, cuda를 사용하기 위해서 docker nvidia를 설치해야한다.

### Docker Install
1. Docker의 GPG key 추가 

```bash
curl -fsSL https://download.docker.com/linux/ubuntu/gpg | sudo apt-key add -
```

1. Docker repository 추가

```bash
sudo add-apt-repository "deb [arch=amd64] https://download.docker.com/linux/ubuntu $(lsb_release -cs) stable"
```

2. 패키지 목록 업데이트

```bash
sudo apt-get update
```

3. Docker 설치

```bash
sudo apt-get install docker-ce
```

### Docker-compose Install
    
- curl 설치.

```bash
sudo apt update
sudo apt install curl
```

1. Docker Compose 바이너리 다운로드

```bash
sudo curl -L "https://github.com/docker/compose/releases/download/1.29.2/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose
```

2. 다운로드한 바이너리 파일에 실행 권한 부여

```bash
sudo chmod +x /usr/local/bin/docker-compose
```

3. Docker Compose 버전 확인

```bash
docker-compose --version
```

### Nvidia docker runtime 설치
    
1. NVIDIA Docker 런타임을 위한 패키지 저장소 설정

```bash
curl -s -L https://nvidia.github.io/nvidia-docker/gpgkey | \
  sudo apt-key add -
distribution=$(. /etc/os-release;echo $ID$VERSION_ID)
curl -s -L https://nvidia.github.io/nvidia-docker/$distribution/nvidia-docker.list | \
  sudo tee /etc/apt/sources.list.d/nvidia-docker.list
```

2. 패키지 목록 업데이트

```bash
sudo apt-get update
```

3. NVIDIA Docker 런타임 설치

```bash
sudo apt-get install -y nvidia-docker2
```

4. Docker 데몬 재시작

```bash
sudo systemctl restart docker
```

위 명령어를 모두 실행하면 호스트 시스템에 NVIDIA Docker 런타임이 설치되고, NVIDIA GPU를 사용하는 Docker 컨테이너를 실행할 수 있다.

여기까지 설치가 완료되면 모든 환경 셋팅은 완료된다.

- [ ]❗따로 shell script를 만들어 자동으로 설치할 수 있게 만들 예정

