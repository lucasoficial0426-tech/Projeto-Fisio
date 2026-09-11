from sqlalchemy.orm import Session
from ..models.fatura import Fatura, StatusFatura
from ..schemas.fatura import FaturaCreate, FaturaUpdate
from typing import List, Optional
from datetime import datetime
from fastapi import HTTPException


class FaturaService:
    def __init__(self, db: Session):
        self.db = db

    def create(self, fatura: FaturaCreate) -> Fatura:
        """
        Cria uma fatura para uma sessão de convênio:
        - RN-06: Sessão de convênio só pode ser faturada se tiver evolução clínica
        - RN-08: Atraso superior a 15 min bloqueia faturamento
        """
        from ..models.sessao import Sessao, TipoAtendimento
        from ..models.evolucao_clinica import EvolucaoClinica

        # Obter a sessão
        sessao = self.db.query(Sessao).filter(Sessao.id == fatura.sessao_id).first()
        if not sessao:
            raise HTTPException(status_code=404, detail="Sessão não encontrada")

        # RN-06: Verificar se tem evolução clínica
        tem_evolucao = self.db.query(EvolucaoClinica).filter(
            EvolucaoClinica.sessao_id == fatura.sessao_id
        ).first() is not None

        if not tem_evolucao:
            raise HTTPException(
                status_code=400,
                detail="RN-06: Sessão de convênio só pode ser faturada se tiver evolução clínica registrada"
            )

        # RN-08: Verificar se atendimento é reduzido
        if sessao.tipo_atendimento == TipoAtendimento.REDUZIDO:
            raise HTTPException(
                status_code=400,
                detail="RN-08: Atraso superior a 15 min bloqueia faturamento no convênio"
            )

        # Verificar se já existe fatura para esta sessão
        existente = self.db.query(Fatura).filter(Fatura.sessao_id == fatura.sessao_id).first()
        if existente:
            raise HTTPException(
                status_code=400,
                detail="Já existe uma fatura para esta sessão"
            )

        db_fatura = Fatura(
            sessao_id=fatura.sessao_id,
            lote_id=fatura.lote_id,
            convenio_id=fatura.convenio_id,
            valor=fatura.valor,
            status=StatusFatura.PENDENTE,
            observacoes=fatura.observacoes,
        )
        self.db.add(db_fatura)
        self.db.commit()
        self.db.refresh(db_fatura)
        return db_fatura

    def get_by_id(self, fatura_id: int) -> Optional[Fatura]:
        return self.db.query(Fatura).filter(Fatura.id == fatura_id).first()

    def get_by_sessao(self, sessao_id: int) -> Optional[Fatura]:
        return self.db.query(Fatura).filter(Fatura.sessao_id == sessao_id).first()

    def get_by_lote(self, lote_id: int) -> List[Fatura]:
        return self.db.query(Fatura).filter(Fatura.lote_id == lote_id).all()

    def get_all(self, skip: int = 0, limit: int = 100) -> List[Fatura]:
        return self.db.query(Fatura).offset(skip).limit(limit).all()

    def update(self, fatura_id: int, fatura: FaturaUpdate) -> Optional[Fatura]:
        db_fatura = self.get_by_id(fatura_id)
        if not db_fatura:
            return None

        if fatura.status is not None:
            db_fatura.status = fatura.status
        if fatura.observacoes is not None:
            db_fatura.observacoes = fatura.observacoes

        self.db.commit()
        self.db.refresh(db_fatura)
        return db_fatura

    def delete(self, fatura_id: int) -> bool:
        db_fatura = self.get_by_id(fatura_id)
        if not db_fatura:
            return False

        self.db.delete(db_fatura)
        self.db.commit()
        return True

    def faturar(self, fatura_id: int) -> Optional[Fatura]:
        """Marca uma fatura como faturada"""
        db_fatura = self.get_by_id(fatura_id)
        if not db_fatura:
            return None

        db_fatura.status = StatusFatura.FATURADO
        self.db.commit()
        self.db.refresh(db_fatura)
        return db_fatura

    def bloquear(self, fatura_id: int, motivo: str) -> Optional[Fatura]:
        """Bloqueia uma fatura"""
        db_fatura = self.get_by_id(fatura_id)
        if not db_fatura:
            return None

        db_fatura.status = StatusFatura.BLOQUEADO
        if db_fatura.observacoes:
            db_fatura.observacoes = f"{db_fatura.observacoes} | {motivo}"
        else:
            db_fatura.observacoes = motivo
        self.db.commit()
        self.db.refresh(db_fatura)
        return db_fatura

    def validar_faturamento(self, sessao_id: int) -> Tuple[bool, str]:
        """
        Valida se uma sessão pode ser faturada:
        - RN-06: Verifica se tem evolução clínica
        - RN-08: Verifica se não é atendimento reduzido
        Retorna (pode_faturar, mensagem)
        """
        from ..models.sessao import Sessao, TipoAtendimento
        from ..models.evolucao_clinica import EvolucaoClinica

        sessao = self.db.query(Sessao).filter(Sessao.id == sessao_id).first()
        if not sessao:
            return False, "Sessão não encontrada"

        # RN-06: Verificar evolução clínica
        tem_evolucao = self.db.query(EvolucaoClinica).filter(
            EvolucaoClinica.sessao_id == sessao_id
        ).first() is not None

        if not tem_evolucao:
            return False, "RN-06: Sessão de convênio só pode ser faturada se tiver evolução clínica registrada"

        # RN-08: Verificar atendimento reduzido
        if sessao.tipo_atendimento == TipoAtendimento.REDUZIDO:
            return False, "RN-08: Atraso superior a 15 min bloqueia faturamento no convênio"

        return True, "Sessão pode ser faturada"
