from facebookads.adobjects.adcreativelinkdatachildattachment import AdCreativeLinkDataChildAttachment
from facebookads.adobjects.adcreativeobjectstoryspec import AdCreativeObjectStorySpec
from facebookads.adobjects.adcreativelinkdata import AdCreativeLinkData
from facebookads.adobjects.adcreative import AdCreative
from facebookads.adobjects.campaign import Campaign
from facebookads.objects import Ad
from facebookads import exceptions
from datetime import date
from time import sleep
import psycopg2.extras
import image_hash
import psycopg2
import urlparse
import logging
import header
import json
import sys
import os

def create_carousel_ad(caption,adset_id,ad_name,design_list,land_on_design,url,campaign_tag,country_code):
	FORMAT = '%(name)s:%(levelname)s:%(asctime)-15s:%(message)s'
	logging.basicConfig(filename='%s-facebook-automated.log' % date.today(),format=FORMAT, level=logging.DEBUG)
	logging.getLogger('create_carousel')
	logging.info('In create carousel')
	connection = None
	simple_list=[]
	utm_medium='exp'
	try:
		connection = header.create_connection(os.environ['FB_APP_DATABASE_URL'])
		cursor = connection.cursor(cursor_factory=psycopg2.extras.DictCursor)
		for design_id in design_list:
			cursor.execute('SELECT designer_id,discount_price from designs where id='+str(design_id[0]))
			row=cursor.fetchone()
			cursor.execute('SELECT id,photo_file_name FROM images where design_id = '+str(design_id[0]))
			rows=cursor.fetchone()
			cursor.execute('SELECT name FROM "categories" INNER JOIN "categories_designs" ON "categories"."id" = "categories_designs"."category_id" WHERE design_id ='+str(design_id[0]))
			category_name = cursor.fetchone()
			cursor.execute("SELECT rate FROM currency_converts WHERE country_code = '" + country_code +"'")
			rate=cursor.fetchone()
			image_link=image_hash.get_image_link(rows['photo_file_name'],rows['id'])
			product1 = AdCreativeLinkDataChildAttachment()
			if land_on_design:
				product1[AdCreativeLinkDataChildAttachment.Field.link] = 'www.mirraw.com/designers/'+str(row['designer_id'])+'/designs/'+str(design_id[0])+'?utm_source=facebook-auto&utm_medium='+utm_medium+'&utm_campaign='+campaign_tag
			else:
				product1[AdCreativeLinkDataChildAttachment.Field.link] = url+'?pid='+str(design_id)+'&utm_source=facebook&utm_medium='+utm_medium+'&utm_campaign='+campaign_tag
			product1[AdCreativeLinkDataChildAttachment.Field.name] = category_name['name']
			price=(row['discount_price']*1.0/rate['rate'])
			product1[AdCreativeLinkDataChildAttachment.Field.description] = 'Price: $' + str(round(price,2))
			logging.info(image_link)
			logging.info(rows['photo_file_name'])
			product1[AdCreativeLinkDataChildAttachment.Field.image_hash] = image_hash.get_image_hash(image_link,rows['photo_file_name'])
			sleep(10)
			simple_list.append(product1)

		link = AdCreativeLinkData()
		link[link.Field.link] = 'www.mirraw.com'
		link[link.Field.child_attachments] = simple_list
		link[link.Field.caption] = caption

		story = AdCreativeObjectStorySpec()
		story[story.Field.page_id] = header.page_id
		story[story.Field.link_data] = link

		creative = AdCreative(parent_id=header.my_account['id'])
		creative[AdCreative.Field.name] = 'MPA Creative'
		creative[AdCreative.Field.object_story_spec] = story
		creative.remote_create()
		creative=json.loads(str(creative).replace('<AdCreative> ',''))

		ad = Ad(parent_id=header.my_account['id'])
		ad[Ad.Field.name] = ad_name
		ad[Ad.Field.adset_id] = adset_id
		ad[Ad.Field.status] = Campaign.Status.paused
		ad[Ad.Field.creative] = {'creative_id': str(creative['id'])}
		logging.info('Creating Ad')
		ad.remote_create()
		logging.info(ad)

	except psycopg2.DatabaseError, e:
		logging.error('Error %s' % e)
		return False

	except StandardError, e:
		logging.error('Error %s' % e)
		return False
	
	except exceptions.FacebookError, e:
		logging.error('Error %s' % e)
		return False

	finally:
		if connection:
			connection.close()
	
	sleep(75)
	return True