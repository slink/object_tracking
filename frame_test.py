import os
import numpy as np
from scipy.misc import imread
from skimage.morphology import label, remove_small_objects
from skimage.measure import regionprops
from still_extractor import segment_extractor, still_cropper, HHMMSS


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

    file_name, file_ext = os.path.splitext(file_name)
    test_file_name = file_name + ".csv"
    
    if not os.path.isfile(test_file_name):
        np.savetxt(test_file_name, x, delimiter="," , fmt = '%.2f')
    else: 
        with open(test_file_name,'a') as f_handle:
            np.savetxt(f_handle, x, delimiter="," , fmt = '%.2f')

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
	# x0, y0 are the location of the centroid for each region
	# x1 and x2 are the *major* axis from the center outward
	# y1 and y2 are the *minor* axis from the center outward
	# bx and by are the bounding box on the regions found 
	for i, props in enumerate(regions):
		centroid = props.centroid
		y0.append(centroid[0])
		x0.append(centroid[1])
		area.append(props.area)

		# orientation = props.orientation
		# x1.append(x0[i] + math.cos(orientation) * 0.5 * props.major_axis_length)
		# y1.append(y0[i] - math.sin(orientation) * 0.5 * props.major_axis_length)
		# x2.append(x0[i] - math.sin(orientation) * 0.5 * props.minor_axis_length)
		# y2.append(y0[i] - math.cos(orientation) * 0.5 * props.minor_axis_length)

		# ax.plot((x0[i], x1[i]), (y0[i], y1[i]), '-r', linewidth=2.5)
		# ax.plot((x0[i], x2[i]), (y0[i], y2[i]), '-r', linewidth=2.5)
		# ax.plot(x0[i], y0[i], '.g', markersize=15)

		# (min_row, min_col, max_row, max_col) are the returns from the bbox
		minr, minc, maxr, maxc = props.bbox
		# bx.append((minc, maxc, maxc, minc, minc))
		# by.append((minr, minr, maxr, maxr, minr))
		ymin.append(maxr)
		# ax.plot(bx[i], by[i], '-b', linewidth=2.5)
		# ax.axhline(maxr, color='g', linewidth=2.5)

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


def video_track(FFMPEG_BINARY, video_name, fps = '1', start_time = 0, end_time = 30, duration = 10):
    
    thresh=0.03
    zoi = np.s_[150:900, 850:1050]

    ymin_global = []

    for segment_start in np.arange(start_time, end_time, duration): # 10 second increments
        
        # pulling the stills out of the movie with ffmpeg
        stills = segment_extractor(FFMPEG_BINARY, video_name, fps = str(fps), start_time = HHMMSS(segment_start), duration = duration)
        # cropping the stills
        cropped_files = [still_cropper(still, zoi = zoi) for still in stills]

        for i, file_name in enumerate(cropped_files[1:-1]):
            frame_curr = rgb2gray(imread(cropped_files[i]))
            frame_prev = rgb2gray(imread(cropped_files[i-1]))
            frame_fut = rgb2gray(imread(cropped_files[i+1]))

            # going from floats to ints
            frame_fut *= 255
            frame_fut = frame_fut.astype(int)
            # thresholding 
            thresh_mat = frame_fut >= thresh * 255
            # region_props
            centroid, ymin, area = region_props(thresh_mat, 100, conn = 40)
            # frame_diff=imabsdiff(frame_diff_f, frame_diff_b)
            # frame_diff_b=imabsdiff(frame_curr, frame_prev)
            if len(ymin) is not 0:
            	print ymin[0]
                ymin_global.append(ymin[0])
            else:
                ymin_global.append(np.nan)

        removal_check = [os.remove(cropped_file) for cropped_file in cropped_files]
        
    return ymin_global
