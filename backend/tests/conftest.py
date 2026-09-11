import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from datetime import date, datetime, timedelta

import sys
import os

# Adiciona o diretório backend ao path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from backend.main import app
from backend.database import get_db, Base
from backend.models.paciente import Paciente
from backend.models.profissional import Profissional
from backend.models.sala import Sala
from backend.models.convenio import Convenio
from backend.models.pacote import Pacote
from backend.models.sessao import Sessao
from backend.models.evolucao_clinica import EvolucaoClinica
from backend.models.falta import Falta
from backend.models.lote import Lote
from backend.models.fatura import Fatura

# Configuração do banco de dados de teste
SQLALCHEMY_DATABASE_URL = "sqlite:///./test.db"

engine = create_engine(
    SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False}
)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Cria todas as tabelas
Base.metadata.create_all(bind=engine)


# Fixture para o cliente de teste
@pytest.fixture
def client():
    return TestClient(app)


# Fixture para a sessão do banco de dados
@pytest.fixture
def db_session():
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()


# Fixture para limpar o banco de dados antes de cada teste
@pytest.fixture(autouse=True)
def clean_db(db_session):
    # Deleta todos os dados em ordem inversa para evitar problemas de FK
    db_session.query(Fatura).delete()
    db_session.query(Falta).delete()
    db_session.query(EvolucaoClinica).delete()
    db_session.query(Sessao).delete()
    db_session.query(Lote).delete()
    db_session.query(Pacote).delete()
    db_session.query(Paciente).delete()
    db_session.query(Profissional).delete()
    db_session.query(Sala).delete()
    db_session.query(Convenio).delete()
    db_session.commit()
    yield


# Fixture para criar dados de teste
@pytest.fixture
def setup_test_data(db_session):
    # Convênio
    convenio = Convenio(
        nome="Unimed Teste",
        cnpj="00.000.000/0001-00",
        telefone="(11) 1234-5678",
        email="teste@unimed.com",
        endereco="Rua Teste, 123",
        taxa_desconto=10.0,
        data_contrato=date(2023, 1, 1),
        ativo=True
    )
    db_session.add(convenio)
    db_session.commit()

    # Paciente com convênio
    paciente_convenio = Paciente(
        nome="João Silva",
        cpf="111.111.111-11",
        data_nascimento=date(1980, 1, 1),
        telefone="(11) 99999-9999",
        email="joao@email.com",
        endereco="Rua A, 123",
        convenio_id=convenio.id,
        ativo=True
    )
    db_session.add(paciente_convenio)
    db_session.commit()

    # Paciente particular
    paciente_particular = Paciente(
        nome="Maria Santos",
        cpf="222.222.222-22",
        data_nascimento=date(1990, 5, 15),
        telefone="(11) 88888-8888",
        email="maria@email.com",
        endereco="Rua B, 456",
        convenio_id=None,
        ativo=True
    )
    db_session.add(paciente_particular)
    db_session.commit()

    # Profissional
    profissional = Profissional(
        nome="Dr. Carlos Oliveira",
        cpf="333.333.333-33",
        crf="CRF-12345",
        especialidade="Fisioterapia Ortopédica",
        telefone="(11) 77777-7777",
        email="carlos@email.com",
        ativo=True
    )
    db_session.add(profissional)
    db_session.commit()

    # Sala
    sala = Sala(
        nome="Sala 1",
        descricao="Sala de atendimento individual",
        capacidade=1,
        localizacao="Andar 1",
        ativo=True
    )
    db_session.add(sala)
    db_session.commit()

    # Pacote para paciente particular (ativo)
    pacote_ativo = Pacote(
        paciente_id=paciente_particular.id,
        data_compra=date(2023, 10, 1),
        data_expiracao=date(2023, 12, 30),  # 90 dias após compra (RN-01)
        sessao_total=10,
        sessao_restante=8,
        tipo_pagamento="PARTICULAR",
        valor=600.00,
        status="ATIVO",
        convenio_id=None
    )
    db_session.add(pacote_ativo)
    db_session.commit()

    # Pacote para paciente particular (expirado)
    pacote_expirado = Pacote(
        paciente_id=paciente_particular.id,
        data_compra=date(2023, 1, 1),
        data_expiracao=date(2023, 4, 1),  # Expirado
        sessao_total=10,
        sessao_restante=5,
        tipo_pagamento="PARTICULAR",
        valor=600.00,
        status="EXPIRADO",
        convenio_id=None
    )
    db_session.add(pacote_expirado)
    db_session.commit()

    # Pacote para paciente de convênio
    pacote_convenio = Pacote(
        paciente_id=paciente_convenio.id,
        data_compra=date(2023, 10, 1),
        data_expiracao=date(2023, 12, 30),
        sessao_total=10,
        sessao_restante=10,
        tipo_pagamento="CONVENIO",
        valor=500.00,
        status="ATIVO",
        convenio_id=convenio.id
    )
    db_session.add(pacote_convenio)
    db_session.commit()

    # Sessão agendada
    sessao_agendada = Sessao(
        paciente_id=paciente_particular.id,
        profissional_id=profissional.id,
        sala_id=sala.id,
        pacote_id=pacote_ativo.id,
        convenio_id=None,
        data_hora_inicio=datetime(2023, 12, 15, 10, 0),
        data_hora_fim=datetime(2023, 12, 15, 11, 0),
        status="AGENDADO",
        tipo_atendimento="NORMAL",
        observacoes="",
        atraso_minutos=0
    )
    db_session.add(sessao_agendada)
    db_session.commit()

    return {
        "convenio": convenio,
        "paciente_convenio": paciente_convenio,
        "paciente_particular": paciente_particular,
        "profissional": profissional,
        "sala": sala,
        "pacote_ativo": pacote_ativo,
        "pacote_expirado": pacote_expirado,
        "pacote_convenio": pacote_convenio,
        "sessao_agendada": sessao_agendada
    }


# Sobrescreve a dependência get_db para usar a sessão de teste
@pytest.fixture
def override_get_db(setup_test_data, db_session):
    def _override_get_db():
        try:
            yield db_session
        finally:
            db_session.close()
    return _override_get_db


@pytest.fixture
def app_with_test_db(override_get_db):
    app.dependency_overrides[get_db] = override_get_db
    yield app
    app.dependency_overrides.clear()
