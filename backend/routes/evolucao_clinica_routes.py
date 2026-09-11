from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List
from ..database import get_db
from ..schemas.evolucao_clinica import EvolucaoClinicaCreate, EvolucaoClinicaUpdate, EvolucaoClinicaResponse
from ..services.evolucao_clinica_service import EvolucaoClinicaService

router = APIRouter()


@router.post("/", response_model=EvolucaoClinicaResponse, status_code=status.HTTP_201_CREATED)
def create_evolucao(evolucao: EvolucaoClinicaCreate, db: Session = Depends(get_db)):
    """Cria um registro de evolução clínica para uma sessão"""
    service = EvolucaoClinicaService(db)
    
    # Verificar se já existe evolução para esta sessão
    if service.get_by_sessao(evolucao.sessao_id):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Já existe uma evolução clínica para esta sessão"
        )
    
    return service.create(evolucao)


@router.get("/{evolucao_id}", response_model=EvolucaoClinicaResponse)
def read_evolucao(evolucao_id: int, db: Session = Depends(get_db)):
    """Obtém uma evolução clínica pelo ID"""
    service = EvolucaoClinicaService(db)
    evolucao = service.get_by_id(evolucao_id)
    if not evolucao:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Evolução clínica não encontrada"
        )
    return evolucao


@router.get("/", response_model=List[EvolucaoClinicaResponse])
def read_all_evolucoes(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    """Lista todas as evoluções clínicas"""
    service = EvolucaoClinicaService(db)
    return service.get_all(skip, limit)


@router.get("/sessao/{sessao_id}", response_model=EvolucaoClinicaResponse)
def read_evolucao_by_sessao(sessao_id: int, db: Session = Depends(get_db)):
    """Obtém a evolução clínica de uma sessão"""
    service = EvolucaoClinicaService(db)
    evolucao = service.get_by_sessao(sessao_id)
    if not evolucao:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Evolução clínica não encontrada para esta sessão"
        )
    return evolucao


@router.put("/{evolucao_id}", response_model=EvolucaoClinicaResponse)
def update_evolucao(evolucao_id: int, evolucao: EvolucaoClinicaUpdate, db: Session = Depends(get_db)):
    """Atualiza uma evolução clínica"""
    service = EvolucaoClinicaService(db)
    updated_evolucao = service.update(evolucao_id, evolucao)
    if not updated_evolucao:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Evolução clínica não encontrada"
        )
    return updated_evolucao


@router.delete("/{evolucao_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_evolucao(evolucao_id: int, db: Session = Depends(get_db)):
    """Deleta uma evolução clínica"""
    service = EvolucaoClinicaService(db)
    if not service.delete(evolucao_id):
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Evolução clínica não encontrada"
        )
    return None


@router.get("/sessao/{sessao_id}/tem-evolucao/", response_model=bool)
def tem_evolucao(sessao_id: int, db: Session = Depends(get_db)):
    """
    RN-06: Verifica se uma sessão tem evolução clínica registrada
    (Sessão de convênio só pode ser faturada se tiver evolução clínica)
    """
    service = EvolucaoClinicaService(db)
    return service.tem_evolucao(sessao_id)
