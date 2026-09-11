from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime


class FaltaBase(BaseModel):
    sessao_id: int
    avisado: bool = False
    antecedencia_horas: float = Field(0, ge=0)
    justificativa: Optional[str] = None


class FaltaCreate(FaltaBase):
    pass


class FaltaUpdate(BaseModel):
    avisado: Optional[bool] = None
    antecedencia_horas: Optional[float] = Field(None, ge=0)
    justificativa: Optional[str] = None


class FaltaResponse(FaltaBase):
    id: int
    data_registro: datetime

    class Config:
        from_attributes = True
