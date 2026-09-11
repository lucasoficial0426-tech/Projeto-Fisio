"""
Testes para RN-02 e RN-03:
- RN-02: Falta sem aviso com antecedência de 24h consome uma sessão do pacote
- RN-03: Falta avisada com 24h ou mais de antecedência não consome sessão
"""
import pytest
from datetime import datetime, timedelta
from fastapi.testclient import TestClient

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from backend.main import app
from backend.database import get_db
from backend.models.falta import Falta
from backend.models.pacote import Pacote


@pytest.fixture
def client_with_db(override_get_db):
    app.dependency_overrides[get_db] = override_get_db
    yield TestClient(app)
    app.dependency_overrides.clear()


class TestRN02FaltaSemAviso:
    """Testes para RN-02: Falta sem aviso consome sessão"""

    def test_falta_sem_aviso_consome_sessao(self, db_session, setup_test_data):
        """
        Dado uma sessão com pacote ativo
        Quando registramos uma falta sem aviso com antecedência < 24h
        Então uma sessão do pacote deve ser consumida
        """
        # Dado: Sessão agendada com pacote ativo
        sessao = setup_test_data["sessao_agendada"]
        pacote_antes = db_session.query(Pacote).filter(Pacote.id == sessao.pacote_id).first()
        sessao_restante_antes = pacote_antes.sessao_restante
        
        # Quando: Registramos uma falta sem aviso
        falta = Falta(
            sessao_id=sessao.id,
            avisado=False,
            antecedencia_horas=12.0,  # Menos de 24h
            justificativa="Paciente não avisou"
        )
        db_session.add(falta)
        db_session.commit()
        
        # Então: Verificamos que uma sessão foi consumida
        pacote_depois = db_session.query(Pacote).filter(Pacote.id == sessao.pacote_id).first()
        sessao_restante_depois = pacote_depois.sessao_restante
        
        assert sessao_restante_depois == sessao_restante_antes - 1

    def test_falta_sem_aviso_api(self, client_with_db, setup_test_data):
        """
        Dado uma sessão agendada
        Quando registramos uma falta sem aviso via API
        Então o pacote deve ter uma sessão consumida
        """
        # Dado: Sessão agendada
        sessao = setup_test_data["sessao_agendada"]
        pacote_id = sessao.pacote_id
        
        # Obter sessão restante antes
        response_pacote = client_with_db.get(f"/api/pacotes/{pacote_id}")
        sessao_restante_antes = response_pacote.json()["sessao_restante"]
        
        # Quando: Registramos uma falta sem aviso
        falta_data = {
            "sessao_id": sessao.id,
            "avisado": False,
            "antecedencia_horas": 12.0,
            "justificativa": "Paciente não avisou"
        }
        response = client_with_db.post("/api/faltas/", json=falta_data)
        
        # Então: Verificamos a resposta
        assert response.status_code == 201
        
        # Verificamos que uma sessão foi consumida
        response_pacote_depois = client_with_db.get(f"/api/pacotes/{pacote_id}")
        sessao_restante_depois = response_pacote_depois.json()["sessao_restante"]
        
        assert sessao_restante_depois == sessao_restante_antes - 1


