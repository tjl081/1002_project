from datetime import datetime
from dis import dis
from geopy.geocoders import Nominatim # pip install geopy
import eel
import numpy as np
import pandas as pd
import json
from bson.json_util import dumps # converts mongodb cursor into python suitable 
import glob
import os
from pymongo import MongoClient
from bson.objectid import ObjectId
from re import search
import requests
from requests.structures import CaseInsensitiveDict
from pprint import pprint

url = "https://api.geoapify.com/v2/place-details?id=id%3D514d368a517c511e40594bfd7b574ec84740f00103f90135335d1c00000000920313416e61746f6d697363686573204d757365756d&apiKey=282342ec9baa42e2ba5897587f10f26c"
url2 = "https://api.geoapify.com/v2/places?categories=education&filter=circle:103.8068432,1.2918389,5000&bias=proximity:103.8068432,1.2918389&limit=20&apiKey=282342ec9baa42e2ba5897587f10f26c"
headers = CaseInsensitiveDict()
headers["Accept"] = "application/json"

resp = requests.get(url, headers=headers)
response = requests.get(url2)
print(response.json())


geoapify = "https://api.geoapify.com/v1/geocode/search?postcode=543301&apiKey=282342ec9baa42e2ba5897587f10f26c"
resp2 = requests.get(geoapify,headers=headers)
#print(resp2.json())


def getPlaces():
    geoapify = "https://api.geoapify.com/v2/places?categories=education&filter=place:517added3d06f95940597de212dd3938f63ff00102f9019bd2d52300000000c00207&limit=20&apiKey=282342ec9baa42e2ba5897587f10f26c"
    headers = CaseInsensitiveDict()
    headers["Accept"] = "application/json"
    resp2 = requests.get(geoapify,headers=headers)
    newdict = resp2.json()
    items = newdict['features']
    newarray = []
    # name_list = []
    # amenity_list = []
    # distance_list = []
    # postcode_list = []
    name = ""
    amenity = ""
    distance =""
    postcode = ""
    
    data_list=[]
    for item in items:
        newarray.append(item['properties'])
    pprint(newarray)
    for i in newarray:
        data_dict = {}#
        name = i['name']
        raw = i['datasource']['raw']
        amenity = raw['amenity']
        distance = i['distance']
        postcode = i['postcode']
        # name_list.append(name)
        # amenity_list.append(amenity)
        # distance_list.append(distance)
        # postcode_list.append(postcode)
        data_dict['name'] = name
        data_dict['amenity'] = amenity
        data_dict['distance'] = distance
        data_dict['postcode'] = postcode
        data_list.append(data_dict)
    return data_list
    #return data_list
    #data_list = data_dict
    #return name_list,amenity_list,distance_list,postcode_list
    #return data_dict
   

        


print(getPlaces())

#print(resp.status_code)
# geolocator = Nominatim(user_agent="geoapiExercises")

# # datatable = get_db()
# place =str(309)+ "," + "ANG MO KIO AVE 1"
# location = geolocator.geocode(place)

#     #traverse the data
# data = location.raw
# loc_data = data['display_name'].split(',')
# loc_data_new = []
# for i in loc_data:
#     replaced = i.replace(' ','')
#     loc_data_new.append(replaced)
# print(loc_data_new)
# print(loc_data_new[-2])




db_object = None

def get_db():
    """helper function, returns the resale price table as an object to run operations (like querying) on"""
    global db_object
    if db_object is None:
        PATH = 'C:\\Users\\Vianiece\\Dropbox\\My PC (LAPTOP-DSCM54BJ)\\Desktop\\INF1002\\project\\1002_project\\data\\'
        CONNECTION_STR = ""
        with open(PATH + '/access_url.txt', 'r') as f:
            CONNECTION_STR = f.readline()
        print(CONNECTION_STR)
        initial_time = datetime.now()
        client = MongoClient(CONNECTION_STR)
        print(f"Connected to MongoDB client in {(datetime.now() - initial_time).total_seconds()}")
        db = client.test
        db_object = db["resale_prices"]

    return db_object

def getRecordId(month,town,flat_type,block,street_name,storey_range,floor_area_sqm,flat_model,lease_commence_date,resale_price,remaining_lease):
    data_table = get_db()
    record = data_table.find_one({"month":month, "town":town,"flat_type":flat_type,"block":block,"street_name":street_name,"storey_range":storey_range,"floor_area_sqm":floor_area_sqm,"flat_model":flat_model,"lease_commence_date":lease_commence_date,"resale_price":resale_price,"remaining_lease":remaining_lease})
    return record["_id"]
def getRecordByRecordId(id):
    data_table = get_db()
    # cursor = data_table.find({'_id': id})
    # result = json.loads(dumps(cursor))
    # return result
    record = data_table.find_one({'_id': ObjectId(id) })
    return record

#print(getRecordByRecordId('6339c62318d5e7121d97a688'))
#print(getRecordId("2022-09","PUNGGOL", "5 ROOM" ,"226C" ,"SUMANG LANE", "13 TO 15" ,114, "PREMIUM APARTMENT" ,2018 ,723000 ,"94 years 07 months"))


# record_dict = getRecordByRecordId('6339c62318d5e7121d97a5ca')
# # for key in record_dict.items():
# #keylist = list(record_dict.keys())

# keylist = list(record_dict.values())
# #print(keylist)
# rowlist= []
# for key in keylist:
    
#     rowlist.append(key)

# print(rowlist)


