import os, glob, re, argparse, sys
import numpy as np
import subprocess as sp
from scipy.misc import imread, imshow
from datetime import timedelta, datetime
import matplotlib.pylab as plt
from skimage.morphology import label, remove_small_objects
from skimage.measure import regionprops

def threshold_image(x, thresh):
    """
    threshold_image(x) applies a threshold, returning a boolean matrix
    """
    return x >= (thresh * x.max())

def zscore(val, list_of_vals):
    """
    zscore(val, list_of_vals)
    returns a standard normal z value defined as: (x - mu) / sigma
    """
    zscore = (val - np.nanmean(list_of_vals)) / np.nanstd(list_of_vals)
    return zscore

def save_to_csv(x, file_name = 'foo.txt'):

    dir_name, file_name = os.path.split(file_name)
    file_name, file_ext = os.path.splitext(file_name)
    csv_file_name = file_name + ".csv"
    
    if not os.path.isfile(csv_file_name):
        np.savetxt(csv_file_name, x, delimiter=",", fmt = '%.2f')
        return csv_file_name

    else: 
        with open(csv_file_name, 'a') as f_handle:
            np.savetxt(f_handle, x, delimiter=",", fmt = '%.2f')
        return csv_file_name

def rgb2gray(image):
    # The sRGB color space is defined in terms of the CIE 1931 linear 
    # luminance Y, which is given by: 0.2126 * R + 0.7152 * G + 0.0722 * B 
    # In the Y'UV and Y'IQ models used by PAL and NTSC, the rec601 luma (Y') 
    # component is computed as: 0.2989 * R + 0.5870 * G + 0.1140 * B 
    
    if image.shape[2] is 4: # RGBA
        image = image[:,:,:3] # discard alpha channel
    elif image.shape[2] < 3: # not even 3 channels
        assert image.shape[2] is 3, "This image does not have RGB channel data" 
    
    return 0.2126 * image[:,:,0] + 0.7152 * image[:,:,1] + 0.0722 * image[:,:,2]

def imabsdiff(X, Y):
    # only run on greyscale images
    # image1 and image2 are real, nonsparse numeric arrays with the same class and size.
    assert X.shape == Y.shape, "The images do not have the same shape" 
    assert type(X[0,0]) == type(Y[0,0]), "Image elements do not have the same type" 

    return np.abs(X-Y)

def region_props(image, pixels, conn = 4):
    """
    region_props(image, pixels, conn = 4)
    image -> a boolean matrix
    pixesl -> minimum size of area to look for
    conn -> if they are very thin areas, discard them. 
    """
    #binary_opening_im = remove_small_objects(image, min_size=pixels, connectivity=conn)
    
    label_img = label(image)
    regions = regionprops(label_img)

    x0, y0, ymin, area = ([] for i in range(4))
    """
    x0, y0 are the location of the centroid for each region
    x1 and x2 are the *major* axis from the center outward
    y1 and y2 are the *minor* axis from the center outward
    bx and by are the bounding box on the regions found
    """
    for i, props in enumerate(regions):
        centroid = props.centroid
        y0.append(centroid[0])
        x0.append(centroid[1])
        area.append(props.area)
        """
        # orientation = props.orientation
        x1.append(x0[i] + math.cos(orientation) * 0.5 * props.major_axis_length)
        y1.append(y0[i] - math.sin(orientation) * 0.5 * props.major_axis_length)
        x2.append(x0[i] - math.sin(orientation) * 0.5 * props.minor_axis_length)
        y2.append(y0[i] - math.cos(orientation) * 0.5 * props.minor_axis_length)

        # ax.plot((x0[i], x1[i]), (y0[i], y1[i]), '-r', linewidth=2.5)
        # ax.plot((x0[i], x2[i]), (y0[i], y2[i]), '-r', linewidth=2.5)
        # ax.plot(x0[i], y0[i], '.g', markersize=15)
        """
        # (min_row, min_col, max_row, max_col) are the returns from the bbox
        minr, minc, maxr, maxc = props.bbox
        # bx.append((minc, maxc, maxc, minc, minc))
        # by.append((minr, minr, maxr, maxr, minr))
        ymin.append(maxr)


    return zip(x0,y0), ymin, area

def pick_ymin(ymin_vec, ymin, area, centroid):
    x0, y0 = zip(*centroid)

    sorted_ind = np.argsort(area)[::-1] # sort in decreasing size order
    area = [area[i] for i in sorted_ind]
    x0 = [x0[i] for i in sorted_ind]
    y0 = [y0[i] for i in sorted_ind]
    ymin = [ymin[i] for i in sorted_ind]

    if ymin_vec:
        # something like if ymin[0] > ymin_vec[-1] the use ymin[0]
        if ymin[0] >= ymin_vec[-1]:
            return ymin[0]
        else:
            matches = [i for i in ymin if i < ymin_vec[-1]]
            if matches: return matches[0] 
            else: return np.nan
    else:
        # first frame -- just to get things rolling
        return ymin[0]
    """
    # print 'ymin''s length is: ' + str(len(ymin))
    # just to get the ball rolling
    # if ymin is empty (empty lists are FALSE)
    if not ymin:
        # print 'adding a nan to the list'
        return np.nan
    elif ymin and len(ymin_vec) < 5:
        # print 'adding ' + str(ymin[0]) + ' to the list'
        return ymin[0]
    # if neither are empty and criterion is met
    elif ymin and abs(zscore(ymin[0], ymin_vec)) < 3:
        return ymin[0]
    # if neither are empty but ymin does not meet z-score criterian
    else:
        return np.nanmean(ymin_vec)
    """

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

