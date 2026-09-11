from sqlalchemy import Column, Integer, String, DateTime, Boolean, Text, ForeignKey, CheckConstraint
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from enum import Enum
from .base import Base


class StatusSessao(str, Enum):
    AGENDADO = "AGENDADO"
    CONFIRMADO = "CONFIRMADO"
    REALIZADO = "REALIZADO"
    CANCELADO = "CANCELADO"
    FALTA = "FALTA"
    ATRASADO = "ATRASADO"


class TipoAtendimento(str, Enum):
    NORMAL = "NORMAL"
    REDUZIDO = "REDUZIDO"


class Sessao(Base):
    __tablename__ = "sessoes"

    id = Column(Integer, primary_key=True, autoincrement=True)
    paciente_id = Column(Integer, ForeignKey("pacientes.id"), nullable=False)
    profissional_id = Column(Integer, ForeignKey("profissionais.id"), nullable=False)
    sala_id = Column(Integer, ForeignKey("salas.id"), nullable=False)
    pacote_id = Column(Integer, ForeignKey("pacotes.id"), nullable=True)
    convenio_id = Column(Integer, ForeignKey("convenios.id"), nullable=True)
    data_hora_inicio = Column(DateTime, nullable=False)
    data_hora_fim = Column(DateTime, nullable=False)
    status = Column(String(20), nullable=False, default="AGENDADO")
    tipo_atendimento = Column(String(20), nullable=False, default="NORMAL")
    observacoes = Column(Text)
    data_agendamento = Column(DateTime, nullable=False, default=func.current_timestamp())
    atraso_minutos = Column(Integer, default=0)

    # Constraints
    __table_args__ = (
        CheckConstraint("data_hora_fim > data_hora_inicio", name="chk_horario_valido"),
        CheckConstraint("atraso_minutos >= 0", name="chk_atraso_nao_negativo"),
        CheckConstraint(
            "atraso_minutos <= 15 OR tipo_atendimento = 'REDUZIDO'",
            name="chk_atendimento_reduzido"
        ),
    )

    # Relacionamentos
    paciente = relationship("Paciente", backref="sessoes")
    profissional = relationship("Profissional", backref="sessoes")
    sala = relationship("Sala", backref="sessoes")
    pacote = relationship("Pacote", backref="sessoes", foreign_keys=[pacote_id])
    convenio = relationship("Convenio", backref="sessoes")
    evolucao = relationship("EvolucaoClinica", backref="sessao", uselist=False, cascade="all, delete-orphan")
    falta = relationship("Falta", backref="sessao", uselist=False, cascade="all, delete-orphan")
    faturas = relationship("Fatura", backref="sessao", cascade="all, delete-orphan")
