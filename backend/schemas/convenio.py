from pydantic import BaseModel, Field
from typing import Optional
from datetime import date


class ConvenioBase(BaseModel):
    nome: str = Field(..., max_length=100)
    cnpj: str = Field(..., max_length=18)
    telefone: str = Field(..., max_length=20)
    email: str = Field(..., max_length=100)
    endereco: str
    taxa_desconto: float = Field(..., ge=0, le=100)
    data_contrato: date


class ConvenioCreate(ConvenioBase):
    ativo: bool = True


class ConvenioUpdate(BaseModel):
    nome: Optional[str] = Field(None, max_length=100)
    cnpj: Optional[str] = Field(None, max_length=18)
    telefone: Optional[str] = Field(None, max_length=20)
    email: Optional[str] = Field(None, max_length=100)
    endereco: Optional[str] = None
    taxa_desconto: Optional[float] = Field(None, ge=0, le=100)
    data_contrato: Optional[date] = None
    ativo: Optional[bool] = None


class ConvenioResponse(ConvenioBase):
    id: int
    ativo: bool
    data_cadastro: date

    class Config:
        from_attributes = True
