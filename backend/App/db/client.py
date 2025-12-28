from pymongo import MongoClient
import os


MONGO_URI= os.getenv("MONGO_URI")

db_client = MongoClient(MONGO_URI).scheduling_db