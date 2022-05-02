from db import DB

class Comparison:
    def __init__(self, search_obj, pdf_obj):
        self.op_obj = search_obj
        self.pdf_obj = pdf_obj
        self.desde = self.pdf_obj.desde
        self.hasta = self.pdf_obj.hasta
        self.db = DB()
        self.mail_operations = self.fetch_mail_records()
        self.matches = []
        self.inconsistencies = []
        self.parse_operations()
        print(self.matches)

    def fetch_mail_records(self):
        records = self.db.find_dates(self.desde, self.hasta)
        return records

    def parse_operations(self):
        for record in self.mail_operations:
            for item in self.pdf_obj.operations:
                if record['account'] == 'visa sergio' and record['type'] == 'expense':
                    if record['amount'] == item['cargos_y_abonos']:
                        self.matches.append(item)
                        self.mail_operations.remove(record)
    


