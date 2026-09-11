from pydantic import BaseModel, Field
from typing import Optional
from datetime import date
from enum import Enum


class TipoPagamento(str, Enum):
    CONVENIO = "CONVENIO"
    PARTICULAR = "PARTICULAR"


class StatusPacote(str, Enum):
    ATIVO = "ATIVO"
    EXPIRADO = "EXPIRADO"
    UTILIZADO = "UTILIZADO"


class PacoteBase(BaseModel):
    paciente_id: int
    data_compra: date
    data_expiracao: date
    sessao_total: int = Field(..., ge=1)
    sessao_restante: int = Field(..., ge=0)
    tipo_pagamento: TipoPagamento
    valor: float = Field(..., gt=0)
    convenio_id: Optional[int] = None


class PacoteCreate(PacoteBase):
    pass


class PacoteUpdate(BaseModel):
    sessao_restante: Optional[int] = Field(None, ge=0)
    status: Optional[StatusPacote] = None


class PacoteResponse(PacoteBase):
    id: int
    status: StatusPacote

    class Config:
        from_attributes = True
