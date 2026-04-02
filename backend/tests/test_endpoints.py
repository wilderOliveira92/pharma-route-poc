"""
Integration tests for FastAPI endpoints.
Uses in-memory SQLite and overrides the DB dependency.
"""
from __future__ import annotations

import sys
import os
import uuid

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

# ---------------------------------------------------------------------------
# Test database setup — must happen before importing main/app
# ---------------------------------------------------------------------------

TEST_DATABASE_URL = "sqlite:///./test_pharma.db"

test_engine = create_engine(
    TEST_DATABASE_URL,
    connect_args={"check_same_thread": False},
)
TestSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=test_engine)

# Patch the database module so that the app uses our test engine
import database as db_module
db_module.engine = test_engine
db_module.SessionLocal = TestSessionLocal

# Now import the app (after patching)
from main import app  # noqa: E402
from database import get_db, Base  # noqa: E402
import models  # noqa: F401,E402


def override_get_db():
    db = TestSessionLocal()
    try:
        yield db
    finally:
        db.close()


app.dependency_overrides[get_db] = override_get_db


# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------


@pytest.fixture(autouse=True)
def setup_and_teardown_db():
    """Create tables before each test and drop them after."""
    Base.metadata.create_all(bind=test_engine)
    yield
    Base.metadata.drop_all(bind=test_engine)


@pytest.fixture
def client():
    # raise_server_exceptions=True so test failures surface clearly
    # Don't use as context manager to avoid triggering startup event twice
    return TestClient(app, raise_server_exceptions=True)


@pytest.fixture
def representante_id():
    """Insert a representante directly into the DB and return its id."""
    from models.representante import Representante

    db = TestSessionLocal()
    rep = Representante(
        id=str(uuid.uuid4()),
        nome="Teste Rep",
        email="testrep@pharma.com",
        regiao="SP",
    )
    db.add(rep)
    db.commit()
    rep_id = rep.id
    db.close()
    return rep_id


# ---------------------------------------------------------------------------
# POST /medicos
# ---------------------------------------------------------------------------


class TestCriarMedico:
    def test_criar_medico_sucesso(self, client, representante_id):
        payload = {
            "nome": "Dr. Teste Silva",
            "crm": "CRM/SP-TEST001",
            "especialidade": "Cardiologia",
            "prioridade": "A",
            "representante_id": representante_id,
        }
        response = client.post("/medicos", json=payload)
        assert response.status_code == 201, response.text
        data = response.json()
        assert data["nome"] == "Dr. Teste Silva"
        assert data["crm"] == "CRM/SP-TEST001"
        assert data["prioridade"] == "A"
        assert data["ativo"] is True
        assert "id" in data

    def test_criar_medico_prioridade_invalida(self, client, representante_id):
        payload = {
            "nome": "Dr. Invalido",
            "crm": "CRM/SP-INVALID",
            "especialidade": "X",
            "prioridade": "D",  # invalid
            "representante_id": representante_id,
        }
        response = client.post("/medicos", json=payload)
        assert response.status_code == 422

    def test_criar_medico_campos_obrigatorios(self, client):
        response = client.post("/medicos", json={})
        assert response.status_code == 422


# ---------------------------------------------------------------------------
# GET /medicos
# ---------------------------------------------------------------------------


class TestListarMedicos:
    def test_listar_medicos_vazio(self, client):
        response = client.get("/medicos")
        assert response.status_code == 200
        assert response.json() == []

    def test_listar_medicos_retorna_criados(self, client, representante_id):
        for i, prio in enumerate(["A", "B"]):
            client.post(
                "/medicos",
                json={
                    "nome": f"Dr. {i}",
                    "crm": f"CRM/SP-{i:04d}",
                    "especialidade": "Clínica",
                    "prioridade": prio,
                    "representante_id": representante_id,
                },
            )

        response = client.get("/medicos")
        assert response.status_code == 200
        assert len(response.json()) == 2

    def test_filtro_por_prioridade(self, client, representante_id):
        for i, prio in enumerate(["A", "B", "C"]):
            client.post(
                "/medicos",
                json={
                    "nome": f"Dr. Prio{prio}",
                    "crm": f"CRM/SP-P{i:04d}",
                    "especialidade": "Clínica",
                    "prioridade": prio,
                    "representante_id": representante_id,
                },
            )

        response = client.get("/medicos?prioridade=A")
        assert response.status_code == 200
        medicos = response.json()
        assert len(medicos) == 1
        assert medicos[0]["prioridade"] == "A"


