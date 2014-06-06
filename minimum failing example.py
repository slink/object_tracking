
# coding: utf-8

# In[1]:

import glob
import numpy as np
from skimage.morphology import label, remove_small_objects
from skimage.filter import gaussian_filter
from scipy.misc import imread
import matplotlib.pylab as plt
# get_ipython().magic(u'matplotlib inline')


# In[2]:

stills = glob.glob('*.jpeg')
zoi = np.s_[150:900, 850:1050]


# In[3]:

def threshold_image(x, thresh):
	"""
	threshold_image(x) converts a float image to ints and rescales the result
	and then applies a threshold, returning a boolean matrix
	"""
	# going from floats to ints
	x *= 255
	x = x.astype(int)
	# thresholding 
	y = x >= (thresh * 255)
	return y

def rgb2gray(image):
	"""
    The sRGB color space is defined in terms of the CIE 1931 linear 
	luminance Y, which is given by: 0.2126 * R + 0.7152 * G + 0.0722 * B 
	In the Y'UV and Y'IQ models used by PAL and NTSC, the rec601 luma (Y') 
	component is computed as: 0.2989 * R + 0.5870 * G + 0.1140 * B 
	"""
	if image.shape[2] is 4: # RGBA
		image = image[:,:,:3] # discard alpha channel
	elif image.shape[2] < 3: # not even 3 channels
		assert image.shape[2] is 3, "This image does not have RGB channel data" 
	
	return 0.2126 * image[:,:,0] + 0.7152 * image[:,:,1] + 0.0722 * image[:,:,2]

def imabsdiff(X, Y):
	"""
    only run on greyscale images
	image1 and image2 are real, nonsparse numeric arrays with the same class and size.
    """
	assert X.shape == Y.shape, "The images do not have the same shape" 
	assert type(X[0,0]) == type(Y[0,0]), "Image elements do not have the same type" 

	return np.abs(X-Y)


# In[4]:

n = 9
thresh = 0.05
frame_curr = rgb2gray(imread(stills[n/2])[zoi[0], zoi[1],:])
frame_prev = rgb2gray(imread(stills[0])[zoi[0], zoi[1],:])
frame_fut = rgb2gray(imread(stills[n])[zoi[0], zoi[1],:])

frame_diff_b = imabsdiff(frame_curr, frame_prev)
frame_diff_f = imabsdiff(frame_fut, frame_curr)
frame_diff = imabsdiff(frame_diff_b, frame_diff_f)
# frame_sum = (frame_diff_b + frame_diff_f)/2 

# frame_diff = imabsdiff(frame_diff_f, frame_diff_f)
thresh_mat = threshold_image(frame_diff_b, thresh)


# In[5]:

plt.subplot(1,4,1)
a = frame_diff
plt.imshow(a)

plt.subplot(1,4,2)
b = gaussian_filter(a, .1)
plt.imshow(b)
plt.savefig('1.jpeg')


# In[6]:

plt.subplot(1,4,1)
a = frame_diff
plt.imshow(a)

plt.subplot(1,4,2)
b = gaussian_filter(a, .1)
plt.imshow(b)

plt.subplot(1,4,3)
c = threshold_image(b, .2)
plt.imshow(c)
plt.savefig('2.jpeg')


# In[ ]:



