from datetime import datetime
from dateutil import tz
import locale
import json
import re
import glob
import os
import csv

# from category import Categories

def dir_exist(path):
    return os.path.isdir(path)

def make_dir(path):
    if not dir_exist(path):
        try:
            os.mkdir(path)
        except OSError:
            print (f"Failed to create directory '{path}'")
        else:
            print(f"Creating folder '{path}'..")

def read_csv(file):
    with open(file, 'r') as csv_file:
        return list(csv.reader(csv_file, skipinitialspace=True))[1:]

def string_to_datetime(string):
    if type(string) is str:
        return datetime.strptime(string, '%Y-%m-%dT%H:%M:%S%z').replace(tzinfo=None)
    return string

def get_size_format(b, factor=1024, suffix="B"):
    """
    Scale bytes to its proper byte format
    e.g:
        1253656 => '1.20MB'
        1253656678 => '1.17GB'
    """
    for unit in ["", "K", "M", "G", "T", "P", "E", "Z"]:
        if b < factor:
            return f"{b:.2f}{unit}{suffix}"
        b /= factor
    return f"{b:.2f}Y{suffix}"

def utc_to_local(utc_datetime):
    return utc_datetime.astimezone(tz.tzlocal())

def convert_date(string):
    if ' (' in string:
        string = string.split(' (')[0]
    try:
        date = datetime.strptime(string, '%a, %d %b %Y %H:%M:%S %z')
        tz_date = utc_to_local(date)
    except ValueError:
        date = datetime.strptime(string, '%d %b %Y %H:%M:%S %z')
        tz_date = utc_to_local(date)
    return tz_date

# def convert_money(string):
#     op_amount = 0
#     try:
#         if re.search("\$\d*\.\d*(\.\d{2}|)", string):
#             locale.setlocale(locale.LC_ALL, 'es_CO.UTF8')
#             op_amount = locale.atof(string.strip('$'))
#             locale.setlocale(locale.LC_ALL, 'en_US.UTF8')
#         elif re.search("\$\d*\,\d*(\.\d{2}|)", string):
#             op_amount = locale.atof(string.strip('$'))
#     except ValueError:
#         print(f"Could not convert {string} to money")
#     finally:
#         return op_amount

def convert_money(string):
    op_amount = 0
    try:
        if re.search("\$\d*\.\d*(\,\d{2}|)", string) or ',00' in re.search("\$\d*(\,\d+)", string).groups():
            locale.setlocale(locale.LC_ALL, 'es_CO.UTF8')
            op_amount = locale.atof(string.strip('$'))
            locale.setlocale(locale.LC_ALL, 'en_US.UTF8')
        elif re.search("\$\d*\,\d*(\.\d{2}|)", string):
            locale.setlocale(locale.LC_ALL, 'en_US.UTF8')
            op_amount = locale.atof(string.strip('$'))
    except ValueError:
        print(f"Could not convert {string} to money")
    finally:
        return op_amount

def regexp_in_list(source, items_list, index=1):
    """Takes a source list or dictionary to compare against a list"""
    if isinstance(source, dict):
        for item in source.items():
            for match in items_list:
                if re.search(item[0], match.text, re.IGNORECASE):
                    return item[index]
    elif isinstance(source, list):
        for item in source:
            for match in items_list:
                if re.search(item, match.text, re.IGNORECASE):
                    return match
    return None

def is_num(string):
    try:
        string = string.replace(',', '').replace('.', '').replace('00-', '00')
        if string.isdigit():
            return True
    except AttributeError:
        return False
    return False

def operation_types(file="operations.json"):
    with open(file, "r") as json_file:
        content = json.load(json_file)
    return content

def find_operation(string):
    for op_k, op_v in operation_types().items():
        for value in op_v:
            if value.lower() in string.lower():
                return op_k

def last_pdf():
    list_of_files = glob.glob('./data/*.pdf') # * means all if need specific format then *.csv
    latest_file = max(list_of_files, key=os.path.getctime)
    return latest_file