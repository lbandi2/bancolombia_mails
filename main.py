from utils import make_dir
from search import SearchOperations
import os
from dotenv import load_dotenv

load_dotenv()

OP_TITLE = "Servicio de Alertas y Notificaciones"
BALANCE_TITLE = "Adjunto encontrarás los extractos de tus Tarjetas de Crédito"
PDF_PASSWORD = os.getenv('PDF_PASSWORD_SERGIO')

def main():
    make_dir("creds")
    search = SearchOperations(OP_TITLE)


if __name__ == '__main__':
    main()
