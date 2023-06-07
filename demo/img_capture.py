from data_check import VideoSplit
path1 = '/home/ljj/workspace/ison-tunnel/output_video1.mp4'
path2 = 'output_video2.mp4'
path3 = 'output_video3.mp4'
path4 = 'output_video4.mp4'

video1 = VideoSplit(path1)
video1.save_capture(1)

video2 = VideoSplit(path2)
video2.save_capture(2)

video3 = VideoSplit(path3)
video3.save_capture(3)

video4 = VideoSplit(path4)
video4.save_capture(4)



