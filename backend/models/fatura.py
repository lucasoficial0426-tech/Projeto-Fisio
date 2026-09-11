from sqlalchemy import Column, Integer, String, DateTime, Text, ForeignKey, Numeric, CheckConstraint
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from enum import Enum
from .base import Base


class StatusFatura(str, Enum):
    PENDENTE = "PENDENTE"
    FATURADO = "FATURADO"
    BLOQUEADO = "BLOQUEADO"


class Fatura(Base):
    __tablename__ = "faturas"

    id = Column(Integer, primary_key=True, autoincrement=True)
    sessao_id = Column(Integer, ForeignKey("sessoes.id"), nullable=False)
    lote_id = Column(Integer, ForeignKey("lotes.id"), nullable=False)
    convenio_id = Column(Integer, ForeignKey("convenios.id"), nullable=False)
    valor = Column(Numeric(10, 2), nullable=False)
    data_faturamento = Column(DateTime, nullable=False, default=func.current_timestamp())
    status = Column(String(20), nullable=False, default="PENDENTE")
    observacoes = Column(Text)

    # Constraints
    __table_args__ = (
        CheckConstraint("valor > 0", name="chk_valor_positivo"),
    )

    # Relacionamentos
    sessao = relationship("Sessao", backref="faturas")
    lote = relationship("Lote", backref="faturas")
    convenio = relationship("Convenio", backref="faturas")
