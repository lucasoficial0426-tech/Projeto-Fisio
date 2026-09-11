from sqlalchemy import Column, Integer, String, Date, Boolean, Numeric, Text
from sqlalchemy.sql import func
from .base import Base


class Convenio(Base):
    __tablename__ = "convenios"

    id = Column(Integer, primary_key=True, autoincrement=True)
    nome = Column(String(100), nullable=False)
    cnpj = Column(String(18), nullable=False, unique=True)
    telefone = Column(String(20), nullable=False)
    email = Column(String(100), nullable=False)
    endereco = Column(Text, nullable=False)
    taxa_desconto = Column(Numeric(5, 2), nullable=False, default=0.00)
    data_contrato = Column(Date, nullable=False)
    ativo = Column(Boolean, nullable=False, default=True)
    data_cadastro = Column(Date, nullable=False, default=func.current_date())
