#!/Users/slink/anaconda/bin/python

import os, glob, re, argparse
import numpy as np
import subprocess as sp
from scipy.misc import imread, imshow
from datetime import timedelta, datetime
import matplotlib.pylab as plt

def save_color_channel(file_name, channel = 0):    
	"""
	save_color_channel(file_name, channel = 0) takes an image and 
	returns a new image with only the color channel specified
	"""
	if channel == 0: color = 'Reds'
	elif channel == 1: color = 'Blues'
	elif channel == 2: color = 'Greens'
	
	plt.imshow(-imread(file_name)[:,:,channel], cmap=color)
	plt.axis('off')
	file_name, file_ext = os.path.splitext(file_name)
	plt.savefig(file_name + '_'+ color + '.png', format = 'png', dpi = 300,\
				frameon = False, bbox_inches = 'tight') # pad_inches = 0
	os.remove(file_name + file_ext)


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
	
	FFMPEG_BINARY = 'ffmpeg'
	
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
			


	#if args.verbosity:
	#	print "verbosity turned on"
