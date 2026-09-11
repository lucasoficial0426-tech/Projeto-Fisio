from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List
from ..database import get_db
from ..schemas.lote import LoteCreate, LoteUpdate, LoteResponse
from ..services.lote_service import LoteService

router = APIRouter()


@router.post("/", response_model=LoteResponse, status_code=status.HTTP_201_CREATED)
def create_lote(lote: LoteCreate, db: Session = Depends(get_db)):
    """Cria um novo lote de faturamento"""
    service = LoteService(db)
    return service.create(lote)


@router.get("/{lote_id}", response_model=LoteResponse)
def read_lote(lote_id: int, db: Session = Depends(get_db)):
    """Obtém um lote pelo ID"""
    service = LoteService(db)
    lote = service.get_by_id(lote_id)
    if not lote:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Lote não encontrado"
        )
    return lote


@router.get("/", response_model=List[LoteResponse])
def read_all_lotes(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    """Lista todos os lotes"""
    service = LoteService(db)
    return service.get_all(skip, limit)


@router.get("/convenio/{convenio_id}", response_model=List[LoteResponse])
def read_lotes_by_convenio(convenio_id: int, db: Session = Depends(get_db)):
    """Lista todos os lotes de um convênio"""
    service = LoteService(db)
    return service.get_by_convenio(convenio_id)


@router.put("/{lote_id}", response_model=LoteResponse)
def update_lote(lote_id: int, lote: LoteUpdate, db: Session = Depends(get_db)):
    """Atualiza um lote"""
    service = LoteService(db)
    updated_lote = service.update(lote_id, lote)
    if not updated_lote:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Lote não encontrado"
        )
    return updated_lote


@router.delete("/{lote_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_lote(lote_id: int, db: Session = Depends(get_db)):
    """Deleta um lote"""
    service = LoteService(db)
    if not service.delete(lote_id):
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Lote não encontrado"
        )
    return None


@router.post("/{lote_id}/fechar/", response_model=LoteResponse)
def fechar_lote(lote_id: int, db: Session = Depends(get_db)):
    """Fecha um lote para faturamento"""
    service = LoteService(db)
    lote = service.fechar_lote(lote_id)
    if not lote:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Lote não encontrado"
        )
    return lote


@router.post("/{lote_id}/faturar/", response_model=LoteResponse)
def faturar_lote(lote_id: int, db: Session = Depends(get_db)):
    """Marca um lote como faturado"""
    service = LoteService(db)
    lote = service.faturar_lote(lote_id)
    if not lote:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Lote não encontrado"
        )
    return lote
