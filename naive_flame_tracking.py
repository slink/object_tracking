# ffmpeg -ss 00:00:11 -t 00:00:15 -i test.mp4 -r 25.0 test%4d.jpg
# import moviepy.video.io.ffmpeg_tools as ffmpeg_tools
# import moviepy.video.io.ffmpeg_reader as ffmpeg_reader

# <codecell>

# %pylab inline
import glob, re, os
from scipy.misc import imread, imsave
import numpy as np
import subprocess as sp
from skimage import filter as filt 
from scipy import ndimage

class naive_flame_tracking(object):
    """docstring for naive_flame_tracking"""
    def __init__(self, image_folder, bkgrd_img_start = 1, 
                bkgrd_img_end = 60, tst_img_start = 85, tst_img_end = 95):
        
        super(naive_flame_tracking, self).__init__()
        
        assert type(image_folder) == str

        assert type(bkgrd_img_start) == int
        assert type(bkgrd_img_end) == int
        assert type(tst_img_start) == int
        assert type(tst_img_end) == int

        self.image_folder = os.path.join(os.getcwd(), image_folder)
        self.bkgrd_image_start = bkgrd_img_start
        self.bkgrd_image_end = bkgrd_img_end
        self.tst_img_start = tst_img_start 
        self.tst_img_end = tst_img_end


    def _background_image_list(self):
        image_list = []
        for i in range(self.bkgrd_image_start, self.bkgrd_image_end+1):
            if i < 10:  
                test_name = 'test000' + str(i) + '.jpg'
                filename = os.path.join(self.image_folder, test_name)
                image_list.append(filename)
            else:
                test_name = 'test00' + str(i) + '.jpg'
                filename = os.path.join(self.image_folder, test_name)
                image_list.append(filename)

        
        return image_list

    def _test_image_list(self):
        image_list = []
        for i in range(self.tst_img_start, self.tst_img_end+1):
            if i < 10:  
                test_name = 'test000' + str(i) + '.jpg'
                filename = os.path.join(self.image_folder, test_name)
                image_list.append(filename)
            else:
                test_name = 'test00' + str(i) + '.jpg'
                filename = os.path.join(self.image_folder, test_name)
                image_list.append(filename)

        
        return image_list

    def _find_median_background(self, channel = 0, axis = 2):
        
        for i, filename in enumerate(self._background_image_list()):
            if i == 0: background_temp_data = imread(filename)[:,:,channel]
            else: background_temp_data = np.dstack((background_temp_data, imread(filename)[:,:,channel]))
        
        return np.mean(background_temp_data, axis = axis)
        # np.min(background_temp_data, axis = axis)
        # np.median(background_temp_data, axis = axis)

    def _pixel_distance(self, tup1, tup2):
        # sqrt((x2 - x1)^2 + (y2 - y1)^2)
        return np.sqrt(np.dot(tup2,tup1))

    def _background_subtraction(self, filename, background_image, channel = 0, std = 5):
        test_im = imread(filename)[:,:,channel]
        filtered = test_im - background_image
        smoothed = filt.gaussian_filter(filtered, sigma = std)
        return smoothed

    def _thresholding(self, image, threshold = 0.25):
        return image > threshold*image.max()

    def _center_of_mass(self, image):
        return ndimage.measurements.center_of_mass(image)

    def peak_velocity_com(self, fps = 25):
        dist = []
        max_ind_n1 = ()
        background_image = self._find_median_background()
        
        for i, filename in enumerate(self._test_image_list()):
            if i == 0:
                bs_image = self._background_subtraction(filename, background_image)
                com = self._center_of_mass(self._thresholding(bs_image))
                # max_ind =  unravel_index(bs_image.argmax(), bs_image.shape)
                dist.append(self._pixel_distance(com, com))
                max_ind_n1 = com
            else:
                bs_image = self._background_subtraction(filename, background_image)
                com = self._center_of_mass(self._thresholding(bs_image))
                # max_ind =  unravel_index(bs_image.argmax(), bs_image.shape)
                dist.append(self._pixel_distance(com, com))
                max_ind_n1 = com
        
        self.com_vel = np.array(dist) / float(fps)
        return self.com_vel
        

    def _find_front_edge(self, image):
        """
        find_front_edge(image)
        
        takes in a thresholded and filtered image and returns an (x,y) 
        pair of values corresponding to the front edge of the moving 'blob'
        """
        front_col = 0
        for i, column in enumerate(image.T):
            if column.max() == True: 
                front_col = i
                break
                
        row_up = image[:,front_col].argmax()
        row_down = image[:,front_col][::-1].argmax()
        front_row = int(np.mean([row_up, row_down]))
        return (front_col, front_row)

    def peak_velocity_front_edge(self, fps = 25):
        dist = []
        max_ind_n1 = ()
        background_image = self._find_median_background()
        
        for i, filename in enumerate(self._test_image_list()):
            if i == 0:
                bs_image = self._background_subtraction(filename, background_image)
                fe = self._find_front_edge(self._thresholding(bs_image))
                # max_ind =  unravel_index(bs_image.argmax(), bs_image.shape)
                dist.append(self._pixel_distance(fe, fe))
                max_ind_n1 = fe
            else:
                bs_image = self._background_subtraction(filename, background_image)
                fe = self._find_front_edge(self._thresholding(bs_image))
                # max_ind =  unravel_index(bs_image.argmax(), bs_image.shape)
                dist.append(self._pixel_distance(fe, fe))
                max_ind_n1 = fe
        
        self.com_vel = np.array(dist) / float(fps)
        return self.com_vel


"""
plt.plot(peak_velocity(test_image_list()))

background_image = find_median_background()

bob = background_subtraction('test0086.jpg', background_image)
plt.pcolor(bob)
com = center_of_mass(thresholding(bob))
plt.plot(com[1], com[0], 'r*')


test1 = imread('test0086.jpg')[:,:,0]
plt.pcolor(test1)
"""