# ---------------------------------------------------------------------------
# GET /medicos/{id}
# ---------------------------------------------------------------------------


class TestObterMedico:
    def test_obter_medico_existente(self, client, representante_id):
        created = client.post(
            "/medicos",
            json={
                "nome": "Dr. Detalhe",
                "crm": "CRM/SP-DET001",
                "especialidade": "Ortopedia",
                "prioridade": "C",
                "representante_id": representante_id,
            },
        ).json()

        response = client.get(f"/medicos/{created['id']}")
        assert response.status_code == 200
        assert response.json()["id"] == created["id"]

    def test_obter_medico_inexistente(self, client):
        response = client.get(f"/medicos/{uuid.uuid4()}")
        assert response.status_code == 404


# ---------------------------------------------------------------------------
# DELETE /medicos/{id} (soft delete)
# ---------------------------------------------------------------------------


class TestDeletarMedico:
    def test_soft_delete(self, client, representante_id):
        created = client.post(
            "/medicos",
            json={
                "nome": "Dr. Deletar",
                "crm": "CRM/SP-DEL001",
                "especialidade": "Clínica",
                "prioridade": "B",
                "representante_id": representante_id,
            },
        ).json()

        delete_resp = client.delete(f"/medicos/{created['id']}")
        assert delete_resp.status_code == 204

        # Should not appear in active list
        list_resp = client.get("/medicos")
        ids = [m["id"] for m in list_resp.json()]
        assert created["id"] not in ids

        # Should still be in inactive list
        inactive_resp = client.get("/medicos?ativo=false")
        inactive_ids = [m["id"] for m in inactive_resp.json()]
        assert created["id"] in inactive_ids


# ---------------------------------------------------------------------------
# POST /rotas/otimizar
# ---------------------------------------------------------------------------


