import glob, os

im_list = glob.glob('image-*.jpeg')
[os.remove(im) for im in im_list]

png_list = glob.glob('*.png')
[os.remove(png) for png in png_list]

csv_list = glob.glob('*.csv')
[os.remove(csv) for csv in csv_list]


