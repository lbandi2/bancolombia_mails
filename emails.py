from base64 import urlsafe_b64decode
from utils import convert_date

class Email:
    def __init__(self, headers, parts, has_parts, labels):
        self.has_parts = has_parts
        self.headers = headers
        self.parts = parts
        self.labels = labels

        self.is_unread = self.get_unread_status()
        self.sender = ''
        self.to = ''
        self.subject = ''
        self.date = ''
        self.time = ''
        self.is_html = False
        self.body = ''
        self.has_attachment = False
        self.attachment = ''
        self.read_payload()

    def get_unread_status(self):
        if 'UNREAD' in self.labels:
            return True
        return False

    def parse_parts(self, parts):
        """
        Utility function that parses the content of an email partition
        """
        if parts:
            for part in parts:
                filename = part.get("filename")
                mimeType = part.get("mimeType")
                body = part.get("body")
                data = body.get("data")
                # file_size = body.get("size")
                part_headers = part.get("headers")
                if part.get("parts"):
                    # recursively call this function when we see that a part
                    # has parts inside
                    self.parse_parts(part.get("parts"))
                if mimeType == "text/plain":
                    if data:
                        text = urlsafe_b64decode(data).decode()
                        self.body = text
                elif mimeType == "text/html":
                    self.is_html = True
                    self.body = urlsafe_b64decode(data)
                else:
                    # attachment other than a plain text or HTML
                    for part_header in part_headers:
                        part_header_name = part_header.get("name")
                        part_header_value = part_header.get("value")
                        if part_header_name == "Content-Disposition":
                            if "attachment" in part_header_value:
                                self.has_attachment = True
                                self.attachment = filename

    def read_payload(self):
        if self.headers:
            for header in self.headers:
                name = header.get("name")
                value = header.get("value")
                if name.lower() == 'from':
                    self.sender = value
                if name.lower() == "to":
                    self.to = value.lower()
                if name.lower() == "subject":
                    self.subject = value
                if name.lower() == "date":
                    date = convert_date(value)
                    self.date = date
                if name.lower() == "content-type":
                    if "text/html" in value:
                        self.is_html = True
        if self.has_parts:
            self.parse_parts(self.parts)
        else:
            self.body = urlsafe_b64decode(self.parts)
