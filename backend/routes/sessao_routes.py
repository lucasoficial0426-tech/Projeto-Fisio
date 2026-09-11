from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List
from datetime import datetime
from ..database import get_db
from ..schemas.sessao import SessaoCreate, SessaoUpdate, SessaoResponse
from ..services.sessao_service import SessaoService

router = APIRouter()


@router.post("/", response_model=SessaoResponse, status_code=status.HTTP_201_CREATED)
def create_sessao(sessao: SessaoCreate, db: Session = Depends(get_db)):
    """
    Cria uma nova sessão validando todas as regras de negócio:
    - RN-04: Sala não pode ter mais sessões do que sua capacidade
    - RN-05: Profissional não pode ter duas sessões no mesmo horário
    - RN-07: Paciente particular com pacote expirado ou saldo zerado não pode ser agendado
    - RN-08: Atraso superior a 15 min registra atendimento reduzido
    """
    service = SessaoService(db)
    return service.create(sessao)


@router.get("/{sessao_id}", response_model=SessaoResponse)
def read_sessao(sessao_id: int, db: Session = Depends(get_db)):
    """Obtém uma sessão pelo ID"""
    service = SessaoService(db)
    sessao = service.get_by_id(sessao_id)
    if not sessao:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Sessão não encontrada"
        )
    return sessao


@router.get("/", response_model=List[SessaoResponse])
def read_all_sessoes(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    """Lista todas as sessões"""
    service = SessaoService(db)
    return service.get_all(skip, limit)


@router.get("/paciente/{paciente_id}", response_model=List[SessaoResponse])
def read_sessoes_by_paciente(paciente_id: int, db: Session = Depends(get_db)):
    """Lista todas as sessões de um paciente"""
    service = SessaoService(db)
    return service.get_by_paciente(paciente_id)


@router.get("/profissional/{profissional_id}", response_model=List[SessaoResponse])
def read_sessoes_by_profissional(profissional_id: int, db: Session = Depends(get_db)):
    """Lista todas as sessões de um profissional"""
    service = SessaoService(db)
    return service.get_by_profissional(profissional_id)


@router.get("/sala/{sala_id}", response_model=List[SessaoResponse])
def read_sessoes_by_sala(sala_id: int, db: Session = Depends(get_db)):
    """Lista todas as sessões de uma sala"""
    service = SessaoService(db)
    return service.get_by_sala(sala_id)


@router.get("/data/{data}", response_model=List[SessaoResponse])
def read_sessoes_by_data(data: str, db: Session = Depends(get_db)):
    """Lista todas as sessões de uma data específica"""
    service = SessaoService(db)
    try:
        data_obj = datetime.fromisoformat(data).date()
    except ValueError:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Formato de data inválido. Use YYYY-MM-DD"
        )
    return service.get_by_data(data_obj)


@router.put("/{sessao_id}", response_model=SessaoResponse)
def update_sessao(sessao_id: int, sessao: SessaoUpdate, db: Session = Depends(get_db)):
    """Atualiza uma sessão"""
    service = SessaoService(db)
    updated_sessao = service.update(sessao_id, sessao)
    if not updated_sessao:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Sessão não encontrada"
        )
    return updated_sessao


@router.delete("/{sessao_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_sessao(sessao_id: int, db: Session = Depends(get_db)):
    """Deleta uma sessão"""
    service = SessaoService(db)
    if not service.delete(sessao_id):
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Sessão não encontrada"
        )
    return None


@router.post("/{sessao_id}/confirmar/", response_model=SessaoResponse)
def confirmar_sessao(sessao_id: int, db: Session = Depends(get_db)):
    """Confirma uma sessão agendada"""
    service = SessaoService(db)
    sessao = service.confirmar_sessao(sessao_id)
    if not sessao:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Sessão não encontrada"
        )
    return sessao


@router.post("/{sessao_id}/realizar/", response_model=SessaoResponse)
def realizar_sessao(sessao_id: int, db: Session = Depends(get_db)):
    """Marca uma sessão como realizada"""
    service = SessaoService(db)
    sessao = service.realizar_sessao(sessao_id)
    if not sessao:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Sessão não encontrada"
        )
    return sessao


@router.post("/{sessao_id}/cancelar/", response_model=SessaoResponse)
def cancelar_sessao(sessao_id: int, db: Session = Depends(get_db)):
    """Cancela uma sessão"""
    service = SessaoService(db)
    sessao = service.cancelar_sessao(sessao_id)
    if not sessao:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Sessão não encontrada"
        )
    return sessao


@router.get("/verificar-conflitos/", response_model=dict)
def verificar_conflitos(
    paciente_id: int,
    profissional_id: int,
    sala_id: int,
    data_hora_inicio: str,
    data_hora_fim: str,
    db: Session = Depends(get_db)
):
    """
    Verifica conflitos para agendamento:
    - RN-04: Sala
    - RN-05: Profissional
    """
    service = SessaoService(db)
    
    try:
        dt_inicio = datetime.fromisoformat(data_hora_inicio)
        dt_fim = datetime.fromisoformat(data_hora_fim)
    except ValueError:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Formato de data/hora inválido. Use ISO format (YYYY-MM-DDTHH:MM:SS)"
        )
    
    tem_conflito, mensagem = service.verificar_conflitos(
        paciente_id, profissional_id, sala_id, dt_inicio, dt_fim
    )
    
    return {
        "tem_conflito": tem_conflito,
        "mensagem": mensagem
    }


@router.get("/para-faturamento/{convenio_id}", response_model=List[SessaoResponse])
def get_sessoes_para_faturamento(convenio_id: int, db: Session = Depends(get_db)):
    """
    Retorna sessões de convênio que podem ser faturadas:
    - RN-06: Sessão de convênio só pode ser faturada se tiver evolução clínica
    - RN-08: Atraso superior a 15 min bloqueia faturamento
    """
    service = SessaoService(db)
    return service.get_sessoes_para_faturamento(convenio_id)
