from utils import make_dir
from search import Search

EMAIL_TITLE = "Servicio de Alertas y Notificaciones"

def main():
    make_dir("creds")
    Search(EMAIL_TITLE)

if __name__ == '__main__':
    main()
