#Add to header of your file
from facebookads.adobjects.adaccountuser import AdAccountUser
from facebookads.adobjects.adaccount import AdAccount
from facebookads.api import FacebookAdsApi
from facebookads.objects import AdUser
from facebookads import objects
import psycopg2
import urlparse
import json
import os
#Initialize a new Session and instantiate an API object:

my_app_id = os.environ['AUTO_ADS_FB_APP_ID']
my_app_secret = os.environ['AUTO_ADS_FB_APP_SECRET']
my_access_token = os.environ['AUTO_ADS_FB_APP_ACCESS_TOKEN'] # Your user access token
page_id = os.environ['FB_PAGE_ID']
base_url='https://assets1.mirraw.com/images/'
size='_large'
PWD = os.environ['PWD']
FacebookAdsApi.init(my_app_id, my_app_secret, my_access_token)
me = AdUser(fbid='me')
my_account = me.get_ad_accounts()[0]
my_account=json.loads(str(my_account).replace('<AdAccount> ',''))
def create_connection(database_url):
	urlparse.uses_netloc.append("postgres")
	database_url = urlparse.urlparse(database_url)
	connection = psycopg2.connect( database=database_url.path[1:], user=database_url.username, password=database_url.password, host=database_url.hostname, port=database_url.port )
	return connection
def close_connection(connection):
	if connection:
		connection.close()