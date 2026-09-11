from pydantic import BaseModel, Field
from typing import Optional
from datetime import date


class PacienteBase(BaseModel):
    nome: str = Field(..., max_length=100)
    cpf: str = Field(..., max_length=14)
    data_nascimento: date
    telefone: str = Field(..., max_length=20)
    email: Optional[str] = Field(None, max_length=100)
    endereco: str
    convenio_id: Optional[int] = None


class PacienteCreate(PacienteBase):
    ativo: bool = True


class PacienteUpdate(BaseModel):
    nome: Optional[str] = Field(None, max_length=100)
    cpf: Optional[str] = Field(None, max_length=14)
    data_nascimento: Optional[date] = None
    telefone: Optional[str] = Field(None, max_length=20)
    email: Optional[str] = Field(None, max_length=100)
    endereco: Optional[str] = None
    convenio_id: Optional[int] = None
    ativo: Optional[bool] = None


class PacienteResponse(PacienteBase):
    id: int
    data_cadastro: date
    ativo: bool
    convenio_nome: Optional[str] = None

    class Config:
        from_attributes = True
