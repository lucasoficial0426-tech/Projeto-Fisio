"""
Testes para RN-04 e RN-05:
- RN-04: Uma sala não pode receber mais sessões simultâneas do que sua capacidade cadastrada
- RN-05: Um profissional não pode ter duas sessões no mesmo horário (mesmo em salas diferentes)
"""
import pytest
from datetime import datetime, timedelta
from fastapi.testclient import TestClient

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from backend.main import app
from backend.database import get_db
from backend.models.sessao import Sessao
from backend.models.sala import Sala


@pytest.fixture
def client_with_db(override_get_db):
    app.dependency_overrides[get_db] = override_get_db
    yield TestClient(app)
    app.dependency_overrides.clear()


class TestRN04SalaCapacidade:
    """Testes para RN-04: Sala não pode ter mais sessões do que sua capacidade"""

    def test_sala_capacidade_1_pode_ter_1_sessao(self, db_session, setup_test_data):
        """
        Dado uma sala com capacidade 1
        Quando agendamos 1 sessão
        Então o agendamento deve ser permitido
        """
        # Dado: Sala com capacidade 1
        sala = setup_test_data["sala"]
        assert sala.capacidade == 1
        
        # Quando: Criamos uma sessão
        sessao = Sessao(
            paciente_id=setup_test_data["paciente_particular"].id,
            profissional_id=setup_test_data["profissional"].id,
            sala_id=sala.id,
            pacote_id=setup_test_data["pacote_ativo"].id,
            convenio_id=None,
            data_hora_inicio=datetime(2023, 12, 20, 14, 0),
            data_hora_fim=datetime(2023, 12, 20, 15, 0),
            status="AGENDADO",
            tipo_atendimento="NORMAL",
            observacoes="",
            atraso_minutos=0
        )
        db_session.add(sessao)
        db_session.commit()
        
        # Então: A sessão foi criada com sucesso
        assert sessao.id is not None

    def test_sala_capacidade_1_nao_pode_ter_2_sessoes_simultaneas(self, client_with_db, setup_test_data):
        """
        Dado uma sala com capacidade 1
        Quando tentamos agendar 2 sessões no mesmo horário
        Então a segunda sessão deve ser rejeitada (RN-04)
        """
        # Dado: Sala com capacidade 1
        sala = setup_test_data["sala"]
        
        # Criar primeira sessão
        sessao1_data = {
            "paciente_id": setup_test_data["paciente_particular"].id,
            "profissional_id": setup_test_data["profissional"].id,
            "sala_id": sala.id,
            "pacote_id": setup_test_data["pacote_ativo"].id,
            "data_hora_inicio": "2023-12-20T14:00:00",
            "data_hora_fim": "2023-12-20T15:00:00",
            "status": "AGENDADO",
            "tipo_atendimento": "NORMAL"
        }
        response1 = client_with_db.post("/api/sessoes/", json=sessao1_data)
        assert response1.status_code == 201
        
        # Quando: Tentamos criar segunda sessão no mesmo horário
        # Precisamos de um paciente diferente para evitar conflito de profissional
        from backend.models.paciente import Paciente
        paciente2 = Paciente(
            nome="Outro Paciente",
            cpf="999.999.999-99",
            data_nascimento=date(1985, 1, 1),
            telefone="(11) 99999-9998",
            email="outro@email.com",
            endereco="Rua Z, 999",
            convenio_id=None,
            ativo=True
        )
        db_session = next(get_db())
        db_session.add(paciente2)
        db_session.commit()
        
        sessao2_data = {
            "paciente_id": paciente2.id,
            "profissional_id": setup_test_data["profissional"].id,
            "sala_id": sala.id,
            "data_hora_inicio": "2023-12-20T14:30:00",  # Sobrepõe com a primeira
            "data_hora_fim": "2023-12-20T15:30:00",
            "status": "AGENDADO",
            "tipo_atendimento": "NORMAL"
        }
        
        # Como o profissional já está ocupado, vamos usar um horário diferente
        # mas ainda sobrepondo na sala
        sessao2_data["data_hora_inicio"] = "2023-12-20T14:00:00"
        sessao2_data["data_hora_fim"] = "2023-12-20T15:00:00"
        
        # Mas precisamos de um profissional diferente
        from backend.models.profissional import Profissional
        profissional2 = Profissional(
            nome="Dr. Outro",
            cpf="444.444.444-44",
            crf="CRF-99999",
            especialidade="Fisioterapia",
            telefone="(11) 88888-8888",
            email="outro@dr.com",
            ativo=True
        )
        db_session.add(profissional2)
        db_session.commit()
        
        sessao2_data["profissional_id"] = profissional2.id
        
        response2 = client_with_db.post("/api/sessoes/", json=sessao2_data)
        
        # Então: A segunda sessão deve ser rejeitada
        assert response2.status_code == 400
        assert "RN-04" in response2.json()["detail"]

    def test_verificar_capacidade_sala(self, client_with_db, setup_test_data):
        """
        Dado uma sala com capacidade 1
        Quando verificamos a capacidade para um horário com uma sessão
        Então deve retornar False (sem capacidade)
        """
        # Dado: Sala com capacidade 1
        sala = setup_test_data["sala"]
        
        # Criar uma sessão
        sessao_data = {
            "paciente_id": setup_test_data["paciente_particular"].id,
            "profissional_id": setup_test_data["profissional"].id,
            "sala_id": sala.id,
            "pacote_id": setup_test_data["pacote_ativo"].id,
            "data_hora_inicio": "2023-12-21T10:00:00",
            "data_hora_fim": "2023-12-21T11:00:00",
            "status": "AGENDADO",
            "tipo_atendimento": "NORMAL"
        }
        client_with_db.post("/api/sessoes/", json=sessao_data)
        
        # Quando: Verificamos a capacidade
        response = client_with_db.get(
            f"/api/salas/{sala.id}/capacidade/?data_hora_inicio=2023-12-21T10:00:00&data_hora_fim=2023-12-21T11:00:00"
        )
        
        # Então: Deve retornar False (sem capacidade)
        assert response.status_code == 200
        assert response.json() == False

    def test_verificar_capacidade_sala_disponivel(self, client_with_db, setup_test_data):
        """
        Dado uma sala com capacidade 1
        Quando verificamos a capacidade para um horário sem sessões
        Então deve retornar True (com capacidade)
        """
        # Dado: Sala com capacidade 1
        sala = setup_test_data["sala"]
        
        # Quando: Verificamos a capacidade para um horário livre
        response = client_with_db.get(
            f"/api/salas/{sala.id}/capacidade/?data_hora_inicio=2023-12-25T10:00:00&data_hora_fim=2023-12-25T11:00:00"
        )
        
        # Então: Deve retornar True (com capacidade)
        assert response.status_code == 200
        assert response.json() == True


