from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime
from enum import Enum


class StatusFatura(str, Enum):
    PENDENTE = "PENDENTE"
    FATURADO = "FATURADO"
    BLOQUEADO = "BLOQUEADO"


class FaturaBase(BaseModel):
    sessao_id: int
    lote_id: int
    convenio_id: int
    valor: float = Field(..., gt=0)
    status: StatusFatura = StatusFatura.PENDENTE
    observacoes: Optional[str] = None


class FaturaCreate(FaturaBase):
    pass


class FaturaUpdate(BaseModel):
    status: Optional[StatusFatura] = None
    observacoes: Optional[str] = None


class FaturaResponse(FaturaBase):
    id: int
    data_faturamento: datetime

    class Config:
        from_attributes = True