class TestRN03FaltaAvisada:
    """Testes para RN-03: Falta avisada não consome sessão"""

    def test_falta_avisada_nao_consome_sessao(self, db_session, setup_test_data):
        """
        Dado uma sessão com pacote ativo
        Quando registramos uma falta avisada com antecedência >= 24h
        Então nenhuma sessão do pacote deve ser consumida
        """
        # Dado: Criar uma nova sessão para teste
        from backend.models.sessao import Sessao
        sessao = Sessao(
            paciente_id=setup_test_data["paciente_particular"].id,
            profissional_id=setup_test_data["profissional"].id,
            sala_id=setup_test_data["sala"].id,
            pacote_id=setup_test_data["pacote_ativo"].id,
            convenio_id=None,
            data_hora_inicio=datetime(2023, 12, 16, 10, 0),
            data_hora_fim=datetime(2023, 12, 16, 11, 0),
            status="AGENDADO",
            tipo_atendimento="NORMAL",
            observacoes="",
            atraso_minutos=0
        )
        db_session.add(sessao)
        db_session.commit()
        
        pacote_antes = db_session.query(Pacote).filter(Pacote.id == sessao.pacote_id).first()
        sessao_restante_antes = pacote_antes.sessao_restante
        
        # Quando: Registramos uma falta avisada com 24h de antecedência
        falta = Falta(
            sessao_id=sessao.id,
            avisado=True,
            antecedencia_horas=24.0,  # Exatamente 24h
            justificativa="Paciente avisou com antecedência"
        )
        db_session.add(falta)
        db_session.commit()
        
        # Então: Verificamos que nenhuma sessão foi consumida
        pacote_depois = db_session.query(Pacote).filter(Pacote.id == sessao.pacote_id).first()
        sessao_restante_depois = pacote_depois.sessao_restante
        
        assert sessao_restante_depois == sessao_restante_antes

    def test_falta_avisada_api(self, client_with_db, setup_test_data):
        """
        Dado uma sessão agendada
        Quando registramos uma falta avisada via API
        Então o pacote não deve ter sessões consumidas
        """
        # Dado: Criar uma nova sessão para teste
        sessao_data = {
            "paciente_id": setup_test_data["paciente_particular"].id,
            "profissional_id": setup_test_data["profissional"].id,
            "sala_id": setup_test_data["sala"].id,
            "pacote_id": setup_test_data["pacote_ativo"].id,
            "data_hora_inicio": "2023-12-16T10:00:00",
            "data_hora_fim": "2023-12-16T11:00:00",
            "status": "AGENDADO",
            "tipo_atendimento": "NORMAL"
        }
        response_sessao = client_with_db.post("/api/sessoes/", json=sessao_data)
        sessao = response_sessao.json()
        pacote_id = sessao["pacote_id"]
        
        # Obter sessão restante antes
        response_pacote = client_with_db.get(f"/api/pacotes/{pacote_id}")
        sessao_restante_antes = response_pacote.json()["sessao_restante"]
        
        # Quando: Registramos uma falta avisada
        falta_data = {
            "sessao_id": sessao["id"],
            "avisado": True,
            "antecedencia_horas": 24.0,
            "justificativa": "Paciente avisou com antecedência"
        }
        response = client_with_db.post("/api/faltas/", json=falta_data)
        
        # Então: Verificamos a resposta
        assert response.status_code == 201
        
        # Verificamos que nenhuma sessão foi consumida
        response_pacote_depois = client_with_db.get(f"/api/pacotes/{pacote_id}")
        sessao_restante_depois = response_pacote_depois.json()["sessao_restante"]
        
        assert sessao_restante_depois == sessao_restante_antes

    def test_falta_com_antecedencia_mais_24h(self, db_session, setup_test_data):
        """
        Dado uma sessão com pacote ativo
        Quando registramos uma falta avisada com antecedência > 24h
        Então nenhuma sessão do pacote deve ser consumida
        """
        # Dado: Criar uma nova sessão para teste
        from backend.models.sessao import Sessao
        sessao = Sessao(
            paciente_id=setup_test_data["paciente_particular"].id,
            profissional_id=setup_test_data["profissional"].id,
            sala_id=setup_test_data["sala"].id,
            pacote_id=setup_test_data["pacote_ativo"].id,
            convenio_id=None,
            data_hora_inicio=datetime(2023, 12, 17, 10, 0),
            data_hora_fim=datetime(2023, 12, 17, 11, 0),
            status="AGENDADO",
            tipo_atendimento="NORMAL",
            observacoes="",
            atraso_minutos=0
        )
        db_session.add(sessao)
        db_session.commit()
        
        pacote_antes = db_session.query(Pacote).filter(Pacote.id == sessao.pacote_id).first()
        sessao_restante_antes = pacote_antes.sessao_restante
        
        # Quando: Registramos uma falta avisada com 48h de antecedência
        falta = Falta(
            sessao_id=sessao.id,
            avisado=True,
            antecedencia_horas=48.0,  # Mais de 24h
            justificativa="Paciente avisou com 48h de antecedência"
        )
        db_session.add(falta)
        db_session.commit()
        
        # Então: Verificamos que nenhuma sessão foi consumida
        pacote_depois = db_session.query(Pacote).filter(Pacote.id == sessao.pacote_id).first()
        sessao_restante_depois = pacote_depois.sessao_restante
        
        assert sessao_restante_depois == sessao_restante_antes

    def test_falta_nao_avisada_com_23h59min(self, db_session, setup_test_data):
        """
        Dado uma sessão com pacote ativo
        Quando registramos uma falta não avisada com antecedência de 23h59min
        Então uma sessão do pacote deve ser consumida (RN-02)
        """
        # Dado: Criar uma nova sessão para teste
        from backend.models.sessao import Sessao
        sessao = Sessao(
            paciente_id=setup_test_data["paciente_particular"].id,
            profissional_id=setup_test_data["profissional"].id,
            sala_id=setup_test_data["sala"].id,
            pacote_id=setup_test_data["pacote_ativo"].id,
            convenio_id=None,
            data_hora_inicio=datetime(2023, 12, 18, 10, 0),
            data_hora_fim=datetime(2023, 12, 18, 11, 0),
            status="AGENDADO",
            tipo_atendimento="NORMAL",
            observacoes="",
            atraso_minutos=0
        )
        db_session.add(sessao)
        db_session.commit()
        
        pacote_antes = db_session.query(Pacote).filter(Pacote.id == sessao.pacote_id).first()
        sessao_restante_antes = pacote_antes.sessao_restante
        
        # Quando: Registramos uma falta não avisada com 23h59min
        falta = Falta(
            sessao_id=sessao.id,
            avisado=False,
            antecedencia_horas=23.98,  # 23h59min
            justificativa="Paciente não avisou"
        )
        db_session.add(falta)
        db_session.commit()
        
        # Então: Verificamos que uma sessão foi consumida
        pacote_depois = db_session.query(Pacote).filter(Pacote.id == sessao.pacote_id).first()
        sessao_restante_depois = pacote_depois.sessao_restante
        
        assert sessao_restante_depois == sessao_restante_antes - 1