class TestRN05ProfissionalOcupado:
    """Testes para RN-05: Profissional não pode ter duas sessões no mesmo horário"""

    def test_profissional_pode_ter_1_sessao(self, db_session, setup_test_data):
        """
        Dado um profissional
        Quando agendamos 1 sessão
        Então o agendamento deve ser permitido
        """
        # Dado: Profissional
        profissional = setup_test_data["profissional"]
        
        # Quando: Criamos uma sessão
        sessao = Sessao(
            paciente_id=setup_test_data["paciente_particular"].id,
            profissional_id=profissional.id,
            sala_id=setup_test_data["sala"].id,
            pacote_id=setup_test_data["pacote_ativo"].id,
            convenio_id=None,
            data_hora_inicio=datetime(2023, 12, 22, 9, 0),
            data_hora_fim=datetime(2023, 12, 22, 10, 0),
            status="AGENDADO",
            tipo_atendimento="NORMAL",
            observacoes="",
            atraso_minutos=0
        )
        db_session.add(sessao)
        db_session.commit()
        
        # Então: A sessão foi criada com sucesso
        assert sessao.id is not None

    def test_profissional_nao_pode_ter_2_sessoes_mesmo_horario(self, client_with_db, setup_test_data):
        """
        Dado um profissional
        Quando tentamos agendar 2 sessões no mesmo horário
        Então a segunda sessão deve ser rejeitada (RN-05)
        """
        # Dado: Profissional
        profissional = setup_test_data["profissional"]
        
        # Criar primeira sessão
        sessao1_data = {
            "paciente_id": setup_test_data["paciente_particular"].id,
            "profissional_id": profissional.id,
            "sala_id": setup_test_data["sala"].id,
            "pacote_id": setup_test_data["pacote_ativo"].id,
            "data_hora_inicio": "2023-12-22T09:00:00",
            "data_hora_fim": "2023-12-22T10:00:00",
            "status": "AGENDADO",
            "tipo_atendimento": "NORMAL"
        }
        response1 = client_with_db.post("/api/sessoes/", json=sessao1_data)
        assert response1.status_code == 201
        
        # Quando: Tentamos criar segunda sessão no mesmo horário
        # Usamos um paciente diferente e uma sala diferente
        from backend.models.paciente import Paciente
        paciente2 = Paciente(
            nome="Outro Paciente 2",
            cpf="888.888.888-88",
            data_nascimento=date(1990, 1, 1),
            telefone="(11) 77777-7776",
            email="outro2@email.com",
            endereco="Rua Y, 888",
            convenio_id=None,
            ativo=True
        )
        db_session = next(get_db())
        db_session.add(paciente2)
        db_session.commit()
        
        from backend.models.sala import Sala
        sala2 = Sala(
            nome="Sala 2",
            descricao="Outra sala",
            capacidade=1,
            localizacao="Andar 2",
            ativo=True
        )
        db_session.add(sala2)
        db_session.commit()
        
        sessao2_data = {
            "paciente_id": paciente2.id,
            "profissional_id": profissional.id,  # Mesmo profissional
            "sala_id": sala2.id,  # Sala diferente
            "data_hora_inicio": "2023-12-22T09:00:00",  # Mesmo horário
            "data_hora_fim": "2023-12-22T10:00:00",
            "status": "AGENDADO",
            "tipo_atendimento": "NORMAL"
        }
        response2 = client_with_db.post("/api/sessoes/", json=sessao2_data)
        
        # Então: A segunda sessão deve ser rejeitada
        assert response2.status_code == 400
        assert "RN-05" in response2.json()["detail"]

    def test_profissional_pode_ter_sessoes_em_horarios_diferentes(self, client_with_db, setup_test_data):
        """
        Dado um profissional
        Quando agendamos 2 sessões em horários diferentes
        Então ambas as sessões devem ser permitidas
        """
        # Dado: Profissional
        profissional = setup_test_data["profissional"]
        
        # Criar primeira sessão
        sessao1_data = {
            "paciente_id": setup_test_data["paciente_particular"].id,
            "profissional_id": profissional.id,
            "sala_id": setup_test_data["sala"].id,
            "pacote_id": setup_test_data["pacote_ativo"].id,
            "data_hora_inicio": "2023-12-22T09:00:00",
            "data_hora_fim": "2023-12-22T10:00:00",
            "status": "AGENDADO",
            "tipo_atendimento": "NORMAL"
        }
        response1 = client_with_db.post("/api/sessoes/", json=sessao1_data)
        assert response1.status_code == 201
        
        # Quando: Criamos segunda sessão em horário diferente
        from backend.models.paciente import Paciente
        paciente2 = Paciente(
            nome="Outro Paciente 3",
            cpf="777.777.777-77",
            data_nascimento=date(1988, 1, 1),
            telefone="(11) 66666-6666",
            email="outro3@email.com",
            endereco="Rua X, 777",
            convenio_id=None,
            ativo=True
        )
        db_session = next(get_db())
        db_session.add(paciente2)
        db_session.commit()
        
        sessao2_data = {
            "paciente_id": paciente2.id,
            "profissional_id": profissional.id,
            "sala_id": setup_test_data["sala"].id,
            "data_hora_inicio": "2023-12-22T11:00:00",  # Horário diferente
            "data_hora_fim": "2023-12-22T12:00:00",
            "status": "AGENDADO",
            "tipo_atendimento": "NORMAL"
        }
        response2 = client_with_db.post("/api/sessoes/", json=sessao2_data)
        
        # Então: Ambas as sessões devem ser criadas
        assert response2.status_code == 201

    def test_verificar_conflitos_profissional(self, client_with_db, setup_test_data):
        """
        Dado um profissional com uma sessão agendada
        Quando verificamos conflitos para o mesmo horário
        Então deve retornar True (tem conflito)
        """
        # Dado: Profissional com uma sessão
        profissional = setup_test_data["profissional"]
        
        # Criar uma sessão
        sessao_data = {
            "paciente_id": setup_test_data["paciente_particular"].id,
            "profissional_id": profissional.id,
            "sala_id": setup_test_data["sala"].id,
            "pacote_id": setup_test_data["pacote_ativo"].id,
            "data_hora_inicio": "2023-12-23T10:00:00",
            "data_hora_fim": "2023-12-23T11:00:00",
            "status": "AGENDADO",
            "tipo_atendimento": "NORMAL"
        }
        client_with_db.post("/api/sessoes/", json=sessao_data)
        
        # Quando: Verificamos conflitos
        response = client_with_db.get(
            "/api/sessoes/verificar-conflitos/"
            f"?paciente_id={setup_test_data['paciente_particular'].id}"
            f"&profissional_id={profissional.id}"
            f"&sala_id={setup_test_data['sala'].id}"
            f"&data_hora_inicio=2023-12-23T10:00:00"
            f"&data_hora_fim=2023-12-23T11:00:00"
        )
        
        # Então: Deve retornar que tem conflito
        assert response.status_code == 200
        data = response.json()
        assert data["tem_conflito"] == True
        assert "RN-05" in data["mensagem"]
