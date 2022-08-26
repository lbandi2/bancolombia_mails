from mysql.connector import connect, Error
import os
from dotenv import load_dotenv

from utils import string_to_datetime, get_category

load_dotenv()

class DB:
    DB_HOST = os.getenv('DBSQL_HOST')
    DB_USER = os.getenv('DBSQL_USER')
    DB_PASSWORD = os.getenv('DBSQL_PASSWORD')
    DB = os.getenv('DBSQL')
    DB_TABLE_OP_ACCOUNT = os.getenv('DBSQL_TABLE_OP_ACCOUNT')
    DB_TABLE_OP_CARD = os.getenv('DBSQL_TABLE_OP_CARD')
    DB_TABLE_CARDS = os.getenv('DBSQL_TABLE_CARDS')
    DB_TABLE_ACCOUNTS = os.getenv('DBSQL_TABLE_ACCOUNTS')

    def __init__(self, host=DB_HOST, user=DB_USER, password=DB_PASSWORD, db=DB, db_table='card'):
        self.host = host
        self.db = db
        self.user = user
        self.password = password
        if db_table == 'card':
            self.db_table = self.DB_TABLE_OP_CARD
        else:
            self.db_table = self.DB_TABLE_OP_ACCOUNT
        # self.connect()

    def connect(self, db_action='fetch', query='', records=[], dictionary=True):

        config = {
            'user': self.DB_USER,
            'password': self.DB_PASSWORD,
            'host': self.DB_HOST,
            'database': self.DB,
            'raise_on_warnings': True
            }
        try:
            with connect(**config) as connection:
                with connection.cursor(dictionary=dictionary) as cursor:
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

    def account_from_id(self, account_id):
        query = f"SELECT * FROM {self.DB_TABLE_ACCOUNTS} WHERE id='{account_id}'"
        record = self.connect('fetch', query)
        return record[0]

    def all_cards(self, select_field='*'):
        query = f"SELECT {select_field} FROM {self.DB_TABLE_CARDS}"
        if select_field == '*':
            records = self.connect('fetch', query)
        else:
            records = sum(self.connect('fetch', query, dictionary=False), ())
        return records

    def all_accounts(self):
        query = f"SELECT * FROM {self.DB_TABLE_ACCOUNTS} WHERE is_corporate != 1;"
        records = self.connect('fetch', query)
        return records

    def all_records(self):
        query = f"SELECT * FROM {self.db_table}"
        records = self.connect('fetch', query)
        return records

    def update_category(self, item, category):
        query = f"UPDATE {self.db_table} SET category = '{category}' WHERE id = {item['id']}"
        self.connect('execute', query)

    def fix_categories(self, force=False):
        for item in self.all_records():
            category = None
            if item['type'] == 'extraction' and (item['category'] is None or item['category'] == 'unknown'): #TODO: maybe only check type?
                category = 'extraccion'
                # print(f"[MySQL] Updating category for entry {item[1]} {item[5].upper()}: {category}")
                # self.update_category(item, category)
            elif item[6] is None or item[6] == 'unknown' or force:
                category = get_category(item[5])
            if category is not None:
                print(f"[MySQL] Updating category for entry {item['date']} {item['entity'].upper()}: {category}")
                self.update_category(item, category)

    def find_date(self, date):
        query = f"SELECT * FROM {self.db_table} WHERE datetime LIKE '{date}%'"
        records = self.connect('fetch', query)
        return records

    def is_in_db(self, item):
        for record in self.all_records():
            if record['date'] == string_to_datetime(item['datetime']):
                if record['entity'] == item['entity']:
                    if record['amount'] == float(item['amount']):
                        return True
        return False

    def insert(self, item, force=False):
        if force:
            print(f"[MySQL] Added a bunch of entries")
            self.execute_insert(item)
        elif not self.is_in_db(item):
            print(f"[MySQL] Entry for {self.db_table} {item['datetime']} [{item['type']}] - {item['entity'].upper()}: {item['amount']} added")
            self.execute_insert(item)
        else:
            print("[MySQL] Entry is already in DB")

    def execute_insert(self, items):
        records = []
        account = 'account_id'
        if 'card' in self.db_table.lower():
            account = 'card_id'
        query = f"""
        INSERT INTO {self.db_table}
        (date, type, amount, entity, {account}, category, dues)
        VALUES ( %s, %s, %s, %s, %s, %s, %s )"""

        if type(items) is list:
            for entry in items:
                entry['datetime'] = string_to_datetime(entry['datetime'])
                entry['amount'] = float(entry['amount'])
                records.append(entry)
                print(entry)
        else:
            items["datetime"] = string_to_datetime(items["datetime"])

            records = [
                items["datetime"],
                items["type"],
                items["amount"],
                items["entity"],
                items["account"],
                items["category"],
                items["dues"]
                ],

        self.connect('execute_many', query, records)
