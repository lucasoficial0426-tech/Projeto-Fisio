from sqlalchemy import Column, Integer, String, Date, Boolean, Numeric, ForeignKey, CheckConstraint
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from enum import Enum
from .base import Base


class TipoPagamento(str, Enum):
    CONVENIO = "CONVENIO"
    PARTICULAR = "PARTICULAR"


class StatusPacote(str, Enum):
    ATIVO = "ATIVO"
    EXPIRADO = "EXPIRADO"
    UTILIZADO = "UTILIZADO"


class Pacote(Base):
    __tablename__ = "pacotes"

    id = Column(Integer, primary_key=True, autoincrement=True)
    paciente_id = Column(Integer, ForeignKey("pacientes.id"), nullable=False)
    data_compra = Column(Date, nullable=False)
    data_expiracao = Column(Date, nullable=False)
    sessao_total = Column(Integer, nullable=False, default=10)
    sessao_restante = Column(Integer, nullable=False, default=10)
    tipo_pagamento = Column(String(20), nullable=False)
    valor = Column(Numeric(10, 2), nullable=False)
    status = Column(String(20), nullable=False, default="ATIVO")
    convenio_id = Column(Integer, ForeignKey("convenios.id"), nullable=True)

    # Constraints
    __table_args__ = (
        CheckConstraint("sessao_total > 0", name="chk_sessao_total_positivo"),
        CheckConstraint("sessao_restante >= 0", name="chk_sessao_restante_nao_negativo"),
        CheckConstraint("sessao_restante <= sessao_total", name="chk_sessao_restante_valida"),
        CheckConstraint("valor > 0", name="chk_valor_positivo"),
        CheckConstraint(
            "data_expiracao = data_compra + INTERVAL '90 days'",
            name="chk_expiracao_90_dias"
        ),
    )

    # Relacionamentos
    paciente = relationship("Paciente", backref="pacotes")
    convenio = relationship("Convenio", backref="pacotes")
    sessoes = relationship("Sessao", backref="pacote", foreign_keys="Sessao.pacote_id")
