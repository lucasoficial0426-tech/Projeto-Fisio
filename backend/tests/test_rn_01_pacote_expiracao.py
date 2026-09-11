"""
Testes para RN-01: Pacote de 10 sessões expira 90 dias após a data de compra
"""
import pytest
from datetime import date, timedelta
from fastapi.testclient import TestClient

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from backend.main import app
from backend.database import get_db
from backend.models.pacote import Pacote


@pytest.fixture
def client_with_db(override_get_db):
    app.dependency_overrides[get_db] = override_get_db
    yield TestClient(app)
    app.dependency_overrides.clear()


class TestRN01PacoteExpiracao:
    """Testes para RN-01: Pacote expira 90 dias após a compra"""

    def test_pacote_expiracao_90_dias(self, db_session, setup_test_data):
        """
        Dado um pacote criado com data de compra
        Quando calculamos a data de expiração
        Então a data de expiração deve ser 90 dias após a data de compra
        """
        # Dado: Data de compra
        data_compra = date(2023, 10, 1)
        
        # Quando: Criamos um pacote
        pacote = Pacote(
            paciente_id=setup_test_data["paciente_particular"].id,
            data_compra=data_compra,
            data_expiracao=data_compra + timedelta(days=90),
            sessao_total=10,
            sessao_restante=10,
            tipo_pagamento="PARTICULAR",
            valor=600.00,
            status="ATIVO",
            convenio_id=None
        )
        db_session.add(pacote)
        db_session.commit()
        
        # Então: Verificamos que a expiração é 90 dias após
        assert pacote.data_expiracao == date(2023, 12, 30)
        assert (pacote.data_expiracao - pacote.data_compra).days == 90

    def test_pacote_status_expirado(self, db_session, setup_test_data):
        """
        Dado um pacote com data de expiração no passado
        Quando verificamos o status
        Então o status deve ser EXPIRADO
        """
        # Dado: Pacote expirado
        pacote_expirado = setup_test_data["pacote_expirado"]
        
        # Quando/Então: Verificamos o status
        assert pacote_expirado.status == "EXPIRADO"
        assert pacote_expirado.data_expiracao < date.today()

    def test_pacote_status_ativo(self, db_session, setup_test_data):
        """
        Dado um pacote com data de expiração no futuro
        Quando verificamos o status
        Então o status deve ser ATIVO
        """
        # Dado: Pacote ativo
        pacote_ativo = setup_test_data["pacote_ativo"]
        
        # Quando/Então: Verificamos o status
        assert pacote_ativo.status == "ATIVO"
        assert pacote_ativo.data_expiracao >= date.today()

    def test_criar_pacote_com_expiracao_automatica(self, client_with_db, setup_test_data):
        """
        Dado os dados de um pacote sem data de expiração
        Quando criamos o pacote via API
        Então a API deve calcular automaticamente a expiração como 90 dias após a compra
        """
        # Dado: Dados do pacote
        pacote_data = {
            "paciente_id": setup_test_data["paciente_particular"].id,
            "data_compra": "2023-11-01",
            "sessao_total": 10,
            "sessao_restante": 10,
            "tipo_pagamento": "PARTICULAR",
            "valor": 600.00
        }
        
        # Quando: Criamos o pacote via API
        response = client_with_db.post("/api/pacotes/", json=pacote_data)
        
        # Então: Verificamos a resposta
        assert response.status_code == 201
        data = response.json()
        
        # A data de expiração deve ser 90 dias após a compra
        data_compra = date.fromisoformat(pacote_data["data_compra"])
        data_expiracao_esperada = data_compra + timedelta(days=90)
        data_expiracao = date.fromisoformat(data["data_expiracao"])
        
        assert data_expiracao == data_expiracao_esperada

    def test_pacotes_proximos_expirar(self, client_with_db, setup_test_data):
        """
        Dado pacotes com diferentes datas de expiração
        Quando buscamos por pacotes próximos de expirar
        Então apenas os pacotes que irão expirar nos próximos 30 dias devem ser retornados
        """
        # Dado: Pacotes criados
        # pacote_ativo expira em 2023-12-30 (dentro de 30 dias a partir de 2023-11-01)
        # pacote_expirado já expirou
        
        # Quando: Buscamos por pacotes próximos de expirar
        response = client_with_db.get("/api/pacotes/proximos-expirar/?dias=30")
        
        # Então: Verificamos a resposta
        assert response.status_code == 200
        pacotes = response.json()
        
        # Deve incluir o pacote ativo (que expira em 30 dias)
        pacote_ids = [p["id"] for p in pacotes]
        assert setup_test_data["pacote_ativo"].id in pacote_ids
        
        # Não deve incluir o pacote expirado
        assert setup_test_data["pacote_expirado"].id not in pacote_ids

    def test_validar_pacote_para_agendamento_expirado(self, client_with_db, setup_test_data):
        """
        Dado um pacote expirado
        Quando tentamos validar para agendamento
        Então deve retornar False (RN-07)
        """
        # Dado: Pacote expirado
        pacote_id = setup_test_data["pacote_expirado"].id
        
        # Quando: Validamos o pacote
        response = client_with_db.get(f"/api/pacotes/validar/{pacote_id}")
        
        # Então: Deve retornar False
        assert response.status_code == 200
        assert response.json() == False

    def test_validar_pacote_para_agendamento_ativo(self, client_with_db, setup_test_data):
        """
        Dado um pacote ativo
        Quando tentamos validar para agendamento
        Então deve retornar True
        """
        # Dado: Pacote ativo
        pacote_id = setup_test_data["pacote_ativo"].id
        
        # Quando: Validamos o pacote
        response = client_with_db.get(f"/api/pacotes/validar/{pacote_id}")
        
        # Então: Deve retornar True
        assert response.status_code == 200
        assert response.json() == True
