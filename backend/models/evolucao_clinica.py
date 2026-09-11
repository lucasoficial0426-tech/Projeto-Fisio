from sqlalchemy import Column, Integer, String, DateTime, Text, ForeignKey
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from .base import Base


class EvolucaoClinica(Base):
    __tablename__ = "evolucoes_clinicas"

    id = Column(Integer, primary_key=True, autoincrement=True)
    sessao_id = Column(Integer, ForeignKey("sessoes.id"), nullable=False, unique=True)
    profissional_id = Column(Integer, ForeignKey("profissionais.id"), nullable=False)
    data_registro = Column(DateTime, nullable=False, default=func.current_timestamp())
    descricao = Column(Text, nullable=False)
    objetivos = Column(Text)
    conduta = Column(Text)

    # Relacionamentos
    sessao = relationship("Sessao", backref="evolucao")
    profissional = relationship("Profissional", backref="evolucoes")
