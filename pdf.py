import pdfplumber
import re
from datetime import datetime
import math
from secrets import json_secret
from utils import is_num, get_rubro

password = json_secret('pdf', 'password')
# file = 'Extracto_167236926_202204_TARJETA_VISA_9299.pdf'
# file = 'Extracto_61620622_202202_TARJETA_VISA_9299.pdf'
# file = 'Extracto_84394575_202203_TARJETA_VISA_9299.pdf'
# TODAY = datetime.now().date().strftime('%Y-%m-%d')

class PDF:
    def __init__(self, file, password, date_received):
        self.date_received = date_received
        self.file = file
        self.password = password
        self.pages = []
        self.open_file()
        self.desde = self.pages[0].period[0]
        self.hasta = self.pages[0].period[1]
        self.num_pages = len(self.pages)
        self.operations = self.get_operations()
        self.pago_minimo = self.get_pago_minimo()
        self.pago_total = self.get_pago_total()
        self.pendiente_en_cuotas = self.get_pendiente_en_cuotas()

    def open_file(self):
        with pdfplumber.open(f'{self.file}', password=self.password) as pdf:
            for item in pdf.pages:
                page = PDFPage(item.extract_text())
                self.pages.append(page)

    def get_operations(self):
        ops = []
        for page in self.pages:
            for op in page.operations:
                ops.append(op)
        return ops

    def get_pago_minimo(self):
        total = 0
        for op in self.operations:
            if op['tipo'] == 'expense':
                total += op['cargos_y_abonos']
        return math.ceil(total)
            
    def get_pago_total(self):
        total = 0
        for op in self.operations:
            if op['tipo'] == 'expense':
                total += op['cargos_y_abonos'] + op['saldo_a_diferir']
        return math.ceil(total)

    def get_pendiente_en_cuotas(self):
        total = 0
        for op in self.operations:
            if op['tipo'] == 'expense':
                total += op['saldo_a_diferir']
        return math.ceil(total)


class PDFPage:
    def __init__(self, content):
        self.content = content
        self.cargos_prev = []
        self.period = self.find_period()
        self.operations = self.parse_page()
        self.num_operations = len(self.operations)  # revisar para que solo queden las compras

    def find_period(self):
        for index, item in enumerate(self.content.split('\n')):
            exp = re.findall("\d{2}/\d{2}/\d{4}", item)
            if len(exp) == 2:
                desde = exp[0]
                hasta = exp[1]
                desde_date = datetime.strptime(desde, '%d/%m/%Y').isoformat()
                hasta_date = datetime.strptime(hasta, '%d/%m/%Y').isoformat()
                # desde_date = datetime.strptime(desde, '%d/%m/%Y').strftime('%Y-%m-%d')
                # hasta_date = datetime.strptime(hasta, '%d/%m/%Y').strftime('%Y-%m-%d')
                return [desde_date, hasta_date]
        else:
            raise ValueError("Couldn't find billable period, missing 'desde' and 'hasta'")

    def fix_authorization(self, line):
        if 'INTERESES CORRIENTES' in line or 'INTERESES MORA' in line:
            line = '000000 ' + line
        return line

    def find_operations(self):
        ops = []
        exp = re.compile(r'^\d{6} \d{2}/\d{2}/\d{4}')
        for line in self.content.split('\n'):
            line = self.fix_authorization(line)
            if exp.match(line):
                operation = PDFOperation(line)
                ops.append(operation.values)
        return ops

    def remove_operation(self, lst, op):
        for index, item in enumerate(lst):
            if item['autorizacion'] == op['autorizacion']:
                if item['valor_original'] == op['valor_original']:
                    lst.pop(index)
        return lst

    def check_duplicates(self, operations):
        cargos_prev = []
        lst = []
        for op in operations:
            if op['autorizacion'] == '000000':
                lst.append(op)
            elif op['autorizacion'] not in cargos_prev:
                cargos_prev.append(op['autorizacion'])
                lst.append(op)
            elif op['autorizacion'] in cargos_prev:   # check if duplicate, then remove previous
                self.remove_operation(lst, op)
        return lst

    def parse_page(self):
        all_operations = self.find_operations()
        operations = self.check_duplicates(all_operations)
        return operations

class PDFOperation:
    def __init__(self, line):
        self.original_line = line
        self.line = line
        self.values = {}
        self.get_values()

    def get_values(self):
        self.values['autorizacion'] = self.get_autorizacion()
        self.values['fecha'] = self.get_fecha()
        self.values['cuotas'] = self.get_cuotas()
        self.values['nombre'] = self.get_nombre()
        self.values['tipo'] = self.get_tipo()
        self.values['saldo_a_diferir'] = self.get_last_value()
        self.values['cargos_y_abonos'] = self.get_last_value()
        self.values['tasa_ea_facturada'] = 0.0
        self.values['tasa_pactada'] = 0.0
        if len(self.line.split(' ')) >= 3:
            self.values['tasa_ea_facturada'] = self.get_last_value(type='percentage')
            self.values['tasa_pactada'] = self.get_last_value(type='percentage')
        self.values['valor_original'] = self.get_last_value()

    def get_autorizacion(self):
        aut = self.line.split(" ")[0]
        self.line = self.line.replace(f'{aut} ', '')
        return aut

    def get_fecha(self):
        exp = re.compile(r'\d{2}/\d{2}/\d{4}')
        for item in self.line.split(" "):
            if exp.match(item):
                self.line = self.line.replace(f'{item} ', '')
                # fecha = datetime.strptime(item, "%d/%m/%Y").strftime('%Y-%m-%d')
                fecha = datetime.strptime(item, "%d/%m/%Y").isoformat()
                return fecha

    def get_nombre(self):
        nombre = ''
        for item in self.line.split(" "):
            if not is_num(item):
                nombre += f"{item} "
        else:
            self.line = self.line.replace(f'{nombre}', '')
            return nombre.strip()

    def get_tipo(self):
        num = len(self.line.split(' '))
        if '-' in self.line.split(' ')[-2]:
            return 'income'
        else:
            return 'expense'
    
    def get_cuotas(self):
        exp = re.compile(r"(\d{1,2})/(\d{1,2})$")
        for item in self.line.split(" "):
            if exp.match(item):
                self.line = self.line.replace(f' {item}', '')
                return item
    
    def get_last_value(self, type='float'):
        if type == 'float':
            value = self.line.split(' ')[-1].replace('00-', '00').replace(',', '')
            self.line = " ".join(self.line.split(' ')[:-1])
            return float(value)
        elif type == 'percentage':
            value = self.line.split(' ')[-1].replace(',', '.')
            self.line = " ".join(self.line.split(' ')[:-1])
            return float(value)


# a = PDF(file, password=password)

# with pdfplumber.open(r'./data/Extracto_167236926_202204_TARJETA_VISA_9299.pdf' , password = '1196864') as pdf:
#     first_page = pdf.pages[0]
#     second_page = pdf.pages[1]
#     text_first = first_page.extract_text()
#     text_second = second_page.extract_text()
#     # text = text.split("Período Facturado")[1].split("Disponible Total")[0]
#     # desde = text.split("Desde:")[1].split("Hasta")[0].strip()
#     # hasta = text.split("Hasta:")[1].strip()
#     # print(desde, hasta)
#     exp = re.compile(r'^\d{6} \d{2}/\d{2}/\d{4}')
#     # print(text)
#     for item in text_first.split('\n'):
#         if exp.match(item) or 'INTERESES CORRIENTES' in item:
#             print(item)
#     for item in text_second.split('\n'):
#         if exp.match(item):
#             print(item)

#     print(len(pdf.pages))
