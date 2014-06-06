
import os, sys
import numpy as np
from scipy.misc import imread
import matplotlib.pylab as plt
from skimage.filter import gaussian_filter
from still_extractor import video_duration, segment_extractor, HHMMSS, still_cropper 
from frame_test import rgb2gray, region_props,\
                       imabsdiff, zscore, save_to_csv,\
                       threshold_image, pick_ymin # video_track

def moving_average(a, n=3) :
    ret = np.cumsum(a, dtype=float)
    ret[n:] = ret[n:] - ret[:-n]
    return ret[n - 1:] / n

def update_progress(progress):
    """
    update_progress() : Displays or updates a console progress bar
    Accepts a float between 0 and 1. Any int will be converted to a float.
    A value under 0 represents a 'halt'.
    A value at 1 or bigger represents 100%
    """
    barLength = 10 # Modify this to change the length of the progress bar
    status = ""
    if isinstance(progress, int):
        progress = float(progress)
    if not isinstance(progress, float):
        progress = 0
        status = "error: progress var must be float\r\n"
    if progress < 0:
        progress = 0
        status = "Halt...\r\n"
    if progress >= 1:
        progress = 1
        status = "Done...\r\n"
    block = int(round(barLength*progress))
    text = "\rPercent: [{0}] {1}% {2}".format( "#"*block + "-"*(barLength-block), progress*100, status)
    sys.stdout.write(text)
    sys.stdout.flush()

def video_track(FFMPEG_BINARY, video_name, fps = 24, start_time = 0, end_time = 10, duration = 1):
    """
    video_track(FFMPEG_BINARY, video_name, fps = 24,\
                start_time = 0, end_time = 10, duration = 1)

    calls segment_extractor() and returns a list of the stills 

    video_name -> a *.mp4 or *.mov file 
    fps -> the number of frames to extract per second (eg. '1/20' is 1 frame every 20 sec.)
    start_time -> the time in seconds at which to start the still extraction
    duration -> the number of seconds to extract to stills at one time
    """
    thresh = 0.75
    zoi = np.s_[150:900, 850:1050]

    ymin_global = []

    for segment_start in np.arange(start_time, end_time, duration): # 'duration' second increments
        
        #if (segment_start + duration) % 5 == 0:
        #    print 'processing: ' + str(segment_start) + ' to ' + str(segment_start + duration)
        #    sys.stdout.flush()
            
        # pulling the stills out of the movie with ffmpeg
        stills = segment_extractor(FFMPEG_BINARY, video_name, fps = str(fps),\
                                   start_time = HHMMSS(segment_start),\
                                   duration = duration)

        # cropping the stills
        # cropped_files = [still_cropper(still, zoi = zoi) for still in stills]
        # for i, file_name in enumerate(stills[1:-1]):
            # cropping the stills and greyscaling them
        
        n = 9
        # counting on python 2 integer division where 7 / 2 equals 3 as both are ints

        frame_curr = rgb2gray(imread(stills[n/2])[zoi[0], zoi[1],:])
        frame_prev = rgb2gray(imread(stills[0])[zoi[0], zoi[1],:])
        frame_fut = rgb2gray(imread(stills[n])[zoi[0], zoi[1],:])
        
        frame_diff_b = imabsdiff(frame_curr, frame_prev)
        frame_diff_f = imabsdiff(frame_fut, frame_curr)

        # frame_diff = imabsdiff(frame_diff_b, frame_diff_f)        
        # frame_diff = imabsdiff(frame_diff_f, frame_diff_f)
        frame_blur = gaussian_filter(frame_diff_f, 15)
        thresh_mat = threshold_image(frame_blur, thresh)

        # region_props
        centroid, ymin, area = region_props(thresh_mat, 100, conn = 40)
        # frame_diff_b=imabsdiff(frame_curr, frame_prev)

        if ymin:
            ymin_picked = pick_ymin(ymin_global, ymin, area, centroid)
            print 'current ymin is: ' + str(ymin_picked)
            ymin_global.append(ymin_picked)

        """
        # tested at andres's behest

        # let ymin_global build a bit -- otherwise we can get divide by zero in zscore()
        if len(ymin_global) < 5: 
            ymin_global.append(ymin[0])
        else:
            # if ymin is empty (empty lists are FALSE)
            if not ymin: 
                ymin_global.append(np.nan)
            # if neither are empty and criterion is met
            elif ymin and abs(zscore(ymin[0], ymin_global)) < 3:
                ymin_global.append(ymin[0])
            # if neither are empty but ymin does not meet z-score criterian
            else:
                ymin_global.append(np.nanmean(ymin_global))
        """
        if segment_start % 20 == 0:
            plt.figure()
            plt.subplot(1,3,1)
            plt.imshow(-thresh_mat, cmap='Greys')
            if ymin_global[-1] is not np.nan:
                plt.axhline(ymin_global[-1], color = 'g', linewidth = 2.5)
            plt.subplot(1,3,2)
            plt.imshow(-frame_diff_b, cmap='Greys')
            plt.subplot(1,3,3)
            plt.imshow(-frame_diff_f, cmap='Greys')
            plt.savefig(video_name[:-4] + str(segment_start) + '.png',\
                        bbox_inches='tight')

        update_progress(float(segment_start - start_time)/float(end_time - start_time))
        save_to_csv(ymin_global, file_name = video_name)

    removal_check = [os.remove(still) for still in stills]
    
    return ymin_global

    
   
if __name__ == '__main__':
    FFMPEG_BINARY = 'ffmpeg'
    video_name = 'may_29_14_t1r.mov'
    
    video_length = video_duration(FFMPEG_BINARY, video_name)
    y_min = video_track(FFMPEG_BINARY, video_name, fps = 24, 
                        start_time = 100, end_time = video_length, duration = 10)

    print 'extracted ' + str(len(y_min)) + ' sec. of video'
    print y_min
    # print y_min,




