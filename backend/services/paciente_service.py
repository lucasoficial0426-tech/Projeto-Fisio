from sqlalchemy.orm import Session
from ..models.paciente import Paciente
from ..schemas.paciente import PacienteCreate, PacienteUpdate
from typing import List, Optional
from datetime import date


class PacienteService:
    def __init__(self, db: Session):
        self.db = db

    def create(self, paciente: PacienteCreate) -> Paciente:
        db_paciente = Paciente(
            nome=paciente.nome,
            cpf=paciente.cpf,
            data_nascimento=paciente.data_nascimento,
            telefone=paciente.telefone,
            email=paciente.email,
            endereco=paciente.endereco,
            convenio_id=paciente.convenio_id,
            ativo=paciente.ativo,
        )
        self.db.add(db_paciente)
        self.db.commit()
        self.db.refresh(db_paciente)
        return db_paciente

    def get_by_id(self, paciente_id: int) -> Optional[Paciente]:
        return self.db.query(Paciente).filter(Paciente.id == paciente_id).first()

    def get_by_cpf(self, cpf: str) -> Optional[Paciente]:
        return self.db.query(Paciente).filter(Paciente.cpf == cpf).first()

    def get_all(self, skip: int = 0, limit: int = 100) -> List[Paciente]:
        return self.db.query(Paciente).offset(skip).limit(limit).all()

    def update(self, paciente_id: int, paciente: PacienteUpdate) -> Optional[Paciente]:
        db_paciente = self.get_by_id(paciente_id)
        if not db_paciente:
            return None

        if paciente.nome is not None:
            db_paciente.nome = paciente.nome
        if paciente.cpf is not None:
            db_paciente.cpf = paciente.cpf
        if paciente.data_nascimento is not None:
            db_paciente.data_nascimento = paciente.data_nascimento
        if paciente.telefone is not None:
            db_paciente.telefone = paciente.telefone
        if paciente.email is not None:
            db_paciente.email = paciente.email
        if paciente.endereco is not None:
            db_paciente.endereco = paciente.endereco
        if paciente.convenio_id is not None:
            db_paciente.convenio_id = paciente.convenio_id
        if paciente.ativo is not None:
            db_paciente.ativo = paciente.ativo

        self.db.commit()
        self.db.refresh(db_paciente)
        return db_paciente

    def delete(self, paciente_id: int) -> bool:
        db_paciente = self.get_by_id(paciente_id)
        if not db_paciente:
            return False

        self.db.delete(db_paciente)
        self.db.commit()
        return True

    def get_pacientes_com_pacotes_ativos(self) -> List[Paciente]:
        """Retorna pacientes com pacotes ativos (não expirados e com saldo)"""
        from ..models.pacote import Pacote
        from datetime import date

        return (
            self.db.query(Paciente)
            .join(Pacote, Paciente.id == Pacote.paciente_id)
            .filter(
                Pacote.data_expiracao >= date.today(),
                Pacote.sessao_restante > 0,
                Pacote.status == "ATIVO",
            )
            .distinct()
            .all()
        )
