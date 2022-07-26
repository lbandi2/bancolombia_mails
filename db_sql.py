from mysql.connector import connect, Error
import os
from dotenv import load_dotenv

from utils import string_to_datetime

load_dotenv()

class DB:
    DB_HOST = os.getenv('DBSQL_HOST')
    DB_USER = os.getenv('DBSQL_USER')
    DB_PASSWORD = os.getenv('DBSQL_PASSWORD')
    DB = os.getenv('DBSQL')
    DB_TABLE = os.getenv('DBSQL_TABLE')

    def __init__(self, host=DB_HOST, user=DB_USER, password=DB_PASSWORD, db=DB, table=DB_TABLE):
        self.host = host
        self.db = db
        self.user = user
        self.password = password
        self.table = table
        # self.connect()

    def connect(self, db_action='fetch', query='', records=[]):

        config = {
            'user': self.DB_USER,
            'password': self.DB_PASSWORD,
            'host': self.DB_HOST,
            'database': self.DB,
            'raise_on_warnings': True
            }
        try:
            with connect(**config) as connection:
                with connection.cursor() as cursor:
                    if db_action == 'fetch':
                        return self.fetch(cursor, query)
                    elif db_action == 'execute':
                        self.execute(connection, cursor, query, records)
                    elif db_action == 'execute_many':
                        self.execute_many(connection, cursor, query, records)
        except Error as e:
            print(e)

    def fetch(self, cursor, query):
        cursor.execute(query)
        result = cursor.fetchall()
        return result

    def execute(self, connection, cursor, query, records):
        cursor.execute(query)
        connection.commit()

    def execute_many(self, connection, cursor, query, records):
        cursor.executemany(query, records)
        connection.commit()

    def all_records(self):
        query = f"SELECT * FROM {self.table}"
        records = self.connect('fetch', query)
        return records

    def find_date(self, date):
        query = f"SELECT * FROM {self.table} WHERE datetime LIKE '{date}%'"
        records = self.connect('fetch', query)
        return records

    def is_in_db(self, item):
        for record in self.all_records():
            if record[1] == string_to_datetime(item['datetime']):
                if record[5] == item['entity']:
                    if record[4] == float(item['amount']):
                        return True
        return False

    def insert(self, item, force=False):
        if force:
            print(f"[MySQL] Added a bunch of entries")
            self.execute_insert(item)
        elif not self.is_in_db(item):
            print(f"[MySQL] Entry for {item['datetime']} [{item['type']}] - {item['entity'].upper()}: {item['amount']} added")
            self.execute_insert(item)
        else:
            print("[MySQL] Entry is already in DB")

    def execute_insert(self, items):
        records = []
        query = f"""
        INSERT INTO {self.table}
        (datetime, account, type, amount, entity)
        VALUES ( %s, %s, %s, %s, %s )"""

        if type(items) is list:
            for entry in items:
                entry[0] = string_to_datetime(entry[0])
                entry[3] = float(entry[3])
                records.append(entry)
                print(entry)
        else:
            items["datetime"] = string_to_datetime(items["datetime"])

            records = [
                items["datetime"],
                items["account"],
                items["type"],
                items["amount"],
                items["entity"]
                ],

        self.connect('execute_many', query, records)
