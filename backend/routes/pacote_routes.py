from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List
from datetime import date
from ..database import get_db
from ..schemas.pacote import PacoteCreate, PacoteUpdate, PacoteResponse
from ..services.pacote_service import PacoteService

router = APIRouter()


@router.post("/", response_model=PacoteResponse, status_code=status.HTTP_201_CREATED)
def create_pacote(pacote: PacoteCreate, db: Session = Depends(get_db)):
    """Cria um novo pacote de sessões (RN-01: expira em 90 dias)"""
    service = PacoteService(db)
    
    # Verificar se paciente existe
    from ..services.paciente_service import PacienteService
    paciente_service = PacienteService(db)
    if not paciente_service.get_by_id(pacote.paciente_id):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Paciente não encontrado"
        )
    
    return service.create(pacote)


@router.get("/{pacote_id}", response_model=PacoteResponse)
def read_pacote(pacote_id: int, db: Session = Depends(get_db)):
    """Obtém um pacote pelo ID"""
    service = PacoteService(db)
    pacote = service.get_by_id(pacote_id)
    if not pacote:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Pacote não encontrado"
        )
    return pacote


@router.get("/", response_model=List[PacoteResponse])
def read_all_pacotes(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    """Lista todos os pacotes"""
    service = PacoteService(db)
    return service.get_all(skip, limit)


@router.get("/paciente/{paciente_id}", response_model=List[PacoteResponse])
def read_pacotes_by_paciente(paciente_id: int, db: Session = Depends(get_db)):
    """Lista todos os pacotes de um paciente"""
    service = PacoteService(db)
    return service.get_by_paciente(paciente_id)


@router.put("/{pacote_id}", response_model=PacoteResponse)
def update_pacote(pacote_id: int, pacote: PacoteUpdate, db: Session = Depends(get_db)):
    """Atualiza um pacote"""
    service = PacoteService(db)
    updated_pacote = service.update(pacote_id, pacote)
    if not updated_pacote:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Pacote não encontrado"
        )
    return updated_pacote


@router.delete("/{pacote_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_pacote(pacote_id: int, db: Session = Depends(get_db)):
    """Deleta um pacote"""
    service = PacoteService(db)
    if not service.delete(pacote_id):
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Pacote não encontrado"
        )
    return None


@router.post("/{pacote_id}/consumir-sessao/", response_model=PacoteResponse)
def consumir_sessao(pacote_id: int, db: Session = Depends(get_db)):
    """Consome uma sessão do pacote (RN-02, RN-07)"""
    service = PacoteService(db)
    pacote = service.get_by_id(pacote_id)
    if not pacote:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Pacote não encontrado"
        )
    
    if not service.consumir_sessao(pacote_id):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Não foi possível consumir sessão (pacote sem saldo ou expirado)"
        )
    
    return pacote


@router.get("/validar/{pacote_id}", response_model=bool)
def validar_pacote_para_agendamento(pacote_id: int, db: Session = Depends(get_db)):
    """
    RN-07: Valida se um pacote pode ser usado para agendamento
    (Paciente particular com pacote expirado ou saldo zerado não pode ser agendado)
    """
    service = PacoteService(db)
    return service.validar_pacote_para_agendamento(pacote_id)


@router.get("/proximos-expirar/", response_model=List[PacoteResponse])
def get_pacotes_proximos_expirar(dias: int = 30, db: Session = Depends(get_db)):
    """
    RN-01: Retorna pacotes que irão expirar nos próximos dias
    """
    service = PacoteService(db)
    return service.get_pacotes_proximos_expirar(dias)
