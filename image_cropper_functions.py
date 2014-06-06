from __future__ import division
import Image, glob, os

def cropper(image, dims = (300, 600)):
	
	file_name, file_extension = os.path.splitext(image)
	im = Image.open(image)
	width, height = im.size   # Get dimensions
	(new_width, new_height) = dims

	left = int((width - new_width)/2)
	top = int((height - new_height)/2)
	right = int((width + new_width)/2)
	bottom = int((height + new_height)/2)

	im = im.crop((left, top, right, bottom))
	im.save('cropped_'+image, format = file_extension[1:])

def files(extentsion = '.jpeg'):
	
	extentsion = '*' + extentsion
	file_list = glob.glob(extentsion)
	return file_list

if __name__ == '__main__':
	
	folder_name = '/Users/slink/src/object_tracking/test_videos'
	extentsion = '.jpeg'
	dims = (300, 600)

	current_dir = os.getcwd()
	os.chdir(folder_name)
	file_list = files(extentsion)

	try:
		for i, f in enumerate(file_list):
			print '{:%}'.format(i/len(file_list))
			cropper(f, dims)
	except Exception, e:
		raise e
	finally:
		os.chdir(current_dir)

		


