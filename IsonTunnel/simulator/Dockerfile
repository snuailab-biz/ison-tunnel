FROM ljjsnuailab/ison-simulator


# # 시간대 설정
# ENV DEBIAN_FRONTEND=noninteractive
# RUN apt-get update && apt-get install -y tzdata && \
#     ln -fs /usr/share/zoneinfo/Asia/Seoul /etc/localtime && \
#     dpkg-reconfigure --frontend noninteractive tzdata
# 필수 패키지 설치

# 작업 디렉토리 설정
WORKDIR /app

# 소스 코드 추가
# COPY . .

# 포트 설정 (필요한 경우)
EXPOSE 1235

# 앱 실행 (필요한 경우)
CMD [ "service_simulator/ISON_3D_PRO.x86_64" ]