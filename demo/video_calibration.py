
from data_check import VideoSplit
path1 = '/home/ljj/workspace/ison-tunnel/output_video1.mp4'

video1 = VideoSplit(path1)

video1.set_calibration(param_path ='/home/ljj/workspace/ison-tunnel/IsonTunnel/configure/field/cam1/params.json')

video1.video_show()