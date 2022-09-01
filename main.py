from utils import make_dir
from search import SearchOperations
import os
from dotenv import load_dotenv

load_dotenv()

GMAIL_LABEL = os.getenv('GMAIL_LABEL')

def main():
    make_dir("creds")
    search = SearchOperations(GMAIL_LABEL)

# 6.5 min to download ~ 400 emails
# 2 min to process afterwards
# total: 8.5s min

if __name__ == '__main__':
    main()
