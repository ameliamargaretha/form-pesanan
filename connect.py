from pymongo import MongoClient
import os


client = MongoClient(os.environ['MONGODB_URI'])
db = client['form']
p_db = db['pesanan']
