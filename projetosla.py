import os
from sqlalchemy import create_engine, Column, String, Integer, ForeignKey, REAL
from sqlalchemy.orm import sessionmaker, declarative_base
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime, timezone


db = create_engine("sqlite:///banco.db")
Session = sessionmaker(bind=db)
session = Session()
Base = declarative_base()

