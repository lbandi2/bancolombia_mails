from bs4 import BeautifulSoup
import re
from utils import regexp_in_list, convert_money, get_category
from dotenv import dotenv_values

ACCOUNTS = dotenv_values('accounts.env')

class MailOperation:
    operations = {
        "informa pago Factura Programada": "expense",
        "informa Compra por": "expense",
        "informa Retiro por": "extraction",
        "informa que": "income"
    }

    def __init__(self, email_body, date):
        self.email_body = email_body
        self.date = date
        self.soup = BeautifulSoup(self.email_body, "html.parser")
        self.operation = self.generate_output(self.date)

    def is_valid(self):
        if self.op_type() is not None:
            if self.op_entity() is not None:
                if self.op_account() is not None:
                    if self.op_amount() is not None:
                        return True
        print(f"Skipping mail from {self.date} because it's not an operation")
        return False

    def generate_output(self, date):
        if self.is_valid():
            operation = {}
            operation['datetime'] = date
            operation['account'] = self.op_account()
            operation['type'] = self.op_type()
            operation['amount'] = convert_money(self.op_amount())
            operation['entity'] = self.op_entity()
            if get_category(self.op_entity()) is not None:
                operation['category'] = get_category(self.op_entity())
            else:
                operation['category'] = 'unknown'
            return operation

    def op_entity(self):
        tables = self.soup.find_all('td')
        entity = None
        operation_string = regexp_in_list(self.operations, tables, index=0).lower()
        op_type = regexp_in_list(self.operations, tables)
        money = self.op_amount()
        for item in tables:
            if re.search("0180*931987", item.text):
                if op_type == 'income':                                              # pago de tarjeta
                    text_w_money = item.text.lower().split(operation_string)[1]
                    string = text_w_money.split('realizo abono')[0].strip()
                elif op_type == 'extraction':
                    text_w_money = item.text.lower().split(operation_string)[1]
                    if re.search("\d{2}\:\d{2}", text_w_money):                      # extracciones
                        text_w_timedate = text_w_money.split(money)[1]
                        time = re.search("\d{2}\:\d{2}", text_w_timedate).group()
                        string = text_w_timedate.split(time)[0].strip('en ').lstrip().replace('. hora', '')
                elif op_type == 'expense':
                    text_w_money = item.text.lower().split(operation_string)[1]
                    if re.search("\d{2}\:\d{2}", text_w_money):                      # compras habituales
                        text_w_timedate = text_w_money.split(money)[1]
                        time = re.search("\d{2}\:\d{2}", text_w_timedate).group()
                        string = text_w_timedate.split(time)[0].strip('en ').lstrip()
                    elif re.search("\d{2}/\d{2}/\d{4}", text_w_money):               # debito automatico (no time, only date)
                        text_no_extras = text_w_money.split(money)[0].strip('por ')
                        text_no_extras = text_no_extras.split(' (')[0]
                        string = text_no_extras
                else:
                    raise ValueError("Could not find time nor date to grab phrase")
                entity = string.title()
        if entity is None:
            print("Operation place/person could not be found using known method as reference")
            return None
            # raise ValueError("Operation place/person could not be found using known method as reference")
        else:
            return entity

    def op_account(self):
        tables = self.soup.find_all('td')
        # item = regexp_in_list(self.accounts, tables)
        item = regexp_in_list(ACCOUNTS, tables)
        if item is None:
            print("Operation account could not be found using known card numbers as reference")
            return None
            # raise ValueError("Operation account could not be found using known card numbers as reference")
        else:
            return item

    def op_type(self):
        tables = self.soup.find_all('td')
        item = regexp_in_list(self.operations, tables)
        if item is None:
            print("Operation type could not be found using known phrases as reference")
            return None
            # raise ValueError("Operation type could not be found using known phrases as reference")
        else:
            return item

    def op_amount(self):
        tables = self.soup.find_all('td')
        money = None
        for item in tables:
            if re.search("0180*931987", item.text):
                try:
                    money = re.search("(?:[$])(?:\d+(?:[.,]?\d*)*)", item.text).group()
                except AttributeError:
                    return None
        if money is None:
            print(f"Operation amount {money} could not be found using phone number as reference")
            return None
            # raise ValueError(f"Operation amount {money} could not be found using phone number as reference")
        else:
            return money    
