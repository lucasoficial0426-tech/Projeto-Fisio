from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime
from enum import Enum


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


class SessaoBase(BaseModel):
    paciente_id: int
    profissional_id: int
    sala_id: int
    data_hora_inicio: datetime
    data_hora_fim: datetime
    pacote_id: Optional[int] = None
    convenio_id: Optional[int] = None
    status: StatusSessao = StatusSessao.AGENDADO
    tipo_atendimento: TipoAtendimento = TipoAtendimento.NORMAL
    observacoes: Optional[str] = None
    atraso_minutos: int = Field(0, ge=0)


class SessaoCreate(SessaoBase):
    pass


class SessaoUpdate(BaseModel):
    status: Optional[StatusSessao] = None
    tipo_atendimento: Optional[TipoAtendimento] = None
    observacoes: Optional[str] = None
    atraso_minutos: Optional[int] = Field(None, ge=0)


class SessaoResponse(SessaoBase):
    id: int
    data_agendamento: datetime

    class Config:
        from_attributes = True
