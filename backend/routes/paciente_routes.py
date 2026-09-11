from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List
from ..database import get_db
from ..schemas.paciente import PacienteCreate, PacienteUpdate, PacienteResponse
from ..services.paciente_service import PacienteService

router = APIRouter()


@router.post("/", response_model=PacienteResponse, status_code=status.HTTP_201_CREATED)
def create_paciente(paciente: PacienteCreate, db: Session = Depends(get_db)):
    """Cria um novo paciente"""
    service = PacienteService(db)
    
    # Verificar se CPF já existe
    if service.get_by_cpf(paciente.cpf):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="CPF já cadastrado"
        )
    
    return service.create(paciente)


@router.get("/{paciente_id}", response_model=PacienteResponse)
def read_paciente(paciente_id: int, db: Session = Depends(get_db)):
    """Obtém um paciente pelo ID"""
    service = PacienteService(db)
    paciente = service.get_by_id(paciente_id)
    if not paciente:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Paciente não encontrado"
        )
    return paciente


@router.get("/", response_model=List[PacienteResponse])
def read_all_pacientes(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    """Lista todos os pacientes"""
    service = PacienteService(db)
    return service.get_all(skip, limit)


@router.put("/{paciente_id}", response_model=PacienteResponse)
def update_paciente(paciente_id: int, paciente: PacienteUpdate, db: Session = Depends(get_db)):
    """Atualiza um paciente"""
    service = PacienteService(db)
    updated_paciente = service.update(paciente_id, paciente)
    if not updated_paciente:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Paciente não encontrado"
        )
    return updated_paciente


@router.delete("/{paciente_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_paciente(paciente_id: int, db: Session = Depends(get_db)):
    """Deleta um paciente"""
    service = PacienteService(db)
    if not service.delete(paciente_id):
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Paciente não encontrado"
        )
    return None


@router.get("/com-pacotes-ativos/", response_model=List[PacienteResponse])
def get_pacientes_com_pacotes_ativos(db: Session = Depends(get_db)):
    """Retorna pacientes com pacotes ativos (RN-07)"""
    service = PacienteService(db)
    return service.get_pacientes_com_pacotes_ativos()
