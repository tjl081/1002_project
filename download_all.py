from pymongo import MongoClient # pip install "pymongo[srv]"
import os
import json
from bson.json_util import dumps # converts mongodb cursor into python suitable 
import csv
import pandas as pd
import pprint



pp = pprint.PrettyPrinter(indent=4)
# THIS SCRIPT JUST QUERIES THE DATABASE AND CONVERTS THE RESULTS TO A CSV
# INDEX NOT YET IMPLEMENTED
# ALL RESULTS: ~35s
# FILTER TO 3 YEARS: < 10s



def get_db():
    """helper function, returns the resale price table as an object to run operations (like querying) on"""
    PATH = os.getcwd() + '\\data\\'
    CONNECTION_STR = ""
    with open(PATH + '/access_url.txt', 'r') as f:
        CONNECTION_STR = f.readline()
    print(CONNECTION_STR)
    client = MongoClient(CONNECTION_STR)
    db = client.test
    resale_prices = db["resale_prices"]
    return resale_prices


db = get_db() # connection itself takes ~1-2s
# db.create_index([("town", 1)])
# db.create_index([("flat_type", 1)])
# db.create_index([("flat_model", 1)])
# db.create_index([("street_name", 1)])
print(db.index_information())
# c = db.find({"$and" : [{"town": {"$eq": "ANG MO KIO"}}]}, limit=2000, projection={'_id': False}).sort("month", -1).explain()['executionStats']
# pp.pprint(c)

# cursor = db.find({"month": {"$gte": "1995-01"}}, limit=0,  projection={'_id': False})
# # result = json.loads(dumps(cursor))
# result = list(cursor)

# # print the total number of documents returned in a MongoDB collection
# print ("total docs returned by find():", len( result ))

# print(result[0])

# df = pd.DataFrame(result)

# print(df.head(5))
# csv_export = df.to_csv("out.csv", index=False)
