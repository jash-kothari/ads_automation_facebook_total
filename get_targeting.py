from facebookads.adobjects.targetingsearch import TargetingSearch
from facebookads.adobjects.targeting import Targeting
from time import sleep
import logging
import header
from datetime import date
import json

FORMAT = '%(asctime)-15s %(message)s %(pathname)s'
logging.basicConfig(filename='%s-facebook-automated.log' % date.today(),format=FORMAT, level=logging.DEBUG)
def list_ids(name):
	interest_ids=[]
	with open(name) as fp:
	    for line in fp:
	    	print line
			# query = raw_input("Enter query for targeting customer type.\n")
		params = {
				'q': line,
				'type': 'adinterest',

			}

		resp = TargetingSearch.search(params=params)[0]
		resp=json.loads(str(resp).replace('<TargetingSearch> ',''))
		interest_ids.append(str(resp['id']))
	logging.info(interest_ids)
	sleep(60)
	return interest_ids