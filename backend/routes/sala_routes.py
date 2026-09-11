from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List
from datetime import datetime
from ..database import get_db
from ..schemas.sala import SalaCreate, SalaUpdate, SalaResponse
from ..services.sala_service import SalaService

router = APIRouter()


@router.post("/", response_model=SalaResponse, status_code=status.HTTP_201_CREATED)
def create_sala(sala: SalaCreate, db: Session = Depends(get_db)):
    """Cria uma nova sala"""
    service = SalaService(db)
    return service.create(sala)


@router.get("/{sala_id}", response_model=SalaResponse)
def read_sala(sala_id: int, db: Session = Depends(get_db)):
    """Obtém uma sala pelo ID"""
    service = SalaService(db)
    sala = service.get_by_id(sala_id)
    if not sala:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Sala não encontrada"
        )
    return sala


@router.get("/", response_model=List[SalaResponse])
def read_all_salas(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    """Lista todas as salas"""
    service = SalaService(db)
    return service.get_all(skip, limit)


@router.put("/{sala_id}", response_model=SalaResponse)
def update_sala(sala_id: int, sala: SalaUpdate, db: Session = Depends(get_db)):
    """Atualiza uma sala"""
    service = SalaService(db)
    updated_sala = service.update(sala_id, sala)
    if not updated_sala:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Sala não encontrada"
        )
    return updated_sala


@router.delete("/{sala_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_sala(sala_id: int, db: Session = Depends(get_db)):
    """Deleta uma sala"""
    service = SalaService(db)
    if not service.delete(sala_id):
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Sala não encontrada"
        )
    return None


@router.get("/disponiveis/", response_model=List[SalaResponse])
def get_salas_disponiveis(
    data_hora_inicio: str,
    data_hora_fim: str,
    db: Session = Depends(get_db)
):
    """Retorna salas disponíveis em um horário específico (RN-04)"""
    service = SalaService(db)
    
    try:
        dt_inicio = datetime.fromisoformat(data_hora_inicio)
        dt_fim = datetime.fromisoformat(data_hora_fim)
    except ValueError:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Formato de data/hora inválido. Use ISO format (YYYY-MM-DDTHH:MM:SS)"
        )
    
    return service.get_salas_disponiveis(dt_inicio, dt_fim)


@router.get("/{sala_id}/capacidade/", response_model=bool)
def verificar_capacidade_sala(
    sala_id: int,
    data_hora_inicio: str,
    data_hora_fim: str,
    db: Session = Depends(get_db)
):
    """Verifica se uma sala tem capacidade para mais uma sessão no horário (RN-04)"""
    service = SalaService(db)
    
    try:
        dt_inicio = datetime.fromisoformat(data_hora_inicio)
        dt_fim = datetime.fromisoformat(data_hora_fim)
    except ValueError:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Formato de data/hora inválido. Use ISO format (YYYY-MM-DDTHH:MM:SS)"
        )
    
    return service.verificar_capacidade_sala(sala_id, dt_inicio, dt_fim)
