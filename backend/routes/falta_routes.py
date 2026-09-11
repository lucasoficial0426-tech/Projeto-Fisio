from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List
from ..database import get_db
from ..schemas.falta import FaltaCreate, FaltaUpdate, FaltaResponse
from ..services.falta_service import FaltaService

router = APIRouter()


@router.post("/", response_model=FaltaResponse, status_code=status.HTTP_201_CREATED)
def create_falta(falta: FaltaCreate, db: Session = Depends(get_db)):
    """
    Registra uma falta (RN-02, RN-03):
    - RN-02: Falta sem aviso com antecedência de 24h consome uma sessão do pacote
    - RN-03: Falta avisada com 24h ou mais de antecedência não consome sessão
    """
    service = FaltaService(db)
    
    # Verificar se já existe falta para esta sessão
    if service.get_by_sessao(falta.sessao_id):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Já existe um registro de falta para esta sessão"
        )
    
    return service.create(falta)


@router.get("/{falta_id}", response_model=FaltaResponse)
def read_falta(falta_id: int, db: Session = Depends(get_db)):
    """Obtém uma falta pelo ID"""
    service = FaltaService(db)
    falta = service.get_by_id(falta_id)
    if not falta:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Falta não encontrada"
        )
    return falta


@router.get("/", response_model=List[FaltaResponse])
def read_all_faltas(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    """Lista todas as faltas"""
    service = FaltaService(db)
    return service.get_all(skip, limit)


@router.get("/sessao/{sessao_id}", response_model=FaltaResponse)
def read_falta_by_sessao(sessao_id: int, db: Session = Depends(get_db)):
    """Obtém a falta de uma sessão"""
    service = FaltaService(db)
    falta = service.get_by_sessao(sessao_id)
    if not falta:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Falta não encontrada para esta sessão"
        )
    return falta


@router.put("/{falta_id}", response_model=FaltaResponse)
def update_falta(falta_id: int, falta: FaltaUpdate, db: Session = Depends(get_db)):
    """Atualiza uma falta"""
    service = FaltaService(db)
    updated_falta = service.update(falta_id, falta)
    if not updated_falta:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Falta não encontrada"
        )
    return updated_falta


@router.delete("/{falta_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_falta(falta_id: int, db: Session = Depends(get_db)):
    """Deleta uma falta"""
    service = FaltaService(db)
    if not service.delete(falta_id):
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Falta não encontrada"
        )
    return None