def segment_extractor(FFMPEG_BINARY, video_name, fps = '1/20',\
                    start_time = 0, duration = 10):
    """
    segment_extractor(video_name) calls ffmpeg and returns a list of the stills 
    that it returns where: 

    video_name -> a *.mp4 or *.mov file 
    fps -> the number of frames to extract per second (eg. '1/20' is 1 frame every 20 sec.)
    start_time -> the time in seconds at which to start the still extraction
    duration -> the number of seconds to extract to stills at one time
    """

    if type(fps) is not str:
        fps = str(fps)
    if type(duration) is not str:
        duration = str(duration)
    if type(start_time) is not str:
        start_time = HHMMSS(start_time)

    try:
        sp.call([FFMPEG_BINARY, '-loglevel', 'panic', '-i', video_name, '-ss', start_time,\
              '-t', duration, '-r', fps, 'image-%4d.jpeg'])
    except Exception, e:
        raise e 
    return sorted(glob.glob('*.jpeg'))

def still_extractor(FFMPEG_BINARY, video_name, fps = '1/20'):
    """
    still_extractor(video_name) calls ffmpeg and returns a list of the stills 
    that it returns where: 

    video_name -> a *.mp4 or *.mov file 
    fps -> the number of frames to extract per second (eg. '1/20' is 1 frame every 20 sec.)
    """

    if type(fps) is not str:
        fps = str(fps)
    
    try:
        sp.call([FFMPEG_BINARY, '-loglevel', 'panic', '-i', video_name, '-r', fps, 'image-%4d.jpeg'])
    except Exception, e:
        raise e 
    return sorted(glob.glob('*.jpeg'))

def still_cropper(file_name, zoi = np.s_[:, :]):
    """
    still_cropper(file_name, zoi = np.s_[:, :]) takes 
    in an image and crops it to the zoi specified 
    """
    plt.imshow(imread(file_name)[zoi[0],zoi[1],:])
    plt.axis('off')
    file_name, file_ext = os.path.splitext(file_name)
    new_file_name = file_name + '.png'
    plt.savefig(new_file_name, format = 'png', dpi = 300, frameon = False,\
                bbox_inches = 'tight') # pad_inches = 0
        
    os.remove(file_name + file_ext)

    return new_file_name

def HHMMSS(sec):
    """
    HHMMSS(sec) takes an integer or float and returns a 'time string'
    formated as strings HH:MM:SS 
    (eg. HHMMSS(35) -> '00:00:35' and HHMMSS(7201) -> '02:00:01')
    """
    # based on http://stackoverflow.com/a/4048773/1902480   
    sec = timedelta(seconds = sec)
    d = datetime(1900,1,1) + sec
    return '{:%H:%M:%S}'.format(d)

def cvsecs(*args):
    # This function is substantially based on one found at http://zulko.github.io/moviepy/
    # used from within video_duration
    """
    Converts a time to second. Either cvsecs(min,secs) or
    cvsecs(hours,mins,secs).
    >>> cvsecs(5.5) # -> 5.5 seconds
    >>> cvsecs(10, 4.5) # -> 604.5 seconds
    >>> cvsecs(1, 0, 5) # -> 3605 seconds
    """
    if len(args) == 1:
        return args[0]
    elif len(args) == 2:
        return 60*args[0]+args[1]
    elif len(args) ==3:
        return 3600*args[0]+60*args[1]+args[2]

def load_video_data(FFMPEG_BINARY, filename):
    # This function is substantially based on one found at http://zulko.github.io/moviepy/
    # open the file in a pipe, provoke an error, read output
    proc = sp.Popen([FFMPEG_BINARY, "-i", filename, "-"],
                    stdin=sp.PIPE,
                    stdout=sp.PIPE,
                    stderr=sp.PIPE)
    proc.stdout.readline()
    proc.terminate()
    infos = proc.stderr.read()
    
    lines = infos.splitlines()
    if "No such file or directory" in lines[-1]:
        raise IOError("%s not found ! Wrong path ?" % filename)

    # get the output line that speaks about video
    line = [l for l in lines if ' Video: ' in l][0]
    return lines

def video_duration(FFMPEG_BINARY, filename):
    # This function is substantially based on one found at http://zulko.github.io/moviepy/
    lines = load_video_data(FFMPEG_BINARY, filename)
    line = [l for l in lines if ' Video: ' in l][0]
    
    # get duration (in seconds)
    line = [l for l in lines if 'Duration: ' in l][0]
    match = re.search(" [0-9][0-9]:[0-9][0-9]:[0-9][0-9].[0-9][0-9]", line)
    hms = map(float, line[match.start()+1:match.end()].split(':'))
    duration = cvsecs(*hms)
    return duration

if __name__ == '__main__':
    
    pass

    #if args.verbosity:
    #   print "verbosity turned on"
