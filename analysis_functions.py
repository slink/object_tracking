import numpy as np
from skimage import filter as filt 
from scipy.misc import imread
from scipy import ndimage

from helper_functions import background_image_list, test_image_list

def find_median_background(image_list, channel = 0, axis = 2):
    # image_list = background_image_list(image_folder, n)
    for i, filename in enumerate(image_list):
        if i == 0: background_temp_data = imread(filename)[:,:,channel]
        else: background_temp_data = np.dstack((background_temp_data, imread(filename)[:,:,channel]))
    
    return np.mean(background_temp_data, axis = axis)

def pixel_distance(tup1, tup2):
    # sqrt((x2 - x1)^2 + (y2 - y1)^2)
    return sqrt(np.dot(tup2,tup1))

def background_subtraction(filename, background_image, std = 5):
    test_im = imread(filename)
    for i in test_im.shape[2]:
        filtered = test_im[:,:,i] - background_image
        smoothed = filt.gaussian_filter(filtered, sigma = std)
    return smoothed

def thresholding(image, threshold = 0.25):
    return image > threshold*image.max()

def center_of_mass(image):
    return ndimage.measurements.center_of_mass(image)

def peak_velocity(image_folder, fps = 25, background_images = 10):
    dist = []
    max_ind_n1 = ()

    image_list = background_image_list(image_folder, background_images)
    background_image = find_median_background(image_list)
    
    for i, filename in enumerate(filelist):
        if i == 0:
            bs_image = background_subtraction(filename, background_image)
            com = center_of_mass(thresholding(bs_image)[:,:,0])
            # max_ind =  unravel_index(bs_image.argmax(), bs_image.shape)
            dist.append(pixel_distance(com, com))
            max_ind_n1 = com
        else:
            bs_image = background_subtraction(filename, background_image)
            com = center_of_mass(thresholding(bs_image)[:,:,0])
            # max_ind =  unravel_index(bs_image.argmax(), bs_image.shape)
            dist.append(pixel_distance(max_ind_n1, com))
            max_ind_n1 = com
    return np.array(dist) / float(fps)