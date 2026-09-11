from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime
from enum import Enum


class StatusLote(str, Enum):
    ABERTO = "ABERTO"
    FECHADO = "FECHADO"
    FATURADO = "FATURADO"


class LoteBase(BaseModel):
    convenio_id: int
    status: StatusLote = StatusLote.ABERTO
    valor_total: float = Field(0.00, ge=0)
    observacoes: Optional[str] = None


class LoteCreate(LoteBase):
    pass


class LoteUpdate(BaseModel):
    data_fechamento: Optional[datetime] = None
    data_faturamento: Optional[datetime] = None
    status: Optional[StatusLote] = None
    valor_total: Optional[float] = Field(None, ge=0)
    observacoes: Optional[str] = None


class LoteResponse(LoteBase):
    id: int
    data_criacao: datetime
    data_fechamento: Optional[datetime] = None
    data_faturamento: Optional[datetime] = None

    class Config:
        from_attributes = True
