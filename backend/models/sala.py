from sqlalchemy import Column, Integer, String, Text, Boolean
from .base import Base


class Sala(Base):
    __tablename__ = "salas"

    id = Column(Integer, primary_key=True, autoincrement=True)
    nome = Column(String(50), nullable=False)
    descricao = Column(Text)
    capacidade = Column(Integer, nullable=False, default=1)
    localizacao = Column(String(50))
    ativo = Column(Boolean, nullable=False, default=True)

    # Relacionamentos
    sessoes = relationship("Sessao", backref="sala", cascade="all, delete-orphan")
