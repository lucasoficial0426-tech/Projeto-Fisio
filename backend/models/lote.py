from sqlalchemy import Column, Integer, String, DateTime, Text, ForeignKey, Numeric, CheckConstraint
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from enum import Enum
from .base import Base


class StatusLote(str, Enum):
    ABERTO = "ABERTO"
    FECHADO = "FECHADO"
    FATURADO = "FATURADO"


class Lote(Base):
    __tablename__ = "lotes"

    id = Column(Integer, primary_key=True, autoincrement=True)
    convenio_id = Column(Integer, ForeignKey("convenios.id"), nullable=False)
    data_criacao = Column(DateTime, nullable=False, default=func.current_timestamp())
    data_fechamento = Column(DateTime)
    data_faturamento = Column(DateTime)
    status = Column(String(20), nullable=False, default="ABERTO")
    valor_total = Column(Numeric(12, 2), nullable=False, default=0.00)
    observacoes = Column(Text)

    # Constraints
    __table_args__ = (
        CheckConstraint("valor_total >= 0", name="chk_valor_total_nao_negativo"),
    )

    # Relacionamentos
    convenio = relationship("Convenio", backref="lotes")
    faturas = relationship("Fatura", backref="lote", cascade="all, delete-orphan")
