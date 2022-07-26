from mysql.connector import connect, Error
import os
from dotenv import load_dotenv

load_dotenv()

DB_HOST = os.getenv('DBSQL_HOST')
DB_USER = os.getenv('DBSQL_USER')
DB_PASSWORD = os.getenv('DBSQL_PASSWORD')
DB = os.getenv('DBSQL')

try:
    with connect(
        host=DB_HOST,
        user=DB_USER,
        password=DB_PASSWORD,
        database=DB,
    ) as connection:

        create_table_query = """
        CREATE TABLE operations(
            id INT AUTO_INCREMENT PRIMARY KEY,
            datetime DATETIME,
            account VARCHAR(50),
            type VARCHAR(50),
            amount FLOAT(10,2),
            entity VARCHAR(50)
        )
        """
        with connection.cursor() as cursor:
            cursor.execute(create_table_query)
            connection.commit()

        print('Table created.\n')
    

except Error as e:
    print(e)

