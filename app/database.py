import os
from pathlib import Path

from dotenv import load_dotenv
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

dotenv_path = Path(__file__).parents[1] / '.env'
load_dotenv(dotenv_path=dotenv_path.resolve())

SQLALCHEMY_DATABASE_URL = os.getenv('DB_CONN') + '?check_same_thread=False'

engine = create_engine(SQLALCHEMY_DATABASE_URL)
session_local = sessionmaker(autocommit=False, autoflush=False, bind=engine)

base = declarative_base()
