"""
Testes para RN-06 e RN-08:
- RN-06: Sessão de convênio só pode ser faturada se tiver evolução clínica registrada
- RN-08: Atraso superior a 15 min bloqueia faturamento no convênio
"""
import pytest
from datetime import datetime, date
from fastapi.testclient import TestClient

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from backend.main import app
from backend.database import get_db
from backend.models.sessao import Sessao, TipoAtendimento, StatusSessao
from backend.models.evolucao_clinica import EvolucaoClinica
from backend.models.fatura import Fatura


@pytest.fixture
def client_with_db(override_get_db):
    app.dependency_overrides[get_db] = override_get_db
    yield TestClient(app)
    app.dependency_overrides.clear()


class TestRN06EvolucaoClinica:
    """Testes para RN-06: Sessão de convênio só pode ser faturada com evolução clínica"""

    def test_sessao_sem_evolucao_nao_pode_ser_faturada(self, client_with_db, setup_test_data):
        """
        Dado uma sessão de convênio sem evolução clínica
        Quando tentamos faturar
        Então deve ser bloqueado (RN-06)
        """
        # Dado: Criar uma sessão de convênio sem evolução
        from backend.models.pacote import Pacote
        
        # Primeiro, criar um pacote de convênio para o paciente de convênio
        pacote_convenio = Pacote(
            paciente_id=setup_test_data["paciente_convenio"].id,
            data_compra=date(2023, 10, 1),
            data_expiracao=date(2023, 12, 30),
            sessao_total=10,
            sessao_restante=10,
            tipo_pagamento="CONVENIO",
            valor=500.00,
            status="ATIVO",
            convenio_id=setup_test_data["convenio"].id
        )
        db_session = next(get_db())
        db_session.add(pacote_convenio)
        db_session.commit()
        
        # Criar sessão de convênio
        sessao = Sessao(
            paciente_id=setup_test_data["paciente_convenio"].id,
            profissional_id=setup_test_data["profissional"].id,
            sala_id=setup_test_data["sala"].id,
            pacote_id=None,
            convenio_id=setup_test_data["convenio"].id,
            data_hora_inicio=datetime(2023, 12, 15, 14, 0),
            data_hora_fim=datetime(2023, 12, 15, 15, 0),
            status=StatusSessao.REALIZADO,
            tipo_atendimento=TipoAtendimento.NORMAL,
            observacoes="",
            atraso_minutos=0
        )
        db_session.add(sessao)
        db_session.commit()
        
        # Quando: Tentamos validar o faturamento
        response = client_with_db.get(f"/api/faturas/validar/{sessao.id}")
        
        # Então: Deve retornar que não pode faturar
        assert response.status_code == 200
        data = response.json()
        assert data["pode_faturar"] == False
        assert "RN-06" in data["mensagem"]

    def test_sessao_com_evolucao_pode_ser_faturada(self, client_with_db, setup_test_data):
        """
        Dado uma sessão de convênio com evolução clínica
        Quando tentamos faturar
        Então deve ser permitido (RN-06)
        """
        # Dado: Criar uma sessão de convênio com evolução
        from backend.models.pacote import Pacote
        
        # Primeiro, criar um pacote de convênio
        pacote_convenio = Pacote(
            paciente_id=setup_test_data["paciente_convenio"].id,
            data_compra=date(2023, 10, 1),
            data_expiracao=date(2023, 12, 30),
            sessao_total=10,
            sessao_restante=10,
            tipo_pagamento="CONVENIO",
            valor=500.00,
            status="ATIVO",
            convenio_id=setup_test_data["convenio"].id
        )
        db_session = next(get_db())
        db_session.add(pacote_convenio)
        db_session.commit()
        
        # Criar sessão de convênio
        sessao = Sessao(
            paciente_id=setup_test_data["paciente_convenio"].id,
            profissional_id=setup_test_data["profissional"].id,
            sala_id=setup_test_data["sala"].id,
            pacote_id=None,
            convenio_id=setup_test_data["convenio"].id,
            data_hora_inicio=datetime(2023, 12, 15, 16, 0),
            data_hora_fim=datetime(2023, 12, 15, 17, 0),
            status=StatusSessao.REALIZADO,
            tipo_atendimento=TipoAtendimento.NORMAL,
            observacoes="",
            atraso_minutos=0
        )
        db_session.add(sessao)
        db_session.commit()
        
        # Adicionar evolução clínica
        evolucao = EvolucaoClinica(
            sessao_id=sessao.id,
            profissional_id=setup_test_data["profissional"].id,
            descricao="Paciente apresentou melhora significativa",
            objetivos="Continuar tratamento",
            conduta="Exercícios de fortalecimento"
        )
        db_session.add(evolucao)
        db_session.commit()
        
        # Quando: Tentamos validar o faturamento
        response = client_with_db.get(f"/api/faturas/validar/{sessao.id}")
        
        # Então: Deve retornar que pode faturar
        assert response.status_code == 200
        data = response.json()
        assert data["pode_faturar"] == True

    def test_criar_fatura_sem_evolucao(self, client_with_db, setup_test_data):
        """
        Dado uma sessão de convênio sem evolução clínica
        Quando tentamos criar uma fatura
        Então deve ser rejeitado (RN-06)
        """
        # Dado: Criar uma sessão de convênio sem evolução
        from backend.models.pacote import Pacote
        
        pacote_convenio = Pacote(
            paciente_id=setup_test_data["paciente_convenio"].id,
            data_compra=date(2023, 10, 1),
            data_expiracao=date(2023, 12, 30),
            sessao_total=10,
            sessao_restante=10,
            tipo_pagamento="CONVENIO",
            valor=500.00,
            status="ATIVO",
            convenio_id=setup_test_data["convenio"].id
        )
        db_session = next(get_db())
        db_session.add(pacote_convenio)
        db_session.commit()
        
        # Criar lote
        lote_data = {
            "convenio_id": setup_test_data["convenio"].id,
            "status": "ABERTO",
            "valor_total": 0.00
        }
        response_lote = client_with_db.post("/api/lotes/", json=lote_data)
        lote = response_lote.json()
        
        # Criar sessão de convênio
        sessao_data = {
            "paciente_id": setup_test_data["paciente_convenio"].id,
            "profissional_id": setup_test_data["profissional"].id,
            "sala_id": setup_test_data["sala"].id,
            "convenio_id": setup_test_data["convenio"].id,
            "data_hora_inicio": "2023-12-15T18:00:00",
            "data_hora_fim": "2023-12-15T19:00:00",
            "status": "REALIZADO",
            "tipo_atendimento": "NORMAL"
        }
        response_sessao = client_with_db.post("/api/sessoes/", json=sessao_data)
        sessao = response_sessao.json()
        
        # Quando: Tentamos criar uma fatura
        fatura_data = {
            "sessao_id": sessao["id"],
            "lote_id": lote["id"],
            "convenio_id": setup_test_data["convenio"].id,
            "valor": 100.00
        }
        response = client_with_db.post("/api/faturas/", json=fatura_data)
        
        # Então: Deve ser rejeitado
        assert response.status_code == 400
        assert "RN-06" in response.json()["detail"]

    def test_criar_fatura_com_evolucao(self, client_with_db, setup_test_data):
        """
        Dado uma sessão de convênio com evolução clínica
        Quando criamos uma fatura
        Então deve ser permitido (RN-06)
        """
        # Dado: Criar uma sessão de convênio com evolução
        from backend.models.pacote import Pacote
        
        pacote_convenio = Pacote(
            paciente_id=setup_test_data["paciente_convenio"].id,
            data_compra=date(2023, 10, 1),
            data_expiracao=date(2023, 12, 30),
            sessao_total=10,
            sessao_restante=10,
            tipo_pagamento="CONVENIO",
            valor=500.00,
            status="ATIVO",
            convenio_id=setup_test_data["convenio"].id
        )
        db_session = next(get_db())
        db_session.add(pacote_convenio)
        db_session.commit()
        
        # Criar lote
        lote_data = {
            "convenio_id": setup_test_data["convenio"].id,
            "status": "ABERTO",
            "valor_total": 0.00
        }
        response_lote = client_with_db.post("/api/lotes/", json=lote_data)
        lote = response_lote.json()
        
        # Criar sessão de convênio
        sessao_data = {
            "paciente_id": setup_test_data["paciente_convenio"].id,
            "profissional_id": setup_test_data["profissional"].id,
            "sala_id": setup_test_data["sala"].id,
            "convenio_id": setup_test_data["convenio"].id,
            "data_hora_inicio": "2023-12-15T20:00:00",
            "data_hora_fim": "2023-12-15T21:00:00",
            "status": "REALIZADO",
            "tipo_atendimento": "NORMAL"
        }
        response_sessao = client_with_db.post("/api/sessoes/", json=sessao_data)
        sessao = response_sessao.json()
        
        # Adicionar evolução clínica
        evolucao_data = {
            "sessao_id": sessao["id"],
            "profissional_id": setup_test_data["profissional"].id,
            "descricao": "Paciente apresentou melhora",
            "objetivos": "Continuar tratamento",
            "conduta": "Exercícios"
        }
        client_with_db.post("/api/evolucoes/", json=evolucao_data)
        
        # Quando: Criamos uma fatura
        fatura_data = {
            "sessao_id": sessao["id"],
            "lote_id": lote["id"],
            "convenio_id": setup_test_data["convenio"].id,
            "valor": 100.00
        }
        response = client_with_db.post("/api/faturas/", json=fatura_data)
        
        # Então: Deve ser criado com sucesso
        assert response.status_code == 201


