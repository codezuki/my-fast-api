import os
import pyodbc
from dotenv import load_dotenv

load_dotenv()  # Load environment variables from .env file

def get_db_connection():

    driver = os.getenv("DB_DRIVER")
    server = os.getenv("DB_SERVER")
    database = os.getenv("DB_DATABASE")
    username = os.getenv("DB_USERNAME")
    password = os.getenv("DB_PASSWORD")
    trusted_connection = os.getenv("DB_TRUSTED_CONNECTION")


    connection_string = f"DRIVER={driver};SERVER={server};DATABASE={database};UID={username};PWD={password};Trusted_Connection={trusted_connection}"    

    return pyodbc.connect(connection_string)

