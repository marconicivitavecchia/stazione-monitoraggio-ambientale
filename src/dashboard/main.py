from pymongo.mongo_client import MongoClient
from pymongo.server_api import ServerApi

from config import DB_USERNAME,DB_PASSWORD,DB_SERVER

uri = f"mongodb+srv://{DB_USERNAME}:{DB_PASSWORD}@{DB_SERVER}/?retryWrites=true&w=majority"
print(uri)
# Create a new client and connect to the server
client = MongoClient(uri, server_api=ServerApi('1'))

# Send a ping to confirm a successful connection
print("sending ping...")
try:
  client.admin.command('ping')
  print("Pinged your deployment. You successfully connected to MongoDB!")
except Exception as e:
  print(e)

mydb = client["test"]
mycol = mydb["pm5"]
allData = mycol.find()

print(allData)

for x in mycol.find({"boardID": "123"}):
  timestamp = x.get("timestamp")
  pm10 = x.get("PM10")
  pm25 = x.get("PM25")
  print(timestamp, pm10, pm25, sep=",")
