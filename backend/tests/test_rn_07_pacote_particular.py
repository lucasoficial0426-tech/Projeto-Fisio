"""
Testes para RN-07: Paciente particular com pacote expirado ou saldo zerado não pode ser agendado
"""
import pytest
from datetime import date, datetime
from fastapi.testclient import TestClient

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from backend.main import app
from backend.database import get_db
from backend.models.pacote import Pacote
from backend.models.sessao import Sessao


@pytest.fixture
def client_with_db(override_get_db):
    app.dependency_overrides[get_db] = override_get_db
    yield TestClient(app)
    app.dependency_overrides.clear()


class TestRN07PacoteParticular:
    """Testes para RN-07: Paciente particular com pacote expirado ou saldo zerado"""

    def test_agendar_sessao_com_pacote_ativo(self, client_with_db, setup_test_data):
        """
        Dado um paciente particular com pacote ativo
        Quando tentamos agendar uma sessão
        Então o agendamento deve ser permitido
        """
        # Dado: Paciente com pacote ativo
        paciente = setup_test_data["paciente_particular"]
        pacote = setup_test_data["pacote_ativo"]
        
        # Quando: Tentamos agendar uma sessão
        sessao_data = {
            "paciente_id": paciente.id,
            "profissional_id": setup_test_data["profissional"].id,
            "sala_id": setup_test_data["sala"].id,
            "pacote_id": pacote.id,
            "data_hora_inicio": "2023-12-25T10:00:00",
            "data_hora_fim": "2023-12-25T11:00:00",
            "status": "AGENDADO",
            "tipo_atendimento": "NORMAL"
        }
        response = client_with_db.post("/api/sessoes/", json=sessao_data)
        
        # Então: Deve ser criado com sucesso
        assert response.status_code == 201

    def test_agendar_sessao_com_pacote_expirado(self, client_with_db, setup_test_data):
        """
        Dado um paciente particular com pacote expirado
        Quando tentamos agendar uma sessão
        Então o agendamento deve ser rejeitado (RN-07)
        """
        # Dado: Paciente com pacote expirado
        paciente = setup_test_data["paciente_particular"]
        pacote = setup_test_data["pacote_expirado"]
        
        # Quando: Tentamos agendar uma sessão
        sessao_data = {
            "paciente_id": paciente.id,
            "profissional_id": setup_test_data["profissional"].id,
            "sala_id": setup_test_data["sala"].id,
            "pacote_id": pacote.id,
            "data_hora_inicio": "2023-12-25T12:00:00",
            "data_hora_fim": "2023-12-25T13:00:00",
            "status": "AGENDADO",
            "tipo_atendimento": "NORMAL"
        }
        response = client_with_db.post("/api/sessoes/", json=sessao_data)
        
        # Então: Deve ser rejeitado
        assert response.status_code == 400
        assert "RN-07" in response.json()["detail"]

    def test_agendar_sessao_com_pacote_saldo_zerado(self, client_with_db, setup_test_data):
        """
        Dado um paciente particular com pacote com saldo zerado
        Quando tentamos agendar uma sessão
        Então o agendamento deve ser rejeitado (RN-07)
        """
        # Dado: Criar um pacote com saldo zerado
        db_session = next(get_db())
        pacote_saldo_zero = Pacote(
            paciente_id=setup_test_data["paciente_particular"].id,
            data_compra=date(2023, 10, 1),
            data_expiracao=date(2023, 12, 30),  # Ainda não expirou
            sessao_total=10,
            sessao_restante=0,  # Saldo zerado
            tipo_pagamento="PARTICULAR",
            valor=600.00,
            status="UTILIZADO",
            convenio_id=None
        )
        db_session.add(pacote_saldo_zero)
        db_session.commit()
        
        # Quando: Tentamos agendar uma sessão
        sessao_data = {
            "paciente_id": setup_test_data["paciente_particular"].id,
            "profissional_id": setup_test_data["profissional"].id,
            "sala_id": setup_test_data["sala"].id,
            "pacote_id": pacote_saldo_zero.id,
            "data_hora_inicio": "2023-12-25T14:00:00",
            "data_hora_fim": "2023-12-25T15:00:00",
            "status": "AGENDADO",
            "tipo_atendimento": "NORMAL"
        }
        response = client_with_db.post("/api/sessoes/", json=sessao_data)
        
        # Então: Deve ser rejeitado
        assert response.status_code == 400
        assert "RN-07" in response.json()["detail"]

    def test_validar_pacote_para_agendamento_expirado(self, client_with_db, setup_test_data):
        """
        Dado um pacote expirado
        Quando validamos para agendamento
        Então deve retornar False (RN-07)
        """
        # Dado: Pacote expirado
        pacote = setup_test_data["pacote_expirado"]
        
        # Quando: Validamos o pacote
        response = client_with_db.get(f"/api/pacotes/validar/{pacote.id}")
        
        # Então: Deve retornar False
        assert response.status_code == 200
        assert response.json() == False

    def test_validar_pacote_para_agendamento_saldo_zerado(self, client_with_db, setup_test_data):
        """
        Dado um pacote com saldo zerado
        Quando validamos para agendamento
        Então deve retornar False (RN-07)
        """
        # Dado: Criar um pacote com saldo zerado
        db_session = next(get_db())
        pacote_saldo_zero = Pacote(
            paciente_id=setup_test_data["paciente_particular"].id,
            data_compra=date(2023, 10, 1),
            data_expiracao=date(2023, 12, 30),
            sessao_total=10,
            sessao_restante=0,
            tipo_pagamento="PARTICULAR",
            valor=600.00,
            status="UTILIZADO",
            convenio_id=None
        )
        db_session.add(pacote_saldo_zero)
        db_session.commit()
        
        # Quando: Validamos o pacote
        response = client_with_db.get(f"/api/pacotes/validar/{pacote_saldo_zero.id}")
        
        # Então: Deve retornar False
        assert response.status_code == 200
        assert response.json() == False

    def test_validar_pacote_para_agendamento_ativo(self, client_with_db, setup_test_data):
        """
        Dado um pacote ativo
        Quando validamos para agendamento
        Então deve retornar True
        """
        # Dado: Pacote ativo
        pacote = setup_test_data["pacote_ativo"]
        
        # Quando: Validamos o pacote
        response = client_with_db.get(f"/api/pacotes/validar/{pacote.id}")
        
        # Então: Deve retornar True
        assert response.status_code == 200
        assert response.json() == True

    def test_agendar_sessao_convenio_com_pacote_expirado(self, client_with_db, setup_test_data):
        """
        Dado um paciente de convênio com pacote expirado
        Quando tentamos agendar uma sessão
        Então o agendamento deve ser permitido (RN-07 não se aplica a convênios)
        """
        # Dado: Paciente de convênio
        paciente = setup_test_data["paciente_convenio"]
        
        # Criar um pacote expirado para o paciente de convênio
        db_session = next(get_db())
        pacote_expirado_convenio = Pacote(
            paciente_id=paciente.id,
            data_compra=date(2023, 1, 1),
            data_expiracao=date(2023, 4, 1),  # Expirado
            sessao_total=10,
            sessao_restante=5,
            tipo_pagamento="CONVENIO",
            valor=500.00,
            status="EXPIRADO",
            convenio_id=setup_test_data["convenio"].id
        )
        db_session.add(pacote_expirado_convenio)
        db_session.commit()
        
        # Quando: Tentamos agendar uma sessão de convênio
        # (sem especificar pacote_id, já que é convênio)
        sessao_data = {
            "paciente_id": paciente.id,
            "profissional_id": setup_test_data["profissional"].id,
            "sala_id": setup_test_data["sala"].id,
            "convenio_id": setup_test_data["convenio"].id,
            "data_hora_inicio": "2023-12-25T16:00:00",
            "data_hora_fim": "2023-12-25T17:00:00",
            "status": "AGENDADO",
            "tipo_atendimento": "NORMAL"
        }
        response = client_with_db.post("/api/sessoes/", json=sessao_data)
        
        # Então: Deve ser criado com sucesso
        # (RN-07 não se aplica a convênios, apenas a particulares)
        assert response.status_code == 201

    def test_consumir_sessao_pacote_particular(self, client_with_db, setup_test_data):
        """
        Dado um pacote particular ativo
        Quando consumimos uma sessão
        Então o saldo deve diminuir
        """
        # Dado: Pacote ativo
        pacote = setup_test_data["pacote_ativo"]
        
        # Obter saldo antes
        response_antes = client_with_db.get(f"/api/pacotes/{pacote.id}")
        saldo_antes = response_antes.json()["sessao_restante"]
        
        # Quando: Consumimos uma sessão
        response = client_with_db.post(f"/api/pacotes/{pacote.id}/consumir-sessao/")
        
        # Então: Verificamos o saldo depois
        assert response.status_code == 200
        
        response_depois = client_with_db.get(f"/api/pacotes/{pacote.id}")
        saldo_depois = response_depois.json()["sessao_restante"]
        
        assert saldo_depois == saldo_antes - 1

    def test_agendar_sessao_sem_pacote(self, client_with_db, setup_test_data):
        """
        Dado um paciente particular sem pacote
        Quando tentamos agendar uma sessão
        Então o agendamento deve ser rejeitado
        """
        # Dado: Paciente particular sem pacote ativo
        paciente = setup_test_data["paciente_particular"]
        
        # Quando: Tentamos agendar uma sessão sem pacote
        sessao_data = {
            "paciente_id": paciente.id,
            "profissional_id": setup_test_data["profissional"].id,
            "sala_id": setup_test_data["sala"].id,
            "pacote_id": None,  # Sem pacote
            "data_hora_inicio": "2023-12-25T18:00:00",
            "data_hora_fim": "2023-12-25T19:00:00",
            "status": "AGENDADO",
            "tipo_atendimento": "NORMAL"
        }
        response = client_with_db.post("/api/sessoes/", json=sessao_data)
        
        # Então: Deve ser rejeitado (não tem pacote válido)
        assert response.status_code == 400
