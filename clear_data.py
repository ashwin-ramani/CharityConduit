# The following script is never automatically run by the website. It is only run by a user, and completely wipes the entire database.
# Use this script with extreme caution.


import pymongo
from pymongo import MongoClient

cluster = MongoClient("mongodb+srv://ashwinrramani:0CxvlK09zaIzHzOg@charitycompass.6wgbyhi.mongodb.net/?retryWrites=true&w=majority&appName=CharityCompass")
db = cluster["CharityCompass"]
db["users"].delete_many({})
db["organizations"].delete_many({})
db["shifts"].delete_many({})

print("All MongoDB entries successfully deleted across 3 collections.")