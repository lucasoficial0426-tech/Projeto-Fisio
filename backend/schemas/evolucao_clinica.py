from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime


class EvolucaoClinicaBase(BaseModel):
    sessao_id: int
    profissional_id: int
    descricao: str
    objetivos: Optional[str] = None
    conduta: Optional[str] = None


class EvolucaoClinicaCreate(EvolucaoClinicaBase):
    pass


class EvolucaoClinicaUpdate(BaseModel):
    descricao: Optional[str] = None
    objetivos: Optional[str] = None
    conduta: Optional[str] = None


class EvolucaoClinicaResponse(EvolucaoClinicaBase):
    id: int
    data_registro: datetime

    class Config:
        from_attributes = True
