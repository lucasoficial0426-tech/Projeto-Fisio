from sqlalchemy import Column, Integer, String, DateTime, Boolean, Text, ForeignKey, Numeric, CheckConstraint
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from .base import Base


class Falta(Base):
    __tablename__ = "faltas"

    id = Column(Integer, primary_key=True, autoincrement=True)
    sessao_id = Column(Integer, ForeignKey("sessoes.id"), nullable=False, unique=True)
    data_registro = Column(DateTime, nullable=False, default=func.current_timestamp())
    avisado = Column(Boolean, nullable=False, default=False)
    antecedencia_horas = Column(Numeric(5, 2), nullable=False, default=0)
    justificativa = Column(Text)

    # Constraints
    __table_args__ = (
        CheckConstraint("antecedencia_horas >= 0", name="chk_antecedencia_nao_negativa"),
    )

    # Relacionamentos
    sessao = relationship("Sessao", backref="falta")
