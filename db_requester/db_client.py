from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from resources.db_creds import DbCreds

USERNAME = DbCreds.USER
PASSWORD = DbCreds.PASSWORD
HOST = DbCreds.HOST
PORT = DbCreds.PORT
DATABASE_NAME = DbCreds.DBNAME

#  движок для подключения к базе данных
engine = create_engine(
    f"postgresql+psycopg2://{USERNAME}:{PASSWORD}@{HOST}:{PORT}/{DATABASE_NAME}",
    echo=False  # Установить True для отладки SQL запросов
)

#  создаем фабрику сессий
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


def get_db_session():
    """Создает новую сессию БД"""
    return SessionLocal()