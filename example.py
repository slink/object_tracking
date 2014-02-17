from ffmpeg_functions import video_to_stills
from naive_flame_tracking import naive_flame_tracking

FFMPEG_BINARY = 'ffmpeg'
test_video = 'test.mp4'
jpg_folder = 'test_folder'

video_to_stills(FFMPEG_BINARY, test_video, jpg_folder)
test_video = naive_flame_tracking(jpg_folder, 
							bkgrd_img_start=1, 
							bkgrd_img_end=60, 
							tst_img_start=85, 
							tst_img_end=95)

# center of mass velocity for tracked item (pixels per second)
com_vel = bob.peak_velocity_com()

# center of mass velocity for tracked item (pixels per second)
fe_vel= bob.peak_velocity_front_edge()