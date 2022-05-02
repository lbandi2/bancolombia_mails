from gmail_setup import gmail_authenticate
from emails import Email
from operation import Operation
from db import DB

class Search:
    def __init__(self, query):
        self.query = query
        self.service = gmail_authenticate()
        self.emails = []
        self.message_ids = self.search_messages(query)
        self.parse_emails()
        self.operations = self.get_operations()
        self.push_to_db()
        self.expense_total = self.get_expense_total()
        self.income_total = self.get_income_total()
        self.balance = self.get_balance()

    def get_balance(self):
        return self.expense_total - self.income_total

    def get_expense_total(self):
        total = 0
        for item in self.operations:
            if item['type'] == 'expense' and item['account'] == 'cc sergio':
                total += item['amount']
        return float(total)

    def get_income_total(self):
        total = 0
        for item in self.operations:
            if item['type'] == 'income' and item['account'] == 'cc sergio':
                total += item['amount']
        return float(total)

    def push_to_db(self):
        if self.operations != []:
            db = DB()
            for operation in self.operations:
                try:
                    db.insert(operation)
                except:
                    print(f"Error inserting: {operation}")

    def get_operations(self):
        operations = []
        for item in self.emails:
            if item.is_unread:
                date = item.date.strftime("%Y-%m-%d")
                time = item.date.strftime("%H:%M")
                operation = Operation(item.body, date, time)
                if operation.is_valid():
                    operations.append(operation.operation)
        return operations

    def parse_emails(self):
        for index, msg in enumerate(self.message_ids):
            message_content = self.fetch_message(msg)[0]
            message_labels = self.fetch_message(msg)[1]
            message_payload = self.parse_payload(message_content)
            message_headers = message_payload[0]
            has_parts = bool(message_payload[1])
            message_parts = message_payload[2]

            email = Email(message_headers, message_parts, has_parts, message_labels)
            if email.is_unread:
                print(f"Fetched email from {email.date.strftime('%Y-%m-%d')}")
            if not email.is_unread: # stop processing when the first read mail is found
                if len(self.emails) == 0:
                    print("No new mails to process.")
                else:
                    print(f"Found read email from {email.date.strftime('%Y-%m-%d')}, aborting email fetch.")
                break
            self.emails.append(email)
            self.mark_as_read(msg)

    def mark_as_read(self, msg):
        return self.service.users().messages().modify(
            userId='me', id=msg['id'],
            body={'removeLabelIds': ['UNREAD']}).execute()

    def search_messages(self, query):
        result = self.service.users().messages().list(maxResults=300, userId='me', q=query).execute()
        messages = []
        if 'messages' in result:
            messages.extend(result['messages'])
        return messages

    def fetch_message(self, message):
        msg = self.service.users().messages().get(userId='me', id=message['id'], format='full').execute()
        payload = msg['payload']
        labels = msg['labelIds']
        return payload, labels

    def has_parts(self, payload):
        if 'parts' in payload:
            return True
        return False

    def parse_payload(self, payload):
        headers = payload.get('headers')
        if self.has_parts(payload):
            parts = payload.get('parts')
            has_parts = True
        else:
            parts = payload.get('body').get('data')
            has_parts = False
        return headers, has_parts, parts


