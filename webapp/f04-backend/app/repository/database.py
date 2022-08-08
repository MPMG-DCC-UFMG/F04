from pymongo import MongoClient
from dotenv import load_dotenv, find_dotenv
import os

load_dotenv(override=True)

MONGO_USER = os.getenv('DB_USERNAME')
MONGO_PASS = os.getenv('DB_PASSWORD')
MONGO_HOST = os.getenv('DB_HOST')

mongo = MongoClient('mongodb://%s:%s@%s' %
                    (MONGO_USER, MONGO_PASS, MONGO_HOST))
print('mongodb://%s:%s@%s' % (MONGO_USER, MONGO_PASS, MONGO_HOST))


def get_db():
    yield mongo.f04
