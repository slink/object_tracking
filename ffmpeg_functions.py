import glob, re, os, shutil
from scipy.misc import imread, imsave
import numpy as np
import subprocess as sp
from datetime import datetime, timedelta


def video_to_stills(FFMPEG_BINARY, filename, start = NaN, finish = NaN, folder):
    
    if math.isnan(start):
        print 'video start set at 0 sec.'
        start = HHMMSS(0)
    if math.isnan(finish):
        print 'assuming length of test for duration'
        finish = HHMMSS(video_duration(FFMPEG_BINARY, filename))

    fps = video_fps(FFMPEG_BINARY, filename)

    calling_dir = os.getcwd()
    folder_path = os.path.join(calling_dir, folder)
    
    if not os.path.exists(folder_path):
        os.mkdir(folder)

    try:
        os.chdir(folder_path)
    except:
        raise

    try:
        shutil.copy2(filename, folder_path)
    except:
        raise

    proc = sp.Popen([FFMPEG_BINARY, '-ss', start,
                    '-t', finish, '-i', filename, 
                    '-r', fps, 'test%4d.jpg'],
                    stdin=sp.PIPE,
                    stdout=sp.PIPE,
                    stderr=sp.PIPE)

    proc.stdout.readline()
    proc.terminate()

    try:
        os.remove(filename)
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
    if print_infos:
        # print the whole info text returned by FFMPEG
        print infos

    lines = infos.splitlines()
    if "No such file or directory" in lines[-1]:
        raise IOError("%s not found ! Wrong path ?" % filename)

    # get the output line that speaks about video
    line = [l for l in lines if ' Video: ' in l][0]
    return line

def video_size(FFMPEG_BINARY, filename):
    # This function is substantially based on one found at http://zulko.github.io/moviepy/
    line = load_video_data(FFMPEG_BINARY, filename)

    # get the size, of the form 460x320 (w x h)
    match = re.search(" [0-9]*x[0-9]*(,| )", line)
    size = map(int, line[match.start():match.end()-1].split('x'))
    return size

def video_fps(FFMPEG_BINARY, filename):
    # This function is substantially based on one found at http://zulko.github.io/moviepy/
    line = load_video_data(FFMPEG_BINARY, filename)

    # get the frame rate
    match = re.search("( [0-9]*.| )[0-9]* (tbr|fps)", line)
    fps = float(line[match.start():match.end()].split(' ')[1])
    return fps

def video_duration(FFMPEG_BINARY, filename):
    # This function is substantially based on one found at http://zulko.github.io/moviepy/
    line = load_video_data(FFMPEG_BINARY, filename)

    # get duration (in seconds)
    line = [l for l in lines if 'Duration: ' in l][0]
    match = re.search(" [0-9][0-9]:[0-9][0-9]:[0-9][0-9].[0-9][0-9]", line)
    hms = map(float, line[match.start()+1:match.end()].split(':'))
    duration = cvsecs(*hms)
    return duration
    # nframes = int(duration*fps)
    
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
    sec = timedelta(sec)
    d = datetime(1900,1,1) + sec
    
    return '{:%H:%M:%S}'.format(d)
