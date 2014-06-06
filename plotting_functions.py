import matplotlib.pyplot as plt
import numpy as np

def thresholding(image, threshold = 0.25):
    return image > threshold*image.max()

def test_plotter(im, labels):
    """ plots the first three images in a row, 
        and then the second three images in a row 
        -- the second set has a Grey cmap"""

    bool_im_flag = [(type(image) == np.ndarray and type(image[0,0])) == np.bool_ for image in im]

    plt.subplot(2, 3, 1)
    if bool_im_flag[0]: plt.imshow(im[0], cmap = 'Greys')
    else: plt.imshow(im[0]), plt.colorbar(orientation = 'horizontal')
    plt.axis('off')
    plt.title(labels[0])

    plt.subplot(2, 3, 2)
    if bool_im_flag[1]: plt.imshow(im[1], cmap = 'Greys')
    else: plt.imshow(im[1]), plt.colorbar(orientation = 'horizontal') 
    plt.axis('off')
    plt.title(labels[1])

    plt.subplot(2, 3, 3)
    if bool_im_flag[2]: plt.imshow(im[2], cmap = 'Greys')
    else: plt.imshow(im[2]), plt.colorbar(orientation = 'horizontal')  
    plt.axis('off')
    plt.title(labels[2])

    plt.subplot(2, 3, 4)
    plt.imshow(im[3], cmap = 'Greys')
    plt.axis('off')
    plt.title(labels[3])

    plt.subplot(2, 3, 5)
    plt.imshow(im[4], cmap = 'Greys')
    plt.axis('off')
    plt.title(labels[4])

    plt.subplot(2, 3, 6)
    plt.imshow(im[5], cmap = 'Greys')
    plt.axis('off')
    plt.title(labels[5])

    fig = plt.gcf()
    fig.set_size_inches((20, 8))

def image_cmap_view(image, labels):
    """ plots one image r,g,b, all in a row, 
        and then calls a naive thresholding algorithm 
        and does it again with threshholded r,g,b images"""    
    plt.subplot(2, 3, 1)
    plt.title(labels[0])
    plt.imshow(image[:,:,0], cmap='Reds')
    plt.axis('off')
    plt.colorbar(orientation = 'horizontal')

    plt.subplot(2, 3, 2)
    plt.title(labels[1])
    plt.imshow(image[:,:,1], cmap='Greens')
    plt.axis('off')
    plt.colorbar(orientation = 'horizontal')

    plt.subplot(2, 3, 3)
    plt.title(labels[2])
    plt.imshow(image[:,:,2], cmap='Blues')
    plt.axis('off')
    plt.colorbar(orientation = 'horizontal')
    
    plt.subplot(2, 3, 4)
    plt.title(labels[3])
    plt.imshow(thresholding(image[:,:,0]), cmap='Reds')
    plt.axis('off')
    plt.colorbar(orientation = 'horizontal')

    plt.subplot(2, 3, 5)
    plt.title(labels[4])
    plt.imshow(thresholding(image[:,:,1]), cmap='Greens')
    plt.axis('off')
    plt.colorbar(orientation = 'horizontal')

    plt.subplot(2, 3, 6)
    plt.title(labels[5])
    plt.imshow(thresholding(image[:,:,2]), cmap='Blues')
    plt.axis('off')
    plt.colorbar(orientation = 'horizontal')

    fig = plt.gcf()
    fig.set_size_inches((20, 8))

