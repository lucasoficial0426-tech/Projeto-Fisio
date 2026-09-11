from sqlalchemy.orm import Session
from ..models.profissional import Profissional
from ..schemas.profissional import ProfissionalCreate, ProfissionalUpdate
from typing import List, Optional


class ProfissionalService:
    def __init__(self, db: Session):
        self.db = db

    def create(self, profissional: ProfissionalCreate) -> Profissional:
        db_profissional = Profissional(
            nome=profissional.nome,
            cpf=profissional.cpf,
            crf=profissional.crf,
            especialidade=profissional.especialidade,
            telefone=profissional.telefone,
            email=profissional.email,
            ativo=profissional.ativo,
        )
        self.db.add(db_profissional)
        self.db.commit()
        self.db.refresh(db_profissional)
        return db_profissional

    def get_by_id(self, profissional_id: int) -> Optional[Profissional]:
        return self.db.query(Profissional).filter(Profissional.id == profissional_id).first()

    def get_by_cpf(self, cpf: str) -> Optional[Profissional]:
        return self.db.query(Profissional).filter(Profissional.cpf == cpf).first()

    def get_by_crf(self, crf: str) -> Optional[Profissional]:
        return self.db.query(Profissional).filter(Profissional.crf == crf).first()

    def get_all(self, skip: int = 0, limit: int = 100) -> List[Profissional]:
        return self.db.query(Profissional).offset(skip).limit(limit).all()

    def update(self, profissional_id: int, profissional: ProfissionalUpdate) -> Optional[Profissional]:
        db_profissional = self.get_by_id(profissional_id)
        if not db_profissional:
            return None

        if profissional.nome is not None:
            db_profissional.nome = profissional.nome
        if profissional.cpf is not None:
            db_profissional.cpf = profissional.cpf
        if profissional.crf is not None:
            db_profissional.crf = profissional.crf
        if profissional.especialidade is not None:
            db_profissional.especialidade = profissional.especialidade
        if profissional.telefone is not None:
            db_profissional.telefone = profissional.telefone
        if profissional.email is not None:
            db_profissional.email = profissional.email
        if profissional.ativo is not None:
            db_profissional.ativo = profissional.ativo

        self.db.commit()
        self.db.refresh(db_profissional)
        return db_profissional

    def delete(self, profissional_id: int) -> bool:
        db_profissional = self.get_by_id(profissional_id)
        if not db_profissional:
            return False

        self.db.delete(db_profissional)
        self.db.commit()
        return True

    def get_profissionais_disponiveis(self, data_hora_inicio, data_hora_fim) -> List[Profissional]:
        """Retorna profissionais disponíveis em um determinado horário (RN-05)"""
        from ..models.sessao import Sessao

        # Profissionais que NÃO têm sessões no horário solicitado
        subquery = (
            self.db.query(Sessao.profissional_id)
            .filter(
                Sessao.data_hora_inicio < data_hora_fim,
                Sessao.data_hora_fim > data_hora_inicio,
            )
            .subquery()
        )

        return (
            self.db.query(Profissional)
            .filter(
                Profissional.id.notin_(subquery),
                Profissional.ativo == True,
            )
            .all()
        )
