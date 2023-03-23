import pymongo

class DBConnector:
    def __init__(self):
        connection_string = "mongodb://localhost:27017"
        client = pymongo.MongoClient(connection_string)
        self.db = client['mwizz_db']

    def db_update_status(self,collection,request_id,state,url =None):
        if state =="done":
            self.db[collection].update_one({ "_id" : request_id },{ "$set": {"state":state,"dashboardUrl": "https://localhost:3000"}},upsert=True)
        else:
            self.db[collection].update_one({ "_id" : request_id },{ "$set": {"state":state}},upsert=True)
        
