from facebookads.adobjects.targetingsearch import TargetingSearch
from facebookads.adobjects.targeting import Targeting
from datetime import date
from time import sleep
import psycopg2.extras
import psycopg2
import logging
import header
import json

FORMAT = '%(name)s:%(levelname)s:%(asctime)-15s:%(message)s'
logging.basicConfig(filename='%s-facebook-automated.log' % date.today(),format=FORMAT, level=logging.DEBUG)
logging.getLogger('get_targeting')
database_url="postgres://postgres:mirraw123@localhost:5432/mirraw_development"
def list_ids(name):
	database_url
	interest_ids=[]
	with open(name) as fp:
	    for line in fp:
		connection = header.create_connection(database_url)
		cursor = connection.cursor(cursor_factory=psycopg2.extras.DictCursor)
		cursor.execute("select interest_id from adinterests where interest_name like '"+line.replace("'","")+"';")
		row = cursor.fetchone()
		if row is None:
			interest_ids.append(str(add_to_adinterests(line,cursor)))
			sleep(2.5)
			connection.commit()
		else:
			interest_ids.append(str(row['interest_id']))
			logging.info('Fetched from table')
	logging.info(interest_ids)
	header.close_connection(connection)
	return interest_ids
def add_to_adinterests(interest,cursor):
	logging.info('Searching Facebok for adinterest '+interest)
	params = {
		'q': interest,
		'type': 'adinterest'
	}

	resp = TargetingSearch.search(params=params)[0]
	resp=json.loads(str(resp).replace('<TargetingSearch> ',''))
	cursor.execute("insert into adinterests (interest_name,interest_id) values ('"+interest.replace('\'','')+"','"+resp['id']+"')")
	return resp['id']
