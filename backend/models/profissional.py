from sqlalchemy import Column, Integer, String, Date, Boolean, Text
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from .base import Base


class Profissional(Base):
    __tablename__ = "profissionais"

    id = Column(Integer, primary_key=True, autoincrement=True)
    nome = Column(String(100), nullable=False)
    cpf = Column(String(14), nullable=False, unique=True)
    crf = Column(String(20), nullable=False, unique=True)  # Conselho Regional de Fisioterapia
    especialidade = Column(String(50), nullable=False)
    telefone = Column(String(20), nullable=False)
    email = Column(String(100), nullable=False)
    data_cadastro = Column(Date, nullable=False, default=func.current_timestamp())
    ativo = Column(Boolean, nullable=False, default=True)

    # Relacionamentos
    sessoes = relationship("Sessao", backref="profissional", cascade="all, delete-orphan")
    evolucoes = relationship("EvolucaoClinica", backref="profissional", cascade="all, delete-orphan")
