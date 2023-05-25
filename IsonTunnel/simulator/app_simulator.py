import subprocess
from IsonTunnel.simulator import EXE_ROOT

def run():
    # 실행 파일 경로
    executable_path = str(EXE_ROOT / "ISON_3D_PRO.x86_64")
    # 실행 파일 실행
    process = subprocess.Popen(executable_path, shell=True)

    # 프로세스 실행이 종료될 때까지 대기
    process.wait()