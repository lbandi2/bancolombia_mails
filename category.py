import os
from dotenv import load_dotenv

from db_sql import DB

load_dotenv()

class Keyword(DB):
    def __init__(self, dict_item):
        self.id = dict_item.get('id')
        self.name = dict_item.get('name')
        self.category_id = dict_item.get('category_id')

    def __repr__(self):
        return f"[{self.id}] {self.name}"


class Keywords(DB):
    def __init__(self, cat_id):
        self.db_table = os.getenv('DBSQL_TABLE_CATEGORIES_KEYWORDS')
        self.cat_id = cat_id

    def all_records(self):
        query = f"SELECT * FROM {self.db_table} WHERE category_id={self.cat_id}"
        records = self.connect('fetch', query)
        return records

    def get_keywords(self):
        return [Keyword(item) for item in self.all_records()]


class Category(DB):
    def __init__(self, id):
        self.db_table = os.getenv('DBSQL_TABLE_OP_CATEGORIES')
        self.id = id
        self.name = self.get_name()
        self.keywords = Keywords(cat_id=self.id).get_keywords()

    def get_name(self):
        lst = [item.get('name') for item in self.all_records() if item.get('id') == self.id]
        if len(lst) == 1:
            return lst[0]
        print(f"[DB] Could not find a category with id {self.id}")
        return None


class Categories(DB):
    def __init__(self):
        self.db_table = os.getenv('DBSQL_TABLE_OP_CATEGORIES')

    def get_all(self):
        return [Category(id=item.get('id')) for item in self.all_records()]

    def get_category(self, string):
        string = str(string)
        for category in self.get_all():
            for keyword in category.keywords:
                if keyword.name in string.lower():
                    return category.id
        return None
