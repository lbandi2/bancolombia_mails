from utils import make_dir, last_pdf
from search import Search, SearchOperations
from pdf import PDF
from compare import Comparison
from secrets import json_secret

OP_TITLE = "Servicio de Alertas y Notificaciones"
BALANCE_TITLE = "Adjunto encontrarás los extractos de tus Tarjetas de Crédito"
PDF_PASSWORD = json_secret('pdf', 'password')

def main():
    make_dir("creds")
    # pdf = Search(BALANCE_TITLE, stop_if_unread=True, ignore_subject=['Fwd:'], force_get_attachment=True)
    # if len(pdf.emails) > 0:
    #     if 'filename' in pdf.emails[0].attachment:
    #         pdf_file = pdf.emails[0].attachment['filename']
    # else:
    #     pdf_file = last_pdf()

    search = SearchOperations(OP_TITLE)
    # compare = Comparison(search, PDF(pdf_file, PDF_PASSWORD, '2022-04-30'))
    # compare

    # records = compare.fetch_mail_records()
    # print(records)
    # print(len(records))


if __name__ == '__main__':
    main()
