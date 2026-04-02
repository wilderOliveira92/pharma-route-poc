"""
Unit tests for the optimizer module.

Tests:
  - Haversine distance calculation
  - Nearest-neighbor algorithm with mock data
  - Time-window filtering (skip doctor if arrival + 20min > hora_fim)
"""
from __future__ import annotations

import sys
import os
import datetime
import uuid
from unittest.mock import MagicMock, patch

# Allow imports from backend directory
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

import pytest

from optimizer.distance import distancia_euclidiana
from optimizer.route_optimizer import (
    RouteOptimizer,
    _janela_compativel,
    _adicionar_minutos,
    _tempo_deslocamento_minutos,
)


# ---------------------------------------------------------------------------
# Haversine / distancia_euclidiana tests
# ---------------------------------------------------------------------------


class TestDistanciaEuclidiana:
    def test_mesma_posicao_retorna_zero(self):
        dist = distancia_euclidiana(-23.55, -46.63, -23.55, -46.63)
        assert dist == pytest.approx(0.0, abs=1e-6)

    def test_sp_rj_aproximado(self):
        """São Paulo to Rio de Janeiro is roughly 360 km straight line."""
        dist = distancia_euclidiana(-23.5505, -46.6333, -22.9068, -43.1729)
        assert 350 < dist < 380

    def test_curta_distancia_bairros_sp(self):
        """Paulista to Ibirapuera is roughly 2-3 km."""
        dist = distancia_euclidiana(-23.5646, -46.6541, -23.5874, -46.6576)
        assert 1.5 < dist < 4.0

    def test_simetrico(self):
        """Distance A→B == Distance B→A."""
        d1 = distancia_euclidiana(-23.55, -46.63, -23.60, -46.68)
        d2 = distancia_euclidiana(-23.60, -46.68, -23.55, -46.63)
        assert d1 == pytest.approx(d2, rel=1e-9)

    def test_retorna_float(self):
        dist = distancia_euclidiana(-23.55, -46.63, -23.60, -46.68)
        assert isinstance(dist, float)


# ---------------------------------------------------------------------------
# Helper function tests
# ---------------------------------------------------------------------------


class TestHelpers:
    def test_adicionar_minutos(self):
        t = datetime.time(9, 0)
        result = _adicionar_minutos(t, 30)
        assert result == datetime.time(9, 30)

    def test_adicionar_minutos_atravessa_hora(self):
        t = datetime.time(11, 45)
        result = _adicionar_minutos(t, 30)
        assert result == datetime.time(12, 15)

    def test_tempo_deslocamento_minutos(self):
        # 15 km at 30 km/h = 30 minutes
        tempo = _tempo_deslocamento_minutos(15.0)
        assert tempo == pytest.approx(30.0)

    def test_janela_compativel_dentro(self):
        chegada = datetime.time(10, 0)
        hora_fim = datetime.time(10, 30)
        assert _janela_compativel(chegada, 20, hora_fim) is True

    def test_janela_compativel_exato(self):
        chegada = datetime.time(10, 0)
        hora_fim = datetime.time(10, 20)
        assert _janela_compativel(chegada, 20, hora_fim) is True

    def test_janela_incompativel(self):
        chegada = datetime.time(10, 5)
        hora_fim = datetime.time(10, 20)
        # 10:05 + 20 min = 10:25 > 10:20
        assert _janela_compativel(chegada, 20, hora_fim) is False

    def test_janela_chegada_apos_fim(self):
        chegada = datetime.time(11, 0)
        hora_fim = datetime.time(10, 30)
        assert _janela_compativel(chegada, 20, hora_fim) is False


# ---------------------------------------------------------------------------
# RouteOptimizer with mock data
# ---------------------------------------------------------------------------


def _make_medico(nome: str, prioridade: str, lat: float, lon: float, dia: int = 0):
    """Build a minimal mock Medico with one LocalAtendimento and one Disponibilidade."""
    medico_id = str(uuid.uuid4())
    local_id = str(uuid.uuid4())
    disp_id = str(uuid.uuid4())

    disp = MagicMock()
    disp.id = disp_id
    disp.dia_semana = dia
    disp.hora_inicio = datetime.time(8, 0)
    disp.hora_fim = datetime.time(17, 0)

    local = MagicMock()
    local.id = local_id
    local.nome = f"Local {nome}"
    local.endereco = f"Rua {nome}, 1"
    local.latitude = lat
    local.longitude = lon
    local.disponibilidades = [disp]

    medico = MagicMock()
    medico.id = medico_id
    medico.nome = nome
    medico.prioridade = prioridade
    medico.ativo = True
    medico.locais = [local]

    return medico


def _make_db_session(medicos: list, existing_visitas: list | None = None):
    """Build a mock SQLAlchemy Session."""
    db = MagicMock()
    existing_visitas = existing_visitas or []

    def execute_side_effect(stmt):
        result = MagicMock()
        # Distinguish between Medico and Visita queries by inspecting the stmt
        stmt_str = str(stmt)
        if "visitas" in stmt_str.lower():
            result.scalars.return_value.all.return_value = existing_visitas
        else:
            result.scalars.return_value.all.return_value = medicos
        return result

    db.execute.side_effect = execute_side_effect
    db.get.return_value = MagicMock(
        id="rota-mock",
        representante_id="rep-1",
        data_rota=datetime.date.today(),
        status="otimizada",
        distancia_total_km=0.0,
        tempo_total_minutos=0,
        criado_em=datetime.datetime.utcnow(),
    )
    return db


