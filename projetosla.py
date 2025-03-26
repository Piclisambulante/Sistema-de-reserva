import os
from sqlalchemy import create_engine, Column, String, Integer, ForeignKey, DateTime
from sqlalchemy.orm import sessionmaker, declarative_base
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime

# Configuração da DB
db = create_engine("sqlite:///banco.db", echo=True)
Session = sessionmaker(bind=db)
session = Session()
Base = declarative_base()

salao_preserva = [1, 2, 3, 4, 5, 6, 7, 8, 9, 10]

class Clientes(Base): 
    __tablename__ = "clientes" 

    id = Column(Integer, primary_key=True, autoincrement=True)
    nome = Column(String, nullable=False)
    cpf = Column(String, nullable=False, unique=True)
    password_hash = Column(String(256), nullable=False)

    def __init__(self, nome, cpf, password):
        self.nome = nome
        self.cpf = cpf
        self.set_password(password)

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

class Reserva(Base):
    __tablename__ = "reservas"  

    id = Column(Integer, autoincrement=True, primary_key=True)
    salao = Column(Integer, nullable=False)
    dono = Column(ForeignKey("clientes.id"), nullable=False)
    data_pedido = Column(DateTime, default=datetime.utcnow, nullable=False) 
    data_reserva = Column(DateTime, nullable=False)


Base.metadata.create_all(db)
