
import os, sys, re
import numpy as np
from scipy.misc import imread
import matplotlib.pylab as plt
from skimage.filter import gaussian_filter
from auxillary_funcs import *

def video_track(FFMPEG_BINARY, video_name, fps = 24, 
                start_time = 0, duration = 1, plotting_flag = False):
    """
    video_track(FFMPEG_BINARY, video_name, fps = 24,\
                start_time = 0, end_time = 10, duration = 1)

    calls segment_extractor() and returns a list of the stills 

    video_name -> a *.mp4 or *.mov file 
    fps -> the number of frames to extract per second (eg. '1/20' is 1 frame every 20 sec.)
    start_time -> the time in seconds at which to start the still extraction
    duration -> the number of seconds to extract to stills at one time
    """

    n = 12
    thresh = 0.75
    zoi = np.s_[150:900, 850:1050]
    regex = re.compile("[0-9][0-9][0-9][0-9]")

    stills = segment_extractor(FFMPEG_BINARY, video_name, fps = str(fps),\
                           start_time = HHMMSS(start_time), duration = duration)

    im_set = [(stills[i-n], stills[i], stills[i+n]) for i in np.arange(n,len(stills) - n)]

    ymin_global = []

    for i, im in enumerate(im_set):
        back_im = imread(im[0])
        center_im = imread(im[1])
        forward_im = imread(im[2])
    
        frame_curr = rgb2gray(center_im[zoi[0], zoi[1],:])
        frame_prev = rgb2gray(back_im[zoi[0], zoi[1],:])
        frame_fut = rgb2gray(forward_im[zoi[0], zoi[1],:])
        
        frame_diff_b = imabsdiff(frame_curr, frame_prev)
        frame_diff_f = imabsdiff(frame_fut, frame_curr)
        # frame_diff = imabsdiff(frame_diff_b, frame_diff_f)        
        
        frame_blur = gaussian_filter(frame_diff_f, 15)
        thresh_mat = threshold_image(frame_blur, thresh)

        # region_props
        centroid, ymin, area = region_props(thresh_mat, 100, conn = 40)
        # frame_diff_b=imabsdiff(frame_curr, frame_prev)

        ymin_picked = pick_ymin(ymin_global, ymin, area, centroid)
        # print 'current ymin is: ' + str(ymin_picked)
        ymin_global.append(ymin_picked)

        
        if plotting_flag and (i % 96 == 0):
            plt.figure()
            plt.subplot(1,3,1)
            plt.imshow(-thresh_mat, cmap='Greys')
            if ymin_global[-1] is not np.nan:
                plt.axhline(ymin_global[-1], color = 'g', linewidth = 2.5)
            plt.subplot(1,3,2)
            plt.imshow(-frame_diff_b, cmap='Greys')
            plt.subplot(1,3,3)
            plt.imshow(-frame_diff_f, cmap='Greys')
            
            dir_name, file_name = os.path.split(video_name)
            file_name, file_ext = os.path.splitext(file_name)
            
            num = regex.findall(im[1])[0]

            plt.savefig(file_name + num + '.png', bbox_inches='tight')
            plt.close()

        update_progress(float(i)/float(len(im_set)))
    
    return ymin_global, stills

   
if __name__ == '__main__':
    
    FFMPEG_BINARY = 'ffmpeg'
    
    """
    parser = argparse.ArgumentParser()
    parser.add_argument("video_name", help="a video name is required")
    parser.add_argument('-c', '--channel', help='picks out a color channel',\
                        action="store_true")
    args = parser.parse_args()
    
    # video_length = video_duration(FFMPEG_BINARY, args.video_name)
    zoi = np.s_[150:900, 850:1050]
    stills = still_extractor(FFMPEG_BINARY, args.video_name, fps = '1/20')
    cropped_files = []
    for still in stills:
        cropped_files.append(still_cropper(still, zoi = zoi))
        if args.channel: save_color_channel(still, channel = 0) 
         
    """

    video_name = './test_videos/may_29_14_t1r.mov'
    video_length = video_duration(FFMPEG_BINARY, video_name)

    start_time = 100
    dur = (video_length - start_time)
    fps = 24

    #try:
    video_length = video_duration(FFMPEG_BINARY, video_name)
    y_min, stills = video_track(FFMPEG_BINARY, video_name, fps = fps, 
                            start_time = start_time, 
                            duration = dur, plotting_flag = True)
    #except Exception, e:
    #    raise e
    
    print 'extracted ' + str(dur)  + ' sec. of video'

    try:
        save_to_csv(y_min, file_name = video_name)
    except Exception, e:
        raise e
    finally:
        print 'removing ' + str(len(stills)) + ' jpegs'
        removal_check = [os.remove(still) for still in stills]