class TestRouteOptimizer:
    def test_tres_medicos_ordenados_por_prioridade(self):
        """Nearest-neighbor should start with A-priority doctor."""
        medico_a = _make_medico("MedicoA", "A", -23.5500, -46.6300, dia=0)
        medico_b = _make_medico("MedicoB", "B", -23.5600, -46.6400, dia=0)
        medico_c = _make_medico("MedicoC", "C", -23.5700, -46.6500, dia=0)

        db = _make_db_session([medico_a, medico_b, medico_c])
        optimizer = RouteOptimizer()
        data = datetime.date(2026, 3, 30)  # Monday = weekday 0

        resultado = optimizer.otimizar(
            representante_id="rep-1",
            data=data,
            db_session=db,
        )

        assert len(resultado["visitas"]) == 3
        # First visit must be the A-priority doctor
        assert resultado["visitas"][0]["medico_prioridade"] == "A"
        assert resultado["visitas"][0]["sequencia"] == 1

    def test_visitas_com_sequencia_incrementada(self):
        medico_a = _make_medico("Alpha", "A", -23.5500, -46.6300, dia=0)
        medico_b = _make_medico("Beta", "B", -23.5550, -46.6350, dia=0)

        db = _make_db_session([medico_a, medico_b])
        optimizer = RouteOptimizer()
        data = datetime.date(2026, 3, 30)

        resultado = optimizer.otimizar(
            representante_id="rep-1",
            data=data,
            db_session=db,
        )

        sequencias = [v["sequencia"] for v in resultado["visitas"]]
        assert sequencias == list(range(1, len(sequencias) + 1))

    def test_distancia_total_soma_distancias_individuais(self):
        medico_a = _make_medico("Alpha", "A", -23.5500, -46.6300, dia=0)
        medico_b = _make_medico("Beta", "B", -23.5600, -46.6400, dia=0)

        db = _make_db_session([medico_a, medico_b])
        optimizer = RouteOptimizer()
        data = datetime.date(2026, 3, 30)

        with patch("optimizer.route_optimizer.melhor_distancia") as mock_dist:
            mock_dist.return_value = 5.0
            resultado = optimizer.otimizar(
                representante_id="rep-1",
                data=data,
                db_session=db,
            )

        total = sum(v["distancia_km"] for v in resultado["visitas"])
        assert resultado["distancia_total_km"] == pytest.approx(total, abs=0.01)

    def test_filtro_por_dia_semana(self):
        """Doctor available only on Tuesday should not appear in a Monday route."""
        medico_a = _make_medico("Segunda", "A", -23.5500, -46.6300, dia=0)  # Monday
        medico_b = _make_medico("Terca", "B", -23.5600, -46.6400, dia=2)    # Wednesday

        db = _make_db_session([medico_a, medico_b])
        optimizer = RouteOptimizer()
        data = datetime.date(2026, 3, 30)  # Monday

        resultado = optimizer.otimizar(
            representante_id="rep-1",
            data=data,
            db_session=db,
        )

        # Only the Monday doctor should be included
        nomes = [v["medico_nome"] for v in resultado["visitas"]]
        assert "Segunda" in nomes
        assert "Terca" not in nomes


class TestTimeWindowFiltering:
    def test_skip_medico_fora_da_janela(self):
        """
        Doctor with a tight closing time (08:20) and the rep arriving late
        should be skipped.
        """
        medico_a = _make_medico("Principal", "A", -23.5500, -46.6300, dia=0)
        # Build a doctor with a window that closes too early
        medico_b_id = str(uuid.uuid4())
        local_b_id = str(uuid.uuid4())

        disp_b = MagicMock()
        disp_b.id = str(uuid.uuid4())
        disp_b.dia_semana = 0
        # Only 5-minute window — can never fit a 20-minute visit
        disp_b.hora_inicio = datetime.time(8, 0)
        disp_b.hora_fim = datetime.time(8, 5)

        local_b = MagicMock()
        local_b.id = local_b_id
        local_b.nome = "Local B"
        local_b.endereco = "Rua B, 1"
        local_b.latitude = -23.5600
        local_b.longitude = -46.6400
        local_b.disponibilidades = [disp_b]

        medico_b = MagicMock()
        medico_b.id = medico_b_id
        medico_b.nome = "MedicoJanelaFechada"
        medico_b.prioridade = "B"
        medico_b.ativo = True
        medico_b.locais = [local_b]

        db = _make_db_session([medico_a, medico_b])
        optimizer = RouteOptimizer()
        data = datetime.date(2026, 3, 30)

        resultado = optimizer.otimizar(
            representante_id="rep-1",
            data=data,
            db_session=db,
        )

        nomes = [v["medico_nome"] for v in resultado["visitas"]]
        assert "MedicoJanelaFechada" not in nomes
        assert "Principal" in nomes

    def test_visita_exatamente_no_limite_da_janela(self):
        """
        Arrival at 08:00 with hora_fim at 08:20 should succeed (exactly fits).
        """
        chegada = datetime.time(8, 0)
        hora_fim = datetime.time(8, 20)
        assert _janela_compativel(chegada, 20, hora_fim) is True

    def test_visita_um_minuto_apos_limite(self):
        """
        Arrival at 08:01 with hora_fim at 08:20 should fail (20 min won't fit).
        """
        chegada = datetime.time(8, 1)
        hora_fim = datetime.time(8, 20)
        assert _janela_compativel(chegada, 20, hora_fim) is False
