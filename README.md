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

---
## Installation
<p align="center">
    <a href="https://github.com/snuailab-biz/ison-dev/blob/main/docs/environment.md">Installation</a>
</p>

## Excutation
<p align="center">
    <a href="https://github.com/snuailab-biz/ison-dev/blob/main/docs/excutable_guide.md">Excutation</a>
</p>

## Directories
```plain text
ISON
├── docker-compose.yml
├── logs
├── __pycache__
├── README.md
├── requirements.txt
└── services/
    ├── service_detect
    │   ├── app_detect.py
    │   ├── configure
    │   ├── Dockerfile
    │   ├── __init__.py
    │   ├── IsonAI
    │   ├── ison_logger.py
    │   ├── __pycache__
    │   └── requirements.txt
    ├── service_event
    │   ├── app_event.py
    │   ├── configure
    │   ├── Dockerfile
    │   ├── IsonEvent
    │   ├── ison_logger.py
    │   ├── __pycache__
    │   └── requirements.txt
    ├── service_rtsp
    │   ├── app_rtsp.py
    │   ├── client_simulator.py
    │   ├── Dockerfile
    │   ├── ison_logger.py
    │   ├── __pycache__
    │   └── requirements.txt
    └── service_simulator
        ├── DefaultCompany
        ├── Dockerfile
        ├── ISON_3D_PRO_Data
        ├── ISON_3D_PRO.x86_64
        └── UnityPlayer.so
```
