from sqlalchemy.orm import Session
from ..models.sessao import Sessao, StatusSessao, TipoAtendimento
from ..schemas.sessao import SessaoCreate, SessaoUpdate
from typing import List, Optional, Tuple
from datetime import datetime, timedelta
from fastapi import HTTPException


class SessaoService:
    def __init__(self, db: Session):
        self.db = db

    def create(self, sessao: SessaoCreate) -> Sessao:
        """
        Cria uma nova sessão validando todas as regras de negócio:
        - RN-04: Sala não pode ter mais sessões do que sua capacidade
        - RN-05: Profissional não pode ter duas sessões no mesmo horário
        - RN-07: Paciente particular com pacote expirado ou saldo zerado não pode ser agendado
        - RN-08: Atraso superior a 15 min registra atendimento reduzido
        """
        from .pacote_service import PacoteService
        from .sala_service import SalaService
        from .profissional_service import ProfissionalService

        # Validar conflitos de sala (RN-04)
        sala_service = SalaService(self.db)
        if not sala_service.verificar_capacidade_sala(
            sessao.sala_id, sessao.data_hora_inicio, sessao.data_hora_fim
        ):
            raise HTTPException(
                status_code=400,
                detail="RN-04: Sala não pode receber mais sessões simultâneas do que sua capacidade"
            )

        # Validar conflitos de profissional (RN-05)
        profissional_service = ProfissionalService(self.db)
        profissionais_disponiveis = profissional_service.get_profissionais_disponiveis(
            sessao.data_hora_inicio, sessao.data_hora_fim
        )
        if sessao.profissional_id not in [p.id for p in profissionais_disponiveis]:
            raise HTTPException(
                status_code=400,
                detail="RN-05: Profissional não pode ter duas sessões no mesmo horário"
            )

        # Validar pacote do paciente (RN-07)
        if sessao.pacote_id:
            pacote_service = PacoteService(self.db)
            if not pacote_service.validar_pacote_para_agendamento(sessao.pacote_id):
                raise HTTPException(
                    status_code=400,
                    detail="RN-07: Paciente particular com pacote expirado ou saldo zerado não pode ser agendado"
                )

        # RN-08: Verificar se há atraso > 15 min
        tipo_atendimento = TipoAtendimento.NORMAL
        if sessao.atraso_minutos > 15:
            tipo_atendimento = TipoAtendimento.REDUZIDO

        db_sessao = Sessao(
            paciente_id=sessao.paciente_id,
            profissional_id=sessao.profissional_id,
            sala_id=sessao.sala_id,
            pacote_id=sessao.pacote_id,
            convenio_id=sessao.convenio_id,
            data_hora_inicio=sessao.data_hora_inicio,
            data_hora_fim=sessao.data_hora_fim,
            status=sessao.status,
            tipo_atendimento=tipo_atendimento,
            observacoes=sessao.observacoes,
            atraso_minutos=sessao.atraso_minutos,
        )
        self.db.add(db_sessao)
        self.db.commit()
        self.db.refresh(db_sessao)
        return db_sessao

    def get_by_id(self, sessao_id: int) -> Optional[Sessao]:
        return self.db.query(Sessao).filter(Sessao.id == sessao_id).first()

    def get_all(self, skip: int = 0, limit: int = 100) -> List[Sessao]:
        return self.db.query(Sessao).offset(skip).limit(limit).all()

    def get_by_paciente(self, paciente_id: int) -> List[Sessao]:
        return self.db.query(Sessao).filter(Sessao.paciente_id == paciente_id).all()

    def get_by_profissional(self, profissional_id: int) -> List[Sessao]:
        return self.db.query(Sessao).filter(Sessao.profissional_id == profissional_id).all()

    def get_by_sala(self, sala_id: int) -> List[Sessao]:
        return self.db.query(Sessao).filter(Sessao.sala_id == sala_id).all()

    def get_by_data(self, data: datetime.date) -> List[Sessao]:
        return (
            self.db.query(Sessao)
            .filter(
                Sessao.data_hora_inicio >= datetime(data.year, data.month, data.day),
                Sessao.data_hora_inicio < datetime(data.year, data.month, data.day) + timedelta(days=1),
            )
            .all()
        )

    def update(self, sessao_id: int, sessao: SessaoUpdate) -> Optional[Sessao]:
        db_sessao = self.get_by_id(sessao_id)
        if not db_sessao:
            return None

        if sessao.status is not None:
            db_sessao.status = sessao.status
        if sessao.tipo_atendimento is not None:
            db_sessao.tipo_atendimento = sessao.tipo_atendimento
        if sessao.observacoes is not None:
            db_sessao.observacoes = sessao.observacoes
        if sessao.atraso_minutos is not None:
            db_sessao.atraso_minutos = sessao.atraso_minutos
            # RN-08: Se atraso > 15 min, deve ser atendimento reduzido
            if db_sessao.atraso_minutos > 15 and db_sessao.tipo_atendimento != TipoAtendimento.REDUZIDO:
                db_sessao.tipo_atendimento = TipoAtendimento.REDUZIDO

        self.db.commit()
        self.db.refresh(db_sessao)
        return db_sessao

    def delete(self, sessao_id: int) -> bool:
        db_sessao = self.get_by_id(sessao_id)
        if not db_sessao:
            return False

        self.db.delete(db_sessao)
        self.db.commit()
        return True

    def confirmar_sessao(self, sessao_id: int) -> Optional[Sessao]:
        """Confirma uma sessão agendada"""
        db_sessao = self.get_by_id(sessao_id)
        if not db_sessao:
            return None

        db_sessao.status = StatusSessao.CONFIRMADO
        self.db.commit()
        self.db.refresh(db_sessao)
        return db_sessao

    def realizar_sessao(self, sessao_id: int) -> Optional[Sessao]:
        """Marca uma sessão como realizada"""
        db_sessao = self.get_by_id(sessao_id)
        if not db_sessao:
            return None

        db_sessao.status = StatusSessao.REALIZADO
        self.db.commit()
        self.db.refresh(db_sessao)
        return db_sessao

    def cancelar_sessao(self, sessao_id: int) -> Optional[Sessao]:
        """Cancela uma sessão"""
        db_sessao = self.get_by_id(sessao_id)
        if not db_sessao:
            return None

        db_sessao.status = StatusSessao.CANCELADO
        self.db.commit()
        self.db.refresh(db_sessao)
        return db_sessao

    def verificar_conflitos(self, paciente_id: int, profissional_id: int, sala_id: int,
                           data_hora_inicio: datetime, data_hora_fim: datetime) -> Tuple[bool, str]:
        """
        Verifica conflitos para agendamento:
        - RN-04: Sala
        - RN-05: Profissional
        Retorna (tem_conflito, mensagem)
        """
        from ..models.sessao import Sessao

        # Verificar conflitos de sala
        conflitos_sala = self.db.query(Sessao).filter(
            Sessao.sala_id == sala_id,
            Sessao.data_hora_inicio < data_hora_fim,
            Sessao.data_hora_fim > data_hora_inicio,
        ).count()

        from .sala_service import SalaService
        sala_service = SalaService(self.db)
        sala = sala_service.get_by_id(sala_id)
        if sala and conflitos_sala >= sala.capacidade:
            return True, "RN-04: Sala não pode receber mais sessões simultâneas do que sua capacidade"

        # Verificar conflitos de profissional
        conflitos_profissional = self.db.query(Sessao).filter(
            Sessao.profissional_id == profissional_id,
            Sessao.data_hora_inicio < data_hora_fim,
            Sessao.data_hora_fim > data_hora_inicio,
        ).count()

        if conflitos_profissional > 0:
            return True, "RN-05: Profissional não pode ter duas sessões no mesmo horário"

        return False, ""

    def get_sessoes_para_faturamento(self, convenio_id: int) -> List[Sessao]:
        """
        Retorna sessões de convênio que podem ser faturadas:
        - RN-06: Sessão de convênio só pode ser faturada se tiver evolução clínica
        - RN-08: Atraso superior a 15 min bloqueia faturamento
        """
        from ..models.evolucao_clinica import EvolucaoClinica

        return (
            self.db.query(Sessao)
            .join(EvolucaoClinica, Sessao.id == EvolucaoClinica.sessao_id)
            .filter(
                Sessao.convenio_id == convenio_id,
                Sessao.status == StatusSessao.REALIZADO,
                Sessao.tipo_atendimento != TipoAtendimento.REDUZIDO,
            )
            .all()
        )
