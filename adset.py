from facebookads.adobjects.targetingsearch import TargetingSearch
from facebookads.adobjects.targeting import Targeting
from facebookads.adobjects.adset import AdSet
from facebookads import exceptions
from datetime import date
from time import sleep
import logging
import header
import json
import sys

def create_adset(country_list,interest_list,age_min,age_max,adset_name,campaign_id,daily_budget,bid_amount,start_time,end_time):
	try:
		FORMAT = '%(asctime)-15s %(pathname)s %(message)s'
		logging.basicConfig(filename='%s-facebook-automated.log' % date.today(),format=FORMAT, level=logging.DEBUG)
		targeting = {
			Targeting.Field.geo_locations: {
				Targeting.Field.countries: country_list,
			},
			Targeting.Field.interests: interest_list,
			Targeting.Field.age_min: age_min,
			Targeting.Field.age_max: age_max,
		}
		adset = AdSet(parent_id=header.my_account['id'])
		adset.update({
			AdSet.Field.name: adset_name,
			AdSet.Field.campaign_id: campaign_id,
			AdSet.Field.daily_budget: daily_budget,
			AdSet.Field.billing_event: AdSet.BillingEvent.impressions,
			AdSet.Field.optimization_goal: AdSet.OptimizationGoal.reach,
			AdSet.Field.bid_amount: bid_amount,
			AdSet.Field.targeting: targeting,
			AdSet.Field.start_time: start_time,
			AdSet.Field.end_time: end_time,
		})
		adset.remote_create(params={
			'status': AdSet.Status.paused,
		})
		logging.info(adset)

	except exceptions.FacebookError, e:
		logging.error('Error %s' % e)
		return None

	sleep(60)
	return adset[AdSet.Field.id]