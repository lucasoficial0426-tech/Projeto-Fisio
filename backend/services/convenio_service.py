from sqlalchemy.orm import Session
from ..models.convenio import Convenio
from ..schemas.convenio import ConvenioCreate, ConvenioUpdate
from typing import List, Optional
from datetime import date


class ConvenioService:
    def __init__(self, db: Session):
        self.db = db

    def create(self, convenio: ConvenioCreate) -> Convenio:
        db_convenio = Convenio(
            nome=convenio.nome,
            cnpj=convenio.cnpj,
            telefone=convenio.telefone,
            email=convenio.email,
            endereco=convenio.endereco,
            taxa_desconto=convenio.taxa_desconto,
            data_contrato=convenio.data_contrato,
            ativo=convenio.ativo,
        )
        self.db.add(db_convenio)
        self.db.commit()
        self.db.refresh(db_convenio)
        return db_convenio

    def get_by_id(self, convenio_id: int) -> Optional[Convenio]:
        return self.db.query(Convenio).filter(Convenio.id == convenio_id).first()

    def get_by_cnpj(self, cnpj: str) -> Optional[Convenio]:
        return self.db.query(Convenio).filter(Convenio.cnpj == cnpj).first()

    def get_all(self, skip: int = 0, limit: int = 100) -> List[Convenio]:
        return self.db.query(Convenio).offset(skip).limit(limit).all()

    def update(self, convenio_id: int, convenio: ConvenioUpdate) -> Optional[Convenio]:
        db_convenio = self.get_by_id(convenio_id)
        if not db_convenio:
            return None

        if convenio.nome is not None:
            db_convenio.nome = convenio.nome
        if convenio.cnpj is not None:
            db_convenio.cnpj = convenio.cnpj
        if convenio.telefone is not None:
            db_convenio.telefone = convenio.telefone
        if convenio.email is not None:
            db_convenio.email = convenio.email
        if convenio.endereco is not None:
            db_convenio.endereco = convenio.endereco
        if convenio.taxa_desconto is not None:
            db_convenio.taxa_desconto = convenio.taxa_desconto
        if convenio.data_contrato is not None:
            db_convenio.data_contrato = convenio.data_contrato
        if convenio.ativo is not None:
            db_convenio.ativo = convenio.ativo

        self.db.commit()
        self.db.refresh(db_convenio)
        return db_convenio

    def delete(self, convenio_id: int) -> bool:
        db_convenio = self.get_by_id(convenio_id)
        if not db_convenio:
            return False

        self.db.delete(db_convenio)
        self.db.commit()
        return True