class TestOtimizarRota:
    def _criar_medico_com_local_e_disponibilidade(
        self,
        client,
        representante_id: str,
        prioridade: str = "A",
        dia_semana: int = 0,
        crm_suffix: str = "001",
    ) -> dict:
        """Helper: create a doctor with one location and one availability."""
        medico = client.post(
            "/medicos",
            json={
                "nome": f"Dr. Rota {crm_suffix}",
                "crm": f"CRM/SP-ROTA{crm_suffix}",
                "especialidade": "Cardiologia",
                "prioridade": prioridade,
                "representante_id": representante_id,
            },
        ).json()

        local = client.post(
            f"/medicos/{medico['id']}/locais",
            json={
                "medico_id": medico["id"],
                "nome": f"Consultório {crm_suffix}",
                "endereco": f"Rua Teste, {crm_suffix}",
                "latitude": -23.5500 + float(crm_suffix) * 0.01,
                "longitude": -46.6300 + float(crm_suffix) * 0.01,
                "tipo": "consultorio",
            },
        ).json()

        client.post(
            f"/medicos/{medico['id']}/locais/{local['id']}/disponibilidades",
            json={
                "local_id": local["id"],
                "dia_semana": dia_semana,
                "hora_inicio": "08:00:00",
                "hora_fim": "17:00:00",
            },
        )

        return medico

    def test_otimizar_rota_retorna_visitas(self, client, representante_id):
        # 2026-03-30 is a Monday (weekday 0)
        self._criar_medico_com_local_e_disponibilidade(
            client, representante_id, prioridade="A", dia_semana=0, crm_suffix="001"
        )
        self._criar_medico_com_local_e_disponibilidade(
            client, representante_id, prioridade="B", dia_semana=0, crm_suffix="002"
        )

        response = client.post(
            "/rotas/otimizar",
            json={
                "representante_id": representante_id,
                "data": "2026-03-30",
            },
        )
        assert response.status_code == 201, response.text
        data = response.json()
        assert "rota_id" in data
        assert "visitas" in data
        assert len(data["visitas"]) == 2

    def test_otimizar_rota_sem_medicos_disponiveis(self, client, representante_id):
        # Doctor available only on Wednesday (2), but request for Monday (0)
        self._criar_medico_com_local_e_disponibilidade(
            client, representante_id, prioridade="A", dia_semana=2, crm_suffix="010"
        )

        response = client.post(
            "/rotas/otimizar",
            json={
                "representante_id": representante_id,
                "data": "2026-03-30",  # Monday
            },
        )
        assert response.status_code == 201
        data = response.json()
        assert data["visitas"] == []

    def test_otimizar_rota_com_filtro_medico_ids(self, client, representante_id):
        m1 = self._criar_medico_com_local_e_disponibilidade(
            client, representante_id, prioridade="A", dia_semana=0, crm_suffix="020"
        )
        self._criar_medico_com_local_e_disponibilidade(
            client, representante_id, prioridade="B", dia_semana=0, crm_suffix="021"
        )

        response = client.post(
            "/rotas/otimizar",
            json={
                "representante_id": representante_id,
                "data": "2026-03-30",
                "medico_ids": [m1["id"]],
            },
        )
        assert response.status_code == 201
        data = response.json()
        assert len(data["visitas"]) == 1
        assert data["visitas"][0]["medico_id"] == m1["id"]


# ---------------------------------------------------------------------------
# GET /rotas
# ---------------------------------------------------------------------------


class TestListarRotas:
    def test_listar_rotas_vazio(self, client):
        response = client.get("/rotas")
        assert response.status_code == 200
        assert response.json() == []


# ---------------------------------------------------------------------------
# PUT /rotas/{id}/visitas/{visita_id}/status
# ---------------------------------------------------------------------------


class TestAtualizarStatusVisita:
    def test_atualizar_status_visita(self, client, representante_id):
        medico = client.post(
            "/medicos",
            json={
                "nome": "Dr. Status",
                "crm": "CRM/SP-STATUS001",
                "especialidade": "Clínica",
                "prioridade": "A",
                "representante_id": representante_id,
            },
        ).json()

        local = client.post(
            f"/medicos/{medico['id']}/locais",
            json={
                "medico_id": medico["id"],
                "nome": "Local Status",
                "endereco": "Rua Status, 1",
                "latitude": -23.5500,
                "longitude": -46.6300,
                "tipo": "consultorio",
            },
        ).json()

        client.post(
            f"/medicos/{medico['id']}/locais/{local['id']}/disponibilidades",
            json={
                "local_id": local["id"],
                "dia_semana": 0,
                "hora_inicio": "08:00:00",
                "hora_fim": "17:00:00",
            },
        )

        rota_resp = client.post(
            "/rotas/otimizar",
            json={"representante_id": representante_id, "data": "2026-03-30"},
        ).json()

        rota_id = rota_resp["rota_id"]

        # Fetch the actual visita id from the rota detail endpoint
        rota_detail = client.get(f"/rotas/{rota_id}").json()
        visita_id = rota_detail["visitas"][0]["id"]

        status_resp = client.put(
            f"/rotas/{rota_id}/visitas/{visita_id}/status",
            json={"status_visita": "realizada", "observacao": "Médico atendeu."},
        )
        assert status_resp.status_code == 200
        updated = status_resp.json()
        assert updated["status_visita"] == "realizada"
        assert updated["observacao"] == "Médico atendeu."
