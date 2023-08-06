"""This module provides a connection to the database"""
import os
from pymongo import MongoClient
from pymongo.database import Database
from dotenv import load_dotenv
load_dotenv()

def get_database() -> Database:
    """Returns a connection to the database"""
    client = MongoClient(os.getenv('DB_CONNECTION_STRING'))
    return client[os.getenv('DB_NAME')]


if __name__ == '__main__':
    db = get_database()
    # test db conenction by printing all collections
    print(db.list_collection_names())
