from facebookads.adobjects.campaign import Campaign
from facebookads import exceptions
from datetime import date
from time import sleep
import create_carousel as carousel
import commentjson as json
import psycopg2.extras
import get_targeting
import urlparse
import psycopg2
import logging
import random
import header
import adset
import sys
import os

def check_number_of_ads(number_of_items,number_of_cards,number_of_ads,adset_id,caption,country):
	logging.info('In check number of ads')
	if number_of_ads > (number_of_items/number_of_cards):
		serialized_ads_creation(adset_id,rows,(number_of_items/number_of_cards),number_of_cards,caption,country)
		number_of_ads -= (number_of_items/number_of_cards)
		return number_of_ads
	else :
		serialized_ads_creation(adset_id,rows,(number_of_items/number_of_cards),number_of_cards,caption,country)
		return 0

def serialized_ads_creation(adset_id,rows,number_of_ads,number_of_cards,caption,country):
	j=0
	k=number_of_cards
	logging.info('In serialized ads creation')
	for i in xrange(number_of_ads):
		design_list = rows[j:k]
		ad_name = caption+' top items '+str(j)+'-'+str(k)
		ad_created = carousel.create_carousel_ad(caption,adset_id,ad_name,design_list,False,'www.mirraw.com/store/'+name,caption+'_'+str(i),country)
		if not(ad_created):
			logging.error('Error creating ad for design ids %s' % design_list)
		else:
			logging.info('Ad created successfully for design ids %s' % design_list)
		j = k
		k += number_of_cards
	return True;

connection1 = None
try:
	FORMAT = '%(name)s:%(levelname)s:%(asctime)-15s:%(message)s'
	logging.basicConfig(filename='%s-facebook-automated.log' % date.today(),format=FORMAT, level=logging.DEBUG)
	logging.getLogger('read_campaign')
	# Reading from config.json
	file = json.loads(open('config.json').read())

	campaign_id = file['campaign_id']
	categories = file['categories'].split(',')
	number_of_ads = int(file['number_of_ads'])
	number_of_items = int(file['number_of_items'])
	number_of_cards = int(file['number_of_cards'])
	interest_list = file['interest_list'].split(',')
	age_min = int(file['age_min'])
	age_max = int(file['age_max'])
	daily_budget = file['daily_budget']
	bid_amount = file['bid_amount']
	start_time = file['start_time']
	end_time = file['end_time']

	connection1 = header.create_connection(os.environ['FB_APP_DATABASE_URL'])
	dbCursor = connection1.cursor(cursor_factory=psycopg2.extras.DictCursor)

	campaign = Campaign(campaign_id)
	campaign.remote_read(fields=[Campaign.Field.name,Campaign.Field.id])
	countries = campaign[Campaign.Field.name].split(',')

	for country in countries:
		for name in categories:
			for interest in interest_list:
				adset_name = interest.replace('.txt','')+'-'+name
				interests = get_targeting.list_ids(interest)
				adset_id = adset.create_adset(country,interests,age_min,age_max,adset_name,campaign_id,daily_budget,bid_amount,start_time,end_time)
				dbCursor.execute("SELECT l.design_id FROM line_items l,categories_designs cd,categories c WHERE cd.design_id=l.design_id AND c.id=cd.category_id AND l.created_at > current_date - interval '90' day and c.name like '" + name + "' GROUP BY l.design_id,c.name ORDER BY count(l.id) DESC LIMIT "+str(number_of_items))
				rows=dbCursor.fetchall()
				number_of_items = max(number_of_items,len(rows))
				if number_of_items%number_of_cards!=0:
					number_of_items -= (number_of_items%number_of_cards)
				remaining = number_of_ads
				while remaining > 0:
					remaining=check_number_of_ads(number_of_items,number_of_cards,remaining,adset_id,name,country)
					random.shuffle(rows)
				sleep(45)
			sleep(45)
		sleep(45)
	sleep(45)

except psycopg2.DatabaseError, e:
	logging.error('Error %s' % e)

except exceptions.FacebookError, e:
	logging.error('Error %s' % e)

except StandardError, e:
	logging.error('Error %s' % e)

finally:
	if connection1:
		connection1.close()