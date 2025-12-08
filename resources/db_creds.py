import os
from dotenv import load_dotenv

load_dotenv()

class DbCreds:
    DBNAME = os.getenv('DBNAME')
    USER = os.getenv('USER')
    PASSWORD = os.getenv('PASSWORD')
    HOST = os.getenv('HOST')
    PORT = os.getenv('PORT')