from sqlalchemy.orm import Session
from ..models.pacote import Pacote, StatusPacote
from ..schemas.pacote import PacoteCreate, PacoteUpdate
from typing import List, Optional
from datetime import date, timedelta


class PacoteService:
    def __init__(self, db: Session):
        self.db = db

    def create(self, pacote: PacoteCreate) -> Pacote:
        # RN-01: Pacote de 10 sessões expira 90 dias após a data de compra
        data_expiracao = pacote.data_compra + timedelta(days=90)

        db_pacote = Pacote(
            paciente_id=pacote.paciente_id,
            data_compra=pacote.data_compra,
            data_expiracao=data_expiracao,
            sessao_total=pacote.sessao_total,
            sessao_restante=pacote.sessao_restante,
            tipo_pagamento=pacote.tipo_pagamento,
            valor=pacote.valor,
            status=StatusPacote.ATIVO,
            convenio_id=pacote.convenio_id,
        )
        self.db.add(db_pacote)
        self.db.commit()
        self.db.refresh(db_pacote)
        return db_pacote

    def get_by_id(self, pacote_id: int) -> Optional[Pacote]:
        return self.db.query(Pacote).filter(Pacote.id == pacote_id).first()

    def get_by_paciente(self, paciente_id: int) -> List[Pacote]:
        return self.db.query(Pacote).filter(Pacote.paciente_id == paciente_id).all()

    def get_all(self, skip: int = 0, limit: int = 100) -> List[Pacote]:
        return self.db.query(Pacote).offset(skip).limit(limit).all()

    def update(self, pacote_id: int, pacote: PacoteUpdate) -> Optional[Pacote]:
        db_pacote = self.get_by_id(pacote_id)
        if not db_pacote:
            return None

        if pacote.sessao_restante is not None:
            db_pacote.sessao_restante = pacote.sessao_restante
            # Atualiza status com base no saldo
            self._atualizar_status(db_pacote)
        if pacote.status is not None:
            db_pacote.status = pacote.status

        self.db.commit()
        self.db.refresh(db_pacote)
        return db_pacote

    def delete(self, pacote_id: int) -> bool:
        db_pacote = self.get_by_id(pacote_id)
        if not db_pacote:
            return False

        self.db.delete(db_pacote)
        self.db.commit()
        return True

    def _atualizar_status(self, pacote: Pacote) -> None:
        """Atualiza o status do pacote com base na data de expiração e saldo (RN-01, RN-07)"""
        if pacote.data_expiracao < date.today():
            pacote.status = StatusPacote.EXPIRADO
        elif pacote.sessao_restante == 0:
            pacote.status = StatusPacote.UTILIZADO
        else:
            pacote.status = StatusPacote.ATIVO

    def consumir_sessao(self, pacote_id: int) -> bool:
        """Consome uma sessão do pacote (RN-02, RN-07)"""
        db_pacote = self.get_by_id(pacote_id)
        if not db_pacote:
            return False

        if db_pacote.sessao_restante <= 0:
            return False

        db_pacote.sessao_restante -= 1
        self._atualizar_status(db_pacote)
        self.db.commit()
        self.db.refresh(db_pacote)
        return True

    def validar_pacote_para_agendamento(self, pacote_id: int) -> bool:
        """
        RN-07: Paciente particular com pacote expirado ou saldo zerado não pode ser agendado
        """
        db_pacote = self.get_by_id(pacote_id)
        if not db_pacote:
            return False

        # Pacotes de convênio não precisam ser validados aqui (faturamento é validado separadamente)
        if db_pacote.tipo_pagamento == "PARTICULAR":
            if db_pacote.data_expiracao < date.today():
                return False
            if db_pacote.sessao_restante <= 0:
                return False

        return True

    def get_pacotes_proximos_expirar(self, dias: int = 30) -> List[Pacote]:
        """Retorna pacotes que irão expirar nos próximos dias (RN-01)"""
        data_limite = date.today() + timedelta(days=dias)
        return (
            self.db.query(Pacote)
            .filter(
                Pacote.data_expiracao >= date.today(),
                Pacote.data_expiracao <= data_limite,
                Pacote.status == StatusPacote.ATIVO,
            )
            .all()
        )
