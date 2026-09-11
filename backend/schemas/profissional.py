from pydantic import BaseModel, Field
from typing import Optional
from datetime import date


class ProfissionalBase(BaseModel):
    nome: str = Field(..., max_length=100)
    cpf: str = Field(..., max_length=14)
    crf: str = Field(..., max_length=20)
    especialidade: str = Field(..., max_length=50)
    telefone: str = Field(..., max_length=20)
    email: str = Field(..., max_length=100)


class ProfissionalCreate(ProfissionalBase):
    ativo: bool = True


class ProfissionalUpdate(BaseModel):
    nome: Optional[str] = Field(None, max_length=100)
    cpf: Optional[str] = Field(None, max_length=14)
    crf: Optional[str] = Field(None, max_length=20)
    especialidade: Optional[str] = Field(None, max_length=50)
    telefone: Optional[str] = Field(None, max_length=20)
    email: Optional[str] = Field(None, max_length=100)
    ativo: Optional[bool] = None


class ProfissionalResponse(ProfissionalBase):
    id: int
    data_cadastro: date
    ativo: bool

    class Config:
        from_attributes = True
