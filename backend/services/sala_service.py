from sqlalchemy.orm import Session
from ..models.sala import Sala
from ..schemas.sala import SalaCreate, SalaUpdate
from typing import List, Optional


class SalaService:
    def __init__(self, db: Session):
        self.db = db

    def create(self, sala: SalaCreate) -> Sala:
        db_sala = Sala(
            nome=sala.nome,
            descricao=sala.descricao,
            capacidade=sala.capacidade,
            localizacao=sala.localizacao,
            ativo=sala.ativo,
        )
        self.db.add(db_sala)
        self.db.commit()
        self.db.refresh(db_sala)
        return db_sala

    def get_by_id(self, sala_id: int) -> Optional[Sala]:
        return self.db.query(Sala).filter(Sala.id == sala_id).first()

    def get_all(self, skip: int = 0, limit: int = 100) -> List[Sala]:
        return self.db.query(Sala).offset(skip).limit(limit).all()

    def update(self, sala_id: int, sala: SalaUpdate) -> Optional[Sala]:
        db_sala = self.get_by_id(sala_id)
        if not db_sala:
            return None

        if sala.nome is not None:
            db_sala.nome = sala.nome
        if sala.descricao is not None:
            db_sala.descricao = sala.descricao
        if sala.capacidade is not None:
            db_sala.capacidade = sala.capacidade
        if sala.localizacao is not None:
            db_sala.localizacao = sala.localizacao
        if sala.ativo is not None:
            db_sala.ativo = sala.ativo

        self.db.commit()
        self.db.refresh(db_sala)
        return db_sala

    def delete(self, sala_id: int) -> bool:
        db_sala = self.get_by_id(sala_id)
        if not db_sala:
            return False

        self.db.delete(db_sala)
        self.db.commit()
        return True

    def get_salas_disponiveis(self, data_hora_inicio, data_hora_fim, capacidade_minima: int = 1) -> List[Sala]:
        """Retorna salas disponíveis em um determinado horário com capacidade (RN-04)"""
        from sqlalchemy import func
        from ..models.sessao import Sessao

        # Conta quantas sessões cada sala tem no horário solicitado
        subquery = (
            self.db.query(
                Sessao.sala_id,
                func.count(Sessao.id).label("count_sessoes"),
            )
            .filter(
                Sessao.data_hora_inicio < data_hora_fim,
                Sessao.data_hora_fim > data_hora_inicio,
            )
            .group_by(Sessao.sala_id)
            .subquery()
        )

        # Salas onde a contagem de sessões é menor que a capacidade
        return (
            self.db.query(Sala)
            .outerjoin(
                subquery,
                Sala.id == subquery.c.sala_id,
            )
            .filter(
                (subquery.c.count_sessoes.is_(None) | (subquery.c.count_sessoes < Sala.capacidade)),
                Sala.capacidade >= capacidade_minima,
                Sala.ativo == True,
            )
            .all()
        )

    def verificar_capacidade_sala(self, sala_id: int, data_hora_inicio, data_hora_fim) -> bool:
        """Verifica se uma sala tem capacidade para mais uma sessão no horário (RN-04)"""
        from ..models.sessao import Sessao

        sala = self.get_by_id(sala_id)
        if not sala:
            return False

        count = (
            self.db.query(Sessao)
            .filter(
                Sessao.sala_id == sala_id,
                Sessao.data_hora_inicio < data_hora_fim,
                Sessao.data_hora_fim > data_hora_inicio,
            )
            .count()
        )

        return count < sala.capacidade
