import os
from dotenv import load_dotenv

load_dotenv()

class Config:
    SQLALCHEMY_DATABASE_URI = f"postgresql://{os.getenv('LOTTRACK_DB_USER')}:{os.getenv('LOTTRACK_DB_PASSWORD')}@{os.getenv('LOTTRACK_DB_HOST')}:{os.getenv('LOTTRACK_DB_PORT')}/{os.getenv('LOTTRACK_DB_NAME')}"
    SQLALCHEMY_TRACK_MODIFICATIONS = False
