from sqlalchemy.orm import Session
from ..models.evolucao_clinica import EvolucaoClinica
from ..schemas.evolucao_clinica import EvolucaoClinicaCreate, EvolucaoClinicaUpdate
from typing import List, Optional
from datetime import datetime


class EvolucaoClinicaService:
    def __init__(self, db: Session):
        self.db = db

    def create(self, evolucao: EvolucaoClinicaCreate) -> EvolucaoClinica:
        """
        Cria um registro de evolução clínica para uma sessão
        """
        db_evolucao = EvolucaoClinica(
            sessao_id=evolucao.sessao_id,
            profissional_id=evolucao.profissional_id,
            descricao=evolucao.descricao,
            objetivos=evolucao.objetivos,
            conduta=evolucao.conduta,
        )
        self.db.add(db_evolucao)
        self.db.commit()
        self.db.refresh(db_evolucao)
        return db_evolucao

    def get_by_id(self, evolucao_id: int) -> Optional[EvolucaoClinica]:
        return self.db.query(EvolucaoClinica).filter(EvolucaoClinica.id == evolucao_id).first()

    def get_by_sessao(self, sessao_id: int) -> Optional[EvolucaoClinica]:
        return self.db.query(EvolucaoClinica).filter(EvolucaoClinica.sessao_id == sessao_id).first()

    def get_all(self, skip: int = 0, limit: int = 100) -> List[EvolucaoClinica]:
        return self.db.query(EvolucaoClinica).offset(skip).limit(limit).all()

    def update(self, evolucao_id: int, evolucao: EvolucaoClinicaUpdate) -> Optional[EvolucaoClinica]:
        db_evolucao = self.get_by_id(evolucao_id)
        if not db_evolucao:
            return None

        if evolucao.descricao is not None:
            db_evolucao.descricao = evolucao.descricao
        if evolucao.objetivos is not None:
            db_evolucao.objetivos = evolucao.objetivos
        if evolucao.conduta is not None:
            db_evolucao.conduta = evolucao.conduta

        self.db.commit()
        self.db.refresh(db_evolucao)
        return db_evolucao

    def delete(self, evolucao_id: int) -> bool:
        db_evolucao = self.get_by_id(evolucao_id)
        if not db_evolucao:
            return False

        self.db.delete(db_evolucao)
        self.db.commit()
        return True

    def tem_evolucao(self, sessao_id: int) -> bool:
        """Verifica se uma sessão tem evolução clínica registrada (RN-06)"""
        return self.get_by_sessao(sessao_id) is not None
