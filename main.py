from utils import make_dir
from search import SearchOperations
import os
from dotenv import load_dotenv

load_dotenv()

# OP_TITLE = "Servicio de Alertas y Notificaciones"
# BALANCE_TITLE = "Adjunto encontrarás los extractos de tus Tarjetas de Crédito"
GMAIL_LABEL = os.getenv('GMAIL_LABEL')

# PDF_PASSWORD = os.getenv('PDF_PASSWORD_SERGIO')

def main():
    make_dir("creds")
    search = SearchOperations(GMAIL_LABEL)

# 5 min to download ~ 400 emails
# 2 min to process afterwards
# total: 7 min

if __name__ == '__main__':
    main()
