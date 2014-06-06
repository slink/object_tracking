import glob, re, os, shutil, math
from scipy.misc import imread, imsave
import numpy as np
import subprocess as sp
from datetime import datetime, timedelta


def video_to_stills(FFMPEG_BINARY, video_path, 
                    image_folder, start = float('NaN'), finish = float('NaN')):
    
    if math.isnan(float(start)):
        print 'video start set at 0 sec.'
        start = HHMMSS(0)
    elif type(start) == str:
        start = HHMMSS(float(start))
    
    if math.isnan(float(finish)):
        print 'assuming length of test for duration'
        finish = HHMMSS(video_duration(FFMPEG_BINARY, video_path))
    elif type(finish) == str:
        finish = HHMMSS(float(finish))

    fps = video_fps(FFMPEG_BINARY, video_path)

    abs_video_path = os.path.abspath(video_path)
    video_path, video_name =  os.path.split(abs_video_path)

    calling_dir = os.getcwd()
    image_folder_path = os.path.join(calling_dir, image_folder)

    if not os.path.exists(image_folder_path):
        os.mkdir(image_folder)

    try:
        os.chdir(image_folder_path)
    except:
        raise

    try:
        shutil.copy2(abs_video_path, image_folder_path)
    except:
        raise
    new_video_path = os.path.join(image_folder_path, video_name)

    proc = sp.Popen([FFMPEG_BINARY, '-ss', start,
                    '-t', finish, '-i', abs_video_path, 
                    '-r', str(fps), 'test%4d.jpg'],
                    stdin=sp.PIPE,
                    stdout=sp.PIPE,
                    stderr=sp.PIPE)

    proc.stdout.readline()
    proc.terminate()

    try:
        os.remove(new_video_path)
    except:
        raise

    try:
        os.chdir(calling_dir)
    except:
        raise

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

def video_size(FFMPEG_BINARY, filename):
    # This function is substantially based on one found at http://zulko.github.io/moviepy/
    lines = load_video_data(FFMPEG_BINARY, filename)
    line = [l for l in lines if ' Video: ' in l][0]

    # get the size, of the form 460x320 (w x h)
    match = re.search(" [0-9]*x[0-9]*(,| )", line)
    size = map(int, line[match.start():match.end()-1].split('x'))
    return size

def video_fps(FFMPEG_BINARY, filename):
    # This function is substantially based on one found at http://zulko.github.io/moviepy/
    lines = load_video_data(FFMPEG_BINARY, filename)
    line = [l for l in lines if ' Video: ' in l][0]
    
    # get the frame rate
    match = re.search("( [0-9]*.| )[0-9]* (tbr|fps)", line)
    fps = float(line[match.start():match.end()].split(' ')[1])
    return fps

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
    # nframes = int(duration*fps)

def all_infos(FFMPEG_BINARY, filename):
    size = video_size(FFMPEG_BINARY, filename)
    fps = video_fps(FFMPEG_BINARY, filename)
    duration = video_duration(FFMPEG_BINARY, filename)

    return fps, duration, size

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

def HHMMSS(sec):
    # based on http://stackoverflow.com/a/4048773/1902480
    sec = timedelta(seconds = sec)
    d = datetime(1900,1,1) + sec
    print d
    return '{:%H:%M:%S}'.format(d)
