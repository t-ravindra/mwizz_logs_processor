import pymongo
from bson.objectid import ObjectId

class DBConnector:
    def __init__(self):
        connection_string = "mongodb://localhost:27017"
        client = pymongo.MongoClient(connection_string)
        self.db = client['mwizz_db']

    def db_update_status(self,collection,request_id,state,url="http://10.171.247.124:5601/app/dashboards#/view/5f9519f0-c97f-11ed-9b11-6945b3ed2302?_g=(refreshInterval:(pause:!t,value:0),time:(from:now-15m,to:now))&_a=(viewMode:view)"):
        if state =="done":
            self.db[collection].update_one({ "_id" : ObjectId(request_id) },{ "$set": {"state":state,"dashboardUrl": url}},upsert=True)
        else:
            self.db[collection].update_one({ "_id" : (request_id) },{ "$set": {"state":state, "dashboardUrl": url}},upsert=True)

