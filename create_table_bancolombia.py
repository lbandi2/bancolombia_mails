from mysql.connector import connect, Error
import os
from dotenv import load_dotenv

load_dotenv()

DB_HOST = os.getenv('DBSQL_HOST')
DB_USER = os.getenv('DBSQL_USER')
DB_PASSWORD = os.getenv('DBSQL_PASSWORD')
DB_ACCOUNTS_TABLE = os.getenv('DBSQL_ACCOUNTS_TABLE')
DB_CARDS_TABLE = os.getenv('DBSQL_CARDS_TABLE')
DB = os.getenv('DBSQL')

try:
    with connect(
        host=DB_HOST,
        user=DB_USER,
        password=DB_PASSWORD,
        database=DB,
    ) as connection:

        # create_table_query = """
        # CREATE TABLE operations(
        #     id INT AUTO_INCREMENT PRIMARY KEY,
        #     datetime DATETIME,
        #     account VARCHAR(50),
        #     type VARCHAR(50),
        #     amount FLOAT(10,2),
        #     entity VARCHAR(50)
        # )
        # """

        # create_table_query = """
        # CREATE TABLE operations(
        #     id INT AUTO_INCREMENT PRIMARY KEY,
        #     datetime DATETIME,
        #     bank VARCHAR(50),
        #     card_brand VARCHAR(50),
        #     card_type VARCHAR(50),
        #     card_owner VARCHAR(50),
        #     op_type VARCHAR(50),
        #     op_amount FLOAT(10,2),
        #     op_entity VARCHAR(50)
        # )

        # """
        # create_table_query = f"""
        # CREATE TABLE {DB_ACCOUNTS_TABLE}(
        #     account_id INT AUTO_INCREMENT PRIMARY KEY,
        #     bank VARCHAR(50),
        #     owner VARCHAR(50),
        #     number VARCHAR(50),
        #     since DATETIME,
        #     is_active TINYINT(1)
        # )

        create_table_query = f"""
        CREATE TABLE {DB_CARDS_TABLE}(
            id INT AUTO_INCREMENT PRIMARY KEY,
            account_id INT, CONSTRAINT fk_account FOREIGN KEY (account_id) REFERENCES accounts(account_id),
            card_brand VARCHAR(50),
            card_type VARCHAR(50),
            card_number VARCHAR(50),
            card_owner VARCHAR(50),
            is_extension TINYINT(1),
            is_active TINYINT(1)
        )
        """

        with connection.cursor() as cursor:
            cursor.execute(create_table_query)
            connection.commit()

        print('Table created.\n')
    

except Error as e:
    print(e)

