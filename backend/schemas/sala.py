from pydantic import BaseModel, Field
from typing import Optional


class SalaBase(BaseModel):
    nome: str = Field(..., max_length=50)
    descricao: Optional[str] = None
    capacidade: int = Field(..., ge=1)
    localizacao: Optional[str] = Field(None, max_length=50)


class SalaCreate(SalaBase):
    ativo: bool = True


class SalaUpdate(BaseModel):
    nome: Optional[str] = Field(None, max_length=50)
    descricao: Optional[str] = None
    capacidade: Optional[int] = Field(None, ge=1)
    localizacao: Optional[str] = Field(None, max_length=50)
    ativo: Optional[bool] = None


class SalaResponse(SalaBase):
    id: int
    ativo: bool

    class Config:
        from_attributes = True
