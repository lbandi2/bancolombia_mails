from bs4 import BeautifulSoup
import re
from utils import regexp_in_list, convert_money, operation_types
from db_sql import DB
from category import Categories


class MailOperation:
    def __init__(self, email_body, date):
        self.email_body = email_body
        self.date = date
        self.soup = BeautifulSoup(self.email_body, "html.parser").find_all('td')
        self.operation_string = self.get_op_string()
        self.db_table = self.define_db_table()
        self.all_cards = DB(db_table='card').all_cards()
        self.all_accounts = DB(db_table='account').all_accounts()
        self.operation = self.generate_output(self.date)
                
    def define_db_table(self):
        db_table = 'account'
        if self.op_type() == 'expense':
            if isinstance(self.op_account(), dict) and 'type' in self.op_account():
                if self.op_account()['type'] == 'credit':
                    db_table = 'card'
        return db_table

    def is_valid(self):
        if self.op_type() is None:
            print("Operation type could not be found using known phrases as reference")
        else:
            if self.op_entity() is None:
                print("Operation place/person could not be found using known method as reference")
            else:
                if self.op_amount() is None:
                    print("Operation amount could not be found using phone number as reference")
                else:
                    if self.op_account() is not None:
                        return True
                    else:
                        print("Operation account/card could not be found using known account/card numbers as reference")
        print(f"Skipping mail from {self.date} because it's not a recognized operation")
        print(f"Debug data: \ndb_table: {self.db_table}\nop_type: {self.op_type()}\nop_account: {self.op_account()}\nop_amount: {self.op_amount()}\nop_entity: {self.op_entity()}")
        return False

    def get_op_string(self):
        for item in self.soup:
            for op_k, op_v in operation_types().items():
                for value in op_v:
                    if value.lower() in item.text.lower():
                        return value.lower()

    def op_type(self):
        for item in self.soup:
            for op_k, op_v in operation_types().items():
                for value in op_v:
                    if value.lower() in item.text.lower():
                        return op_k
        return None

    def op_amount(self):
        money = None
        for item in self.soup:
            money = re.search("(?:[$])(?:\d+(?:[.,]?\d*)*)", item.text)
            if money:
                return money.group()
        else:
            return None

    # def op_account(self):
    #     accounts = DB(db_table='account').all_accounts()
    #     cards = DB(db_table='card').all_cards()
    #     for element in self.soup:
    #         for account in accounts:
    #             if f"*{account['number']}" in element.text:
    #                 return account
    #         for card in cards:
    #             if f"*{card['number']}" in element.text:
    #                 return card
    #     else:
    #         return None

    def op_account(self):
        accounts = DB(db_table='account')
        cards = DB(db_table='card')
        for element in self.soup:
            for account in accounts.all_accounts():
                if f"*{account['number']}" in element.text:
                    return account
            for card in cards.all_cards():
                if f"*{card['number']}" in element.text:
                    if card['type'] == 'debit':
                        account = accounts.account_from_id(card['account_id'])
                        return account
                    else:
                        return card
        else:
            return None


    def op_entity_bank_payment(self):
        for item in self.soup:
            for card in self.all_cards:
                if re.search(f"\*{card['number']}", item.text.lower()):
                    if 'deuda en pesos' in item.text.lower() and ', abono que' in item.text.lower():
                        text_wo_money = item.text.lower().split('deuda en pesos.')[1].split(', abono que')[0]
                        return text_wo_money.strip().upper()
                    elif 'deuda en dólares' in item.text.lower() and ', abono que' in item.text.lower():
                        text_wo_money = item.text.lower().split('deuda en dólares.')[1].split(', abono que')[0]
                        return text_wo_money.strip().upper()
        return None

    def op_entity_manual_payment(self):
        for item in self.soup:
            for card in self.all_cards:
                if re.search(f"\*{card['number']}", item.text.lower()):
                    if 'realizo abono a su' in item.text.lower():
                        text_wo_money = item.text.lower().split('realizo abono a su ')[1].split(f' por $')[0]
                        return text_wo_money.strip().upper()
                    elif 'desde cta' in item.text.lower():
                        text_wo_money = item.text.lower().split('desde cta ')[1].split(f' por $')[0]
                        return text_wo_money.strip().upper()
        return None

    def op_entity(self):
        entity = None

        for item in self.soup:
            if self.op_type() == 'bank payment':                                        # cobro de tarjeta
                return self.op_entity_bank_payment()

            elif re.search("0180*931987", item.text):
                if self.op_type() == 'manual payment':                                        # pago manual
                    return self.op_entity_manual_payment()
                elif self.op_type() == 'transfer':                                          # transferencia
                    text_wo_money = item.text.lower().split(self.op_amount())[1]
                    date = re.search("\d{2}/\d{2}/\d{4}", text_wo_money).group()
                    for account in self.all_accounts:
                        new_key = account['number']
                        if new_key in text_wo_money:
                            entity = text_wo_money.split(new_key)[1].split(date)[0].replace(' a ', '').replace('.', '').rstrip(' ')
                            break
                elif self.op_type() == 'extraction':                                        # extracciones
                    text_w_money = item.text.lower().split(self.operation_string)[1]
                    if re.search("\d{2}\:\d{2}", text_w_money):
                        text_w_timedate = text_w_money.split(f"{self.op_amount()} en")[1]
                        time = re.search("\d{2}\:\d{2}", text_w_timedate).group()
                        entity = text_w_timedate.split(time)[0].replace('. hora', '').strip()
                elif self.op_type() == 'expense':
                    text_w_money = item.text.lower().split(self.operation_string)[1]
                    if re.search("\d{2}\:\d{2}", text_w_money):
                        if 'desde cta' in text_w_money:
                            text_w_timedate = text_w_money.split(self.op_amount())[1]         # pagos (a veces son debitos automaticos)
                            entity = text_w_timedate.replace(" a ", "").split(" desde cta")[0]
                        elif 'desde producto' in text_w_money:
                            text_w_timedate = text_w_money.split(self.op_amount())[1]         # pagos (a veces son debitos automaticos)
                            entity = text_w_timedate.replace(" a ", "").split(" desde producto")[0]
                        else:
                            text_w_timedate = text_w_money.split(f"{self.op_amount()} en")[1]         # compras habituales
                            time = re.search("\d{2}\:\d{2}", text_w_timedate).group()
                            entity = text_w_timedate.split(time)[0].strip().rstrip('.')
                elif self.op_type() == 'recurring bill':
                    text_w_money = item.text.lower().split(self.operation_string)[1]
                    if re.search("\d{2}/\d{2}/\d{4}", text_w_money):               # debito automatico (no time, only date)
                        text_no_extras = text_w_money.split(self.op_amount())[0].strip('por ')
                        text_no_extras = text_no_extras.split(' (')[0]
                        entity = text_no_extras.replace('  ', ' ')
                else:
                    print("Could not find op_type to grab entity")
            if entity is not None:
                entity = entity.title()
        return entity

    # def find_category_in_db(self, entity, db):
    #     if get_category(entity) is not None:
    #         category = get_category(entity)
    #         db_categs = db
    #         for record in db_categs:
    #             if category == record['name']:
    #                 return record['id']
    #     else:
    #         return None

    def generate_output(self, date):
        if self.is_valid():
            operation = {}
            operation['db_table'] = self.define_db_table()
            operation['datetime'] = date
            operation['type'] = self.op_type()
            operation['account'] = self.op_account()['id']
            if self.op_type() == 'bank payment':
                operation['account'] = self.op_account()['account_id']  # gets bank account id
            operation['amount'] = convert_money(self.op_amount())
            operation['entity'] = self.op_entity()
            # if get_category(self.op_entity()) is not None:
            #     operation['category'] = get_category(self.op_entity())
            # else:
            #     operation['category'] = ''
            db_categ = DB(db_table='categories').all_records()
            # db_categ = Categories().get_all()
            operation['category'] = Categories().get_category(self.op_entity())
            # operation['category'] = find_category_in_db(self.op_entity(), db=db_categ)
            operation['dues'] = 1
            return operation

