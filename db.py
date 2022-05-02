from pymongo import MongoClient
from datetime import datetime
import json
from secrets import json_secret

class DB:
    DB_HOST = json_secret('db', 'host')
    DB = json_secret('db', 'db')
    DB_TABLE = json_secret('db', 'db_table')

    def __init__(self, host=DB_HOST, db=DB, table=DB_TABLE):
        self.host = host
        self.db = db
        self.table = table
        self.connect()

    def connect(self):
        self.client = MongoClient(host=self.host, port=27017)
        self.client_db = self.client[self.db]
        self.client_table = self.client_db[self.table]

    def disconnect(self):
        self.client.close()

    def read_json(self, path):
        with open(path) as file:
            return json.load(file)

    def find(self, date):
        doc = self.client_table.find_one({"date": date})
        return doc

    def find_all(self, date):
        doc = self.client_table.find({"date": date})
        return doc

    def find_dates(self, start, end):
        doc = self.client_table.find({'date': {'$lt': end, '$gte': start}})
        return list(doc)

    def count(self, date):
        doc = self.client_table.count_documents({"date": date})
        return doc

    def delete(self, date):
        query = {"date": date}
        result = self.client_table.delete_one(query)
        result
        print(f"Data deleted: {result}")

    def update(self, date, json_data):
        query = {"date": date}
        data = {"$set": json_data}
        result = self.client_table.update_one(query, data)
        result
        print(f"Data updated: {result}")

    def is_in_db(self, json_data):
        entries = self.find_all(json_data['date'])
        for item in entries:
            if item['date'] == json_data['date']:
                if item['entity'] == json_data['entity']:
                    if item['amount'] == json_data['amount']:
                        return True
        else:
            return False

    def insert(self, json_data):
        if not self.is_in_db(json_data):
            self.client_table.insert_one(json_data)
            print(f"Data entered: {json_data}")
        else:
            print(f"Skipping: {json_data}")

# DB_HOST = json_secret('db', 'host')
# DB = json_secret('db', 'db')
# DB_TABLE = json_secret('db', 'db_table')

# a = DB(DB_HOST, DB, DB_TABLE)
# a.find('2022-04-23', 40050, "Xito Fontanar Chia")

