# FROM pytorch/pytorch:latest
FROM ljjsnuailab/ison-rtsp

RUN apt-get update && apt-get install -y \
    python3.9 \
    python3-pip \
    gir1.2-gstreamer-1.0 \
    gstreamer1.0-plugins-good \
    libgirepository1.0-dev \
    libcairo2-dev \
    libgstreamer-plugins-base1.0-dev \
    libgstreamer-plugins-good1.0-dev \
    libgstreamer1.0-dev \
    libgstrtspserver-1.0-dev\
    gstreamer1.0-plugins-base \
    gstreamer1.0-plugins-good \ 
    gstreamer1.0-plugins-bad \ 
    gstreamer1.0-plugins-ugly \ 
    gstreamer1.0-libav \
    && rm -rf /var/lib/apt/lists/*

# RUN python3 -m pip install --no-cache-dir pygobject
# RUN python3 -m pip install --upgrade pip
# COPY requirements.txt .
# RUN python3 -m pip install -r requirements.txt

WORKDIR /app

EXPOSE 1239
# 소스 코드 추가
# COPY . .

# 포트 설정 (필요한 경우)

# 앱 실행 (필요한 경우)
CMD [ "python3", "service_rtsp/app_rtsp.py" ]
