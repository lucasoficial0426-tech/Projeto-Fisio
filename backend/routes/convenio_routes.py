from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List
from ..database import get_db
from ..schemas.convenio import ConvenioCreate, ConvenioUpdate, ConvenioResponse
from ..services.convenio_service import ConvenioService

router = APIRouter()


@router.post("/", response_model=ConvenioResponse, status_code=status.HTTP_201_CREATED)
def create_convenio(convenio: ConvenioCreate, db: Session = Depends(get_db)):
    """Cria um novo convênio"""
    service = ConvenioService(db)
    
    # Verificar se CNPJ já existe
    if service.get_by_cnpj(convenio.cnpj):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="CNPJ já cadastrado"
        )
    
    return service.create(convenio)


@router.get("/{convenio_id}", response_model=ConvenioResponse)
def read_convenio(convenio_id: int, db: Session = Depends(get_db)):
    """Obtém um convênio pelo ID"""
    service = ConvenioService(db)
    convenio = service.get_by_id(convenio_id)
    if not convenio:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Convênio não encontrado"
        )
    return convenio


@router.get("/", response_model=List[ConvenioResponse])
def read_all_convenios(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    """Lista todos os convênios"""
    service = ConvenioService(db)
    return service.get_all(skip, limit)


@router.put("/{convenio_id}", response_model=ConvenioResponse)
def update_convenio(convenio_id: int, convenio: ConvenioUpdate, db: Session = Depends(get_db)):
    """Atualiza um convênio"""
    service = ConvenioService(db)
    updated_convenio = service.update(convenio_id, convenio)
    if not updated_convenio:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Convênio não encontrado"
        )
    return updated_convenio


@router.delete("/{convenio_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_convenio(convenio_id: int, db: Session = Depends(get_db)):
    """Deleta um convênio"""
    service = ConvenioService(db)
    if not service.delete(convenio_id):
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Convênio não encontrado"
        )
    return None