class TestRN08AtendimentoReduzido:
    """Testes para RN-08: Atraso superior a 15 min bloqueia faturamento"""

    def test_atraso_mais_15min_bloqueia_faturamento(self, client_with_db, setup_test_data):
        """
        Dado uma sessão de convênio com atraso > 15 min
        Quando tentamos faturar
        Então deve ser bloqueado (RN-08)
        """
        # Dado: Criar uma sessão de convênio com atraso > 15 min
        from backend.models.pacote import Pacote
        
        pacote_convenio = Pacote(
            paciente_id=setup_test_data["paciente_convenio"].id,
            data_compra=date(2023, 10, 1),
            data_expiracao=date(2023, 12, 30),
            sessao_total=10,
            sessao_restante=10,
            tipo_pagamento="CONVENIO",
            valor=500.00,
            status="ATIVO",
            convenio_id=setup_test_data["convenio"].id
        )
        db_session = next(get_db())
        db_session.add(pacote_convenio)
        db_session.commit()
        
        # Criar sessão de convênio com atraso > 15 min
        sessao = Sessao(
            paciente_id=setup_test_data["paciente_convenio"].id,
            profissional_id=setup_test_data["profissional"].id,
            sala_id=setup_test_data["sala"].id,
            pacote_id=None,
            convenio_id=setup_test_data["convenio"].id,
            data_hora_inicio=datetime(2023, 12, 16, 10, 0),
            data_hora_fim=datetime(2023, 12, 16, 11, 0),
            status=StatusSessao.REALIZADO,
            tipo_atendimento=TipoAtendimento.REDUZIDO,  # RN-08
            observacoes="",
            atraso_minutos=20  # > 15 min
        )
        db_session.add(sessao)
        db_session.commit()
        
        # Adicionar evolução clínica (para não violar RN-06)
        evolucao = EvolucaoClinica(
            sessao_id=sessao.id,
            profissional_id=setup_test_data["profissional"].id,
            descricao="Paciente chegou atrasado",
            objetivos="",
            conduta=""
        )
        db_session.add(evolucao)
        db_session.commit()
        
        # Quando: Tentamos validar o faturamento
        response = client_with_db.get(f"/api/faturas/validar/{sessao.id}")
        
        # Então: Deve retornar que não pode faturar
        assert response.status_code == 200
        data = response.json()
        assert data["pode_faturar"] == False
        assert "RN-08" in data["mensagem"]

    def test_atraso_15min_ou_menos_permite_faturamento(self, client_with_db, setup_test_data):
        """
        Dado uma sessão de convênio com atraso <= 15 min
        Quando tentamos faturar
        Então deve ser permitido (RN-08)
        """
        # Dado: Criar uma sessão de convênio com atraso <= 15 min
        from backend.models.pacote import Pacote
        
        pacote_convenio = Pacote(
            paciente_id=setup_test_data["paciente_convenio"].id,
            data_compra=date(2023, 10, 1),
            data_expiracao=date(2023, 12, 30),
            sessao_total=10,
            sessao_restante=10,
            tipo_pagamento="CONVENIO",
            valor=500.00,
            status="ATIVO",
            convenio_id=setup_test_data["convenio"].id
        )
        db_session = next(get_db())
        db_session.add(pacote_convenio)
        db_session.commit()
        
        # Criar sessão de convênio com atraso <= 15 min
        sessao = Sessao(
            paciente_id=setup_test_data["paciente_convenio"].id,
            profissional_id=setup_test_data["profissional"].id,
            sala_id=setup_test_data["sala"].id,
            pacote_id=None,
            convenio_id=setup_test_data["convenio"].id,
            data_hora_inicio=datetime(2023, 12, 16, 12, 0),
            data_hora_fim=datetime(2023, 12, 16, 13, 0),
            status=StatusSessao.REALIZADO,
            tipo_atendimento=TipoAtendimento.NORMAL,  # Não é reduzido
            observacoes="",
            atraso_minutos=10  # <= 15 min
        )
        db_session.add(sessao)
        db_session.commit()
        
        # Adicionar evolução clínica
        evolucao = EvolucaoClinica(
            sessao_id=sessao.id,
            profissional_id=setup_test_data["profissional"].id,
            descricao="Paciente chegou no horário",
            objetivos="",
            conduta=""
        )
        db_session.add(evolucao)
        db_session.commit()
        
        # Quando: Tentamos validar o faturamento
        response = client_with_db.get(f"/api/faturas/validar/{sessao.id}")
        
        # Então: Deve retornar que pode faturar
        assert response.status_code == 200
        data = response.json()
        assert data["pode_faturar"] == True

    def test_criar_fatura_com_atraso_mais_15min(self, client_with_db, setup_test_data):
        """
        Dado uma sessão de convênio com atraso > 15 min
        Quando tentamos criar uma fatura
        Então deve ser rejeitado (RN-08)
        """
        # Dado: Criar uma sessão de convênio com atraso > 15 min
        from backend.models.pacote import Pacote
        
        pacote_convenio = Pacote(
            paciente_id=setup_test_data["paciente_convenio"].id,
            data_compra=date(2023, 10, 1),
            data_expiracao=date(2023, 12, 30),
            sessao_total=10,
            sessao_restante=10,
            tipo_pagamento="CONVENIO",
            valor=500.00,
            status="ATIVO",
            convenio_id=setup_test_data["convenio"].id
        )
        db_session = next(get_db())
        db_session.add(pacote_convenio)
        db_session.commit()
        
        # Criar lote
        lote_data = {
            "convenio_id": setup_test_data["convenio"].id,
            "status": "ABERTO",
            "valor_total": 0.00
        }
        response_lote = client_with_db.post("/api/lotes/", json=lote_data)
        lote = response_lote.json()
        
        # Criar sessão de convênio com atraso > 15 min
        sessao_data = {
            "paciente_id": setup_test_data["paciente_convenio"].id,
            "profissional_id": setup_test_data["profissional"].id,
            "sala_id": setup_test_data["sala"].id,
            "convenio_id": setup_test_data["convenio"].id,
            "data_hora_inicio": "2023-12-16T14:00:00",
            "data_hora_fim": "2023-12-16T15:00:00",
            "status": "REALIZADO",
            "tipo_atendimento": "NORMAL",
            "atraso_minutos": 20  # > 15 min
        }
        response_sessao = client_with_db.post("/api/sessoes/", json=sessao_data)
        sessao = response_sessao.json()
        
        # Adicionar evolução clínica (para não violar RN-06)
        evolucao_data = {
            "sessao_id": sessao["id"],
            "profissional_id": setup_test_data["profissional"].id,
            "descricao": "Paciente chegou atrasado",
            "objetivos": "",
            "conduta": ""
        }
        client_with_db.post("/api/evolucoes/", json=evolucao_data)
        
        # Quando: Tentamos criar uma fatura
        fatura_data = {
            "sessao_id": sessao["id"],
            "lote_id": lote["id"],
            "convenio_id": setup_test_data["convenio"].id,
            "valor": 100.00
        }
        response = client_with_db.post("/api/faturas/", json=fatura_data)
        
        # Então: Deve ser rejeitado
        assert response.status_code == 400
        assert "RN-08" in response.json()["detail"]

    def test_sessao_com_atraso_mais_15min_tem_tipo_reduzido(self, db_session, setup_test_data):
        """
        Dado uma sessão com atraso > 15 min
        Quando a sessão é criada ou atualizada
        Então o tipo_atendimento deve ser REDUZIDO (RN-08)
        """
        # Dado: Criar uma sessão com atraso > 15 min
        sessao = Sessao(
            paciente_id=setup_test_data["paciente_particular"].id,
            profissional_id=setup_test_data["profissional"].id,
            sala_id=setup_test_data["sala"].id,
            pacote_id=setup_test_data["pacote_ativo"].id,
            convenio_id=None,
            data_hora_inicio=datetime(2023, 12, 17, 10, 0),
            data_hora_fim=datetime(2023, 12, 17, 11, 0),
            status="REALIZADO",
            tipo_atendimento="NORMAL",
            observacoes="",
            atraso_minutos=20  # > 15 min
        )
        db_session.add(sessao)
        db_session.commit()
        
        # Quando: Recarregamos a sessão
        sessao_reload = db_session.query(Sessao).filter(Sessao.id == sessao.id).first()
        
        # Então: O tipo_atendimento deve ser REDUZIDO
        assert sessao_reload.tipo_atendimento == "REDUZIDO"
