from sqlalchemy.orm import Session
from ..models.falta import Falta
from ..schemas.falta import FaltaCreate, FaltaUpdate
from typing import List, Optional
from datetime import datetime


class FaltaService:
    def __init__(self, db: Session):
        self.db = db

    def create(self, falta: FaltaCreate) -> Falta:
        """
        Registra uma falta e atualiza o pacote do paciente (RN-02, RN-03):
        - RN-02: Falta sem aviso com antecedência de 24h consome uma sessão do pacote
        - RN-03: Falta avisada com 24h ou mais de antecedência não consome sessão
        """
        from .pacote_service import PacoteService

        db_falta = Falta(
            sessao_id=falta.sessao_id,
            avisado=falta.avisado,
            antecedencia_horas=falta.antecedencia_horas,
            justificativa=falta.justificativa,
        )
        self.db.add(db_falta)
        self.db.commit()
        self.db.refresh(db_falta)

        # RN-02 e RN-03: Consumir sessão do pacote se não foi avisado com 24h de antecedência
        if not falta.avisado and falta.antecedencia_horas < 24:
            # Obter a sessão para encontrar o pacote
            from ..models.sessao import Sessao
            sessao = self.db.query(Sessao).filter(Sessao.id == falta.sessao_id).first()
            if sessao and sessao.pacote_id:
                pacote_service = PacoteService(self.db)
                pacote_service.consumir_sessao(sessao.pacote_id)

        return db_falta

    def get_by_id(self, falta_id: int) -> Optional[Falta]:
        return self.db.query(Falta).filter(Falta.id == falta_id).first()

    def get_by_sessao(self, sessao_id: int) -> Optional[Falta]:
        return self.db.query(Falta).filter(Falta.sessao_id == sessao_id).first()

    def get_all(self, skip: int = 0, limit: int = 100) -> List[Falta]:
        return self.db.query(Falta).offset(skip).limit(limit).all()

    def update(self, falta_id: int, falta: FaltaUpdate) -> Optional[Falta]:
        db_falta = self.get_by_id(falta_id)
        if not db_falta:
            return None

        if falta.avisado is not None:
            db_falta.avisado = falta.avisado
        if falta.antecedencia_horas is not None:
            db_falta.antecedencia_horas = falta.antecedencia_horas
        if falta.justificativa is not None:
            db_falta.justificativa = falta.justificativa

        self.db.commit()
        self.db.refresh(db_falta)
        return db_falta

    def delete(self, falta_id: int) -> bool:
        db_falta = self.get_by_id(falta_id)
        if not db_falta:
            return False

        self.db.delete(db_falta)
        self.db.commit()
        return True
