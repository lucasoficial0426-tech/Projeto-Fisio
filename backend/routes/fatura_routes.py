from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List
from ..database import get_db
from ..schemas.fatura import FaturaCreate, FaturaUpdate, FaturaResponse
from ..services.fatura_service import FaturaService

router = APIRouter()


@router.post("/", response_model=FaturaResponse, status_code=status.HTTP_201_CREATED)
def create_fatura(fatura: FaturaCreate, db: Session = Depends(get_db)):
    """
    Cria uma fatura para uma sessão de convênio:
    - RN-06: Sessão de convênio só pode ser faturada se tiver evolução clínica
    - RN-08: Atraso superior a 15 min bloqueia faturamento
    """
    service = FaturaService(db)
    return service.create(fatura)


@router.get("/{fatura_id}", response_model=FaturaResponse)
def read_fatura(fatura_id: int, db: Session = Depends(get_db)):
    """Obtém uma fatura pelo ID"""
    service = FaturaService(db)
    fatura = service.get_by_id(fatura_id)
    if not fatura:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Fatura não encontrada"
        )
    return fatura


@router.get("/", response_model=List[FaturaResponse])
def read_all_faturas(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    """Lista todas as faturas"""
    service = FaturaService(db)
    return service.get_all(skip, limit)


@router.get("/sessao/{sessao_id}", response_model=FaturaResponse)
def read_fatura_by_sessao(sessao_id: int, db: Session = Depends(get_db)):
    """Obtém a fatura de uma sessão"""
    service = FaturaService(db)
    fatura = service.get_by_sessao(sessao_id)
    if not fatura:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Fatura não encontrada para esta sessão"
        )
    return fatura


@router.get("/lote/{lote_id}", response_model=List[FaturaResponse])
def read_faturas_by_lote(lote_id: int, db: Session = Depends(get_db)):
    """Lista todas as faturas de um lote"""
    service = FaturaService(db)
    return service.get_by_lote(lote_id)


@router.put("/{fatura_id}", response_model=FaturaResponse)
def update_fatura(fatura_id: int, fatura: FaturaUpdate, db: Session = Depends(get_db)):
    """Atualiza uma fatura"""
    service = FaturaService(db)
    updated_fatura = service.update(fatura_id, fatura)
    if not updated_fatura:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Fatura não encontrada"
        )
    return updated_fatura


@router.delete("/{fatura_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_fatura(fatura_id: int, db: Session = Depends(get_db)):
    """Deleta uma fatura"""
    service = FaturaService(db)
    if not service.delete(fatura_id):
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Fatura não encontrada"
        )
    return None


@router.post("/{fatura_id}/faturar/", response_model=FaturaResponse)
def faturar_fatura(fatura_id: int, db: Session = Depends(get_db)):
    """Marca uma fatura como faturada"""
    service = FaturaService(db)
    fatura = service.faturar(fatura_id)
    if not fatura:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Fatura não encontrada"
        )
    return fatura


@router.post("/{fatura_id}/bloquear/", response_model=FaturaResponse)
def bloquear_fatura(fatura_id: int, motivo: str = "", db: Session = Depends(get_db)):
    """Bloqueia uma fatura"""
    service = FaturaService(db)
    fatura = service.bloquear(fatura_id, motivo)
    if not fatura:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Fatura não encontrada"
        )
    return fatura


@router.get("/validar/{sessao_id}", response_model=dict)
def validar_faturamento(sessao_id: int, db: Session = Depends(get_db)):
    """
    Valida se uma sessão pode ser faturada:
    - RN-06: Verifica se tem evolução clínica
    - RN-08: Verifica se não é atendimento reduzido
    """
    service = FaturaService(db)
    pode_faturar, mensagem = service.validar_faturamento(sessao_id)
    
    return {
        "pode_faturar": pode_faturar,
        "mensagem": mensagem
    }
