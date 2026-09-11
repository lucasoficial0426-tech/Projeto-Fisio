from sqlalchemy.orm import Session
from ..models.lote import Lote, StatusLote
from ..schemas.lote import LoteCreate, LoteUpdate
from typing import List, Optional
from datetime import datetime


class LoteService:
    def __init__(self, db: Session):
        self.db = db

    def create(self, lote: LoteCreate) -> Lote:
        """Cria um novo lote de faturamento"""
        db_lote = Lote(
            convenio_id=lote.convenio_id,
            status=lote.status,
            valor_total=lote.valor_total,
            observacoes=lote.observacoes,
        )
        self.db.add(db_lote)
        self.db.commit()
        self.db.refresh(db_lote)
        return db_lote

    def get_by_id(self, lote_id: int) -> Optional[Lote]:
        return self.db.query(Lote).filter(Lote.id == lote_id).first()

    def get_by_convenio(self, convenio_id: int) -> List[Lote]:
        return self.db.query(Lote).filter(Lote.convenio_id == convenio_id).all()

    def get_all(self, skip: int = 0, limit: int = 100) -> List[Lote]:
        return self.db.query(Lote).offset(skip).limit(limit).all()

    def update(self, lote_id: int, lote: LoteUpdate) -> Optional[Lote]:
        db_lote = self.get_by_id(lote_id)
        if not db_lote:
            return None

        if lote.data_fechamento is not None:
            db_lote.data_fechamento = lote.data_fechamento
        if lote.data_faturamento is not None:
            db_lote.data_faturamento = lote.data_faturamento
        if lote.status is not None:
            db_lote.status = lote.status
        if lote.valor_total is not None:
            db_lote.valor_total = lote.valor_total
        if lote.observacoes is not None:
            db_lote.observacoes = lote.observacoes

        self.db.commit()
        self.db.refresh(db_lote)
        return db_lote

    def delete(self, lote_id: int) -> bool:
        db_lote = self.get_by_id(lote_id)
        if not db_lote:
            return False

        self.db.delete(db_lote)
        self.db.commit()
        return True

    def fechar_lote(self, lote_id: int) -> Optional[Lote]:
        """Fecha um lote para faturamento"""
        db_lote = self.get_by_id(lote_id)
        if not db_lote:
            return None

        db_lote.status = StatusLote.FECHADO
        db_lote.data_fechamento = datetime.now()
        self.db.commit()
        self.db.refresh(db_lote)
        return db_lote

    def faturar_lote(self, lote_id: int) -> Optional[Lote]:
        """Marca um lote como faturado"""
        db_lote = self.get_by_id(lote_id)
        if not db_lote:
            return None

        db_lote.status = StatusLote.FATURADO
        db_lote.data_faturamento = datetime.now()
        self.db.commit()
        self.db.refresh(db_lote)
        return db_lote
