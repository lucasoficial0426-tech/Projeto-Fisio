from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List
from datetime import datetime
from ..database import get_db
from ..schemas.profissional import ProfissionalCreate, ProfissionalUpdate, ProfissionalResponse
from ..services.profissional_service import ProfissionalService

router = APIRouter()


@router.post("/", response_model=ProfissionalResponse, status_code=status.HTTP_201_CREATED)
def create_profissional(profissional: ProfissionalCreate, db: Session = Depends(get_db)):
    """Cria um novo profissional"""
    service = ProfissionalService(db)
    
    # Verificar se CPF já existe
    if service.get_by_cpf(profissional.cpf):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="CPF já cadastrado"
        )
    
    # Verificar se CRF já existe
    if service.get_by_crf(profissional.crf):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="CRF já cadastrado"
        )
    
    return service.create(profissional)


@router.get("/{profissional_id}", response_model=ProfissionalResponse)
def read_profissional(profissional_id: int, db: Session = Depends(get_db)):
    """Obtém um profissional pelo ID"""
    service = ProfissionalService(db)
    profissional = service.get_by_id(profissional_id)
    if not profissional:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Profissional não encontrado"
        )
    return profissional


@router.get("/", response_model=List[ProfissionalResponse])
def read_all_profissionais(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    """Lista todos os profissionais"""
    service = ProfissionalService(db)
    return service.get_all(skip, limit)


@router.put("/{profissional_id}", response_model=ProfissionalResponse)
def update_profissional(profissional_id: int, profissional: ProfissionalUpdate, db: Session = Depends(get_db)):
    """Atualiza um profissional"""
    service = ProfissionalService(db)
    updated_profissional = service.update(profissional_id, profissional)
    if not updated_profissional:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Profissional não encontrado"
        )
    return updated_profissional


@router.delete("/{profissional_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_profissional(profissional_id: int, db: Session = Depends(get_db)):
    """Deleta um profissional"""
    service = ProfissionalService(db)
    if not service.delete(profissional_id):
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Profissional não encontrado"
        )
    return None


@router.get("/disponiveis/", response_model=List[ProfissionalResponse])
def get_profissionais_disponiveis(
    data_hora_inicio: str,
    data_hora_fim: str,
    db: Session = Depends(get_db)
):
    """Retorna profissionais disponíveis em um horário específico (RN-05)"""
    service = ProfissionalService(db)
    
    try:
        dt_inicio = datetime.fromisoformat(data_hora_inicio)
        dt_fim = datetime.fromisoformat(data_hora_fim)
    except ValueError:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Formato de data/hora inválido. Use ISO format (YYYY-MM-DDTHH:MM:SS)"
        )
    
    return service.get_profissionais_disponiveis(dt_inicio, dt_fim)
