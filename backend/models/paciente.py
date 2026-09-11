from sqlalchemy import Column, Integer, String, Date, Boolean, Text, ForeignKey
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from .base import Base


class Paciente(Base):
    __tablename__ = "pacientes"

    id = Column(Integer, primary_key=True, autoincrement=True)
    nome = Column(String(100), nullable=False)
    cpf = Column(String(14), nullable=False, unique=True)
    data_nascimento = Column(Date, nullable=False)
    telefone = Column(String(20), nullable=False)
    email = Column(String(100))
    endereco = Column(Text, nullable=False)
    convenio_id = Column(Integer, ForeignKey("convenios.id"), nullable=True)
    data_cadastro = Column(Date, nullable=False, default=func.current_timestamp())
    ativo = Column(Boolean, nullable=False, default=True)

    # Relacionamentos
    convenio = relationship("Convenio", backref="pacientes")
    pacotes = relationship("Pacote", backref="paciente", cascade="all, delete-orphan")
    sessoes = relationship("Sessao", backref="paciente", cascade="all, delete-orphan")
