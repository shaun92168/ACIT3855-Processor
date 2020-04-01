import connexion
import yaml
import logging
import logging.config
from apscheduler.schedulers.background import BackgroundScheduler
import json
import requests
import datetime
import os
from threading import Thread
from pykafka import KafkaClient, common
from flask_cors import CORS, cross_origin

from sqlalchemy import create_engine, and_
from sqlalchemy.orm import sessionmaker
from base import Base
from scan_in import ScanIn
from body_info import BodyInfo

with open('log_conf.yaml', 'r') as f:
    log_config = yaml.safe_load(f.read())
    logging.config.dictConfig(log_config)


with open('app_conf.yaml', 'r') as f:
    app_config = yaml.safe_load(f.read())

# DB_ENGINE = create_engine('sqlite:///records.sqlite')
DB_ENGINE = create_engine('mysql+pymysql://' + app_config['datastore']['user'] + ':' +
                          app_config['datastore']['password'] + '@' + app_config['datastore']['hostname'] +
                          ':' + str(app_config['datastore']['port']) + '/' + app_config['datastore']['db'])
Base.metadata.bind = DB_ENGINE
DB_SESSION = sessionmaker(bind=DB_ENGINE)


logger = logging.getLogger('basicLogger')


def get_record_stats():
    """ Gets record stats """

    logger.info("Start get record stats")
    data = {}
    if os.path.exists(app_config['datastore']['filename']):
        file = open(app_config['datastore']['filename'], 'r')
        data = json.load(file)
        file.close()
        logger.debug(data)
        logger.info("Get record stats complete")
        return data, 200
    else:
        logger.error(app_config['datastore']['filename'] + " does not exist")

SCAN_IN_REQUEST = "http://localhost:8090/scan_in"
BODY_INFO_REQUEST = "http://localhost:8090/body_info"
HEADERS = { "content-type": "application/json" }

def populate_stats():
    """ Periodically update stats """
    logger.info("Start Periodic Processing")

    data = {}
    data_new = {}
    datetime_now = datetime.datetime.now()
    if os.path.exists(app_config['datastore']['filename']):
        file = open(app_config['datastore']['filename'], 'r')
        data = json.load(file)
        file.close()
    else:
        data['num_scanin_records'] = 0
        data['num_bi_records'] = 0
        data['updated_timestamp'] = datetime_now
        print(data)

    scan_response = requests.get(SCAN_IN_REQUEST,
                                 params={'startDate':data['updated_timestamp'], 'endDate':datetime_now})
    num_scan_response = 0
    if scan_response.status_code == 200:
        num_scan_response = len(scan_response.json())
        logger.info("Number of new scan response: " + str(num_scan_response))
    else:
        logger.error("error: did not get scan in response")

    bi_response = requests.get(BODY_INFO_REQUEST,
                               params={'startDate': data['updated_timestamp'], 'endDate': datetime_now})
    num_bi_response = 0
    if bi_response.status_code == 200:
        num_bi_response = len(bi_response.json())
        logger.info("Number of new body info response: " + str(num_bi_response))
    else:
        logger.error("error: did not get body info response")

    data_new['num_scanin_records'] = data['num_scanin_records'] + num_scan_response
    data_new['num_bi_records'] = data['num_bi_records'] + num_bi_response
    data_new['updated_timestamp'] = datetime_now.strftime("%Y-%m-%dT%H:%M:%S.%f")[:-4]+"Z"

    with open("data.json", "w") as json_file:
        json.dump(data_new, json_file)

    logger.info("Periodic Processing End")



def init_scheduler():
    sched = BackgroundScheduler(daemon=True)
    sched.add_job(populate_stats,
                  'interval',
                  seconds=app_config['scheduler']['period_sec'])
    sched.start()

app = connexion.FlaskApp(__name__, specification_dir='')
app.add_api("openapi.yaml")
CORS(app.app)
app.app.config['CORS_HEADERS'] = 'Content-Type'

if __name__ == "__main__":
    # run our standalone gevent server
    init_scheduler()
    app.run(port=8100, use_reloader=False)