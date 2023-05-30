FROM ljjsnuailab/ison-eventer

# # 시간대 설정
# ENV DEBIAN_FRONTEND=noninteractive
# RUN apt-get update && apt-get install -y tzdata && \
#     ln -fs /usr/share/zoneinfo/Asia/Seoul /etc/localtime && \
#     dpkg-reconfigure --frontend noninteractive tzdata

# RUN apt-get install -yf \
#     libgl1-mesa-glx \
#     && rm -rf /var/lib/apt/lists/*


# RUN python3 -m pip install --upgrade pip
# COPY requirements.txt .
# RUN python3 -m pip install -r requirements.txt

# # CUDA 관련 환경 변수 설정
# ENV LD_LIBRARY_PATH /usr/local/cuda/lib64:$LD_LIBRARY_PATH
# ENV PATH /usr/local/cuda/bin:$PATH

# 작업 디렉토리 설정
WORKDIR /app

# 소스 코드 추가
# COPY . .

# 앱 실행 (필요한 경우)
CMD [ "python3", "service_event/app_event.py" ]
