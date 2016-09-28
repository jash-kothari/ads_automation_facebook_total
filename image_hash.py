from facebookads.adobjects.adimage import AdImage
from facebookads import exceptions
from PIL import Image as Img
from datetime import date
from time import sleep
import logging
import header
import urllib
import os

def get_image_hash(url,name):
	try:
		FORMAT = '%(asctime)-15s %(message)s %(pathname)s'
		logging.basicConfig(filename='%s-facebook-automated.log' % date.today(),format=FORMAT, level=logging.DEBUG)
		logging.info('Downloading image')
		urllib.urlretrieve(url,name)
		image1 = Img.open(header.PWD+'/'+name)
		width,height = image1.size
		size = width if width < height else height
		# The following code is for center cropping
		image1 = image1.crop(((width/2)-(size/2),(height/2)-(size/2),(width/2)+(size/2),(height/2)+(size/2)))
		image1 = image1.resize((1080,1080),Img.ANTIALIAS)
		image1.save(name)
		image1.close()
		image = AdImage(parent_id=header.my_account['id'])
		image[AdImage.Field.filename] = name
		logging.info('Uploading image')
		sleep(15)
		image.remote_create()
		os.remove(name)
		logging.info('Deleted image locally')

	except OSError, e:
		logging.error('Error %s' % e)
		return False

	except exceptions.FacebookError, e:
		logging.error('Error %s' % e)
		return False

	return image[AdImage.Field.hash]

def get_image_link(name,image_id):
	image_link=""
	extensions=['jpg','tif','gif','bmp','png','jpeg','psd','jp2','xcf','JPG','JPEG']
	for extension in extensions:
		if extension in name:
			image_link = header.base_url+str(image_id)+'/'+name.replace('.'+extension,'') + header.size+'.'+extension 
	return image_link