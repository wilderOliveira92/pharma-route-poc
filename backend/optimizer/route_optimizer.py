"""
Nearest-neighbor greedy route optimizer for pharmaceutical sales reps.

Business rules applied:
  - Only doctors with active availability on the given weekday are considered.
  - Priority order: A (visited 4x/month) > B (2x/month) > C (1x/month).
  - Nearest-neighbor heuristic: start at first unvisited A-priority doctor,
    always move to the closest unvisited next.
  - Time windows are strict: skip a doctor/location if
    estimated arrival + 20 min > hora_fim.
  - Travel speed assumed to be 30 km/h (São Paulo urban average).
  - A rep cannot visit the same doctor at the same location more than once per day.
"""
from __future__ import annotations

import datetime
import uuid
from datetime import timezone
from typing import Optional

from sqlalchemy import select
from sqlalchemy.orm import Session, selectinload

from models.medico import Medico
from models.local_atendimento import LocalAtendimento
from models.disponibilidade import Disponibilidade
from models.visita import Visita
from models.rota import Rota
from optimizer.distance import distancia_euclidiana

_VELOCIDADE_KMPH = 30.0          # RJ urban speed assumption
_DURACAO_VISITA_MIN = 20         # default visit duration
_HORA_INICIO_JORNADA = datetime.time(8, 0)  # rep starts at 08:00

_PRIORIDADE_ORDEM = {"A": 0, "B": 1, "C": 2}


def _tempo_deslocamento_minutos(distancia_km: float) -> float:
    return (distancia_km / _VELOCIDADE_KMPH) * 60.0


def _adicionar_minutos(t: datetime.time, minutos: float) -> datetime.time:
    dt = datetime.datetime.combine(datetime.date.today(), t)
    dt += datetime.timedelta(minutes=minutos)
    return dt.time()


def _janela_compativel(
    hora_chegada: datetime.time,
    duracao_min: int,
    hora_fim: datetime.time,
) -> bool:
    """Return True if arrival + duration fits within the closing time."""
    hora_saida = _adicionar_minutos(hora_chegada, duracao_min)
    return hora_saida <= hora_fim


class RouteOptimizer:
    """Nearest-neighbor greedy route optimizer."""

    def otimizar(
        self,
        representante_id: str,
        data: datetime.date,
        db_session: Session,
        medico_ids: Optional[list[str]] = None,
        local_inicio_endereco: Optional[str] = None,
        local_inicio_latitude: Optional[float] = None,
        local_inicio_longitude: Optional[float] = None,
        hora_inicio_jornada: Optional[datetime.time] = None,
        hora_fim_jornada: Optional[datetime.time] = None,
    ) -> dict:
        """
        Build an optimized route for a sales rep on a given date.

        Returns a dict with:
          - rota_id: str
          - visitas: list of visit dicts (ordered by sequence)
          - distancia_total_km: float
          - tempo_total_minutos: int
        """
        dia_semana = data.weekday()  # 0=Mon .. 6=Sun

        # 1. Fetch all active doctors assigned to the rep with availability today
        # Eager-load locais and disponibilidades to avoid N+1 queries
        stmt = (
            select(Medico)
            .where(Medico.representante_id == representante_id)
            .where(Medico.ativo == True)  # noqa: E712
            .options(
                selectinload(Medico.locais).selectinload(LocalAtendimento.disponibilidades)
            )
        )
        medicos = db_session.execute(stmt).scalars().all()

        if medico_ids:
            medicos = [m for m in medicos if m.id in medico_ids]

        # 2. Gather candidate (medico, local, disponibilidade) tuples
        candidatos: list[dict] = []
        visited_pairs: set[tuple[str, str]] = set()  # (medico_id, local_id) visited today

        # Check existing visits today to enforce the uniqueness rule.
        # Only "realizada" visits block re-optimization — "agendada" visits are
        # just planned and would accumulate across repeated optimize calls.
        existing_stmt = select(Visita).where(
            Visita.representante_id == representante_id,
            Visita.data_visita == data,
            Visita.status_visita == "realizada",
        )
        existing_visitas = db_session.execute(existing_stmt).scalars().all()
        for v in existing_visitas:
            visited_pairs.add((v.medico_id, v.local_id))

        for medico in medicos:
            for local in medico.locais:
                if (medico.id, local.id) in visited_pairs:
                    continue
                for disp in local.disponibilidades:
                    if disp.dia_semana == dia_semana:
                        candidatos.append(
                            {
                                "medico": medico,
                                "local": local,
                                "disponibilidade": disp,
                            }
                        )
                        break  # one availability window per local per day is enough

        if not candidatos:
            return {
                "rota_id": None,
                "visitas": [],
                "distancia_total_km": 0.0,
                "tempo_total_minutos": 0,
            }

        # 3. Sort by priority then by doctor name (deterministic)
        candidatos.sort(
            key=lambda c: (
                _PRIORIDADE_ORDEM.get(c["medico"].prioridade, 99),
                c["medico"].nome,
            )
        )

        # 4. Pre-compute distance matrix (Haversine, O(N²) in-memory — no HTTP calls)
        n = len(candidatos)
        lats = [c["local"].latitude for c in candidatos]
        lons = [c["local"].longitude for c in candidatos]

        # dist_matrix[i][j] = distance from candidatos[i] to candidatos[j]
        dist_matrix: list[list[float]] = [
            [distancia_euclidiana(lats[i], lons[i], lats[j], lons[j]) for j in range(n)]
            for i in range(n)
        ]

        # Starting point distances (from starting coords to each candidate)
        if local_inicio_latitude is not None and local_inicio_longitude is not None:
            start_lat, start_lon = local_inicio_latitude, local_inicio_longitude
        else:
            start_lat, start_lon = lats[0], lons[0]

        dist_from_start = [
            distancia_euclidiana(start_lat, start_lon, lats[j], lons[j])
            for j in range(n)
        ]

        # Nearest-neighbor greedy selection
        hora_atual = hora_inicio_jornada if hora_inicio_jornada is not None else _HORA_INICIO_JORNADA
        visitados: list[dict] = []
        remaining = list(range(n))  # indices into candidatos
        current_idx: Optional[int] = None  # None = at starting point
        distancia_total = 0.0

        while remaining:
            melhor_pos = None
            melhor_dist = float("inf")

            for pos, idx in enumerate(remaining):
                dist = dist_from_start[idx] if current_idx is None else dist_matrix[current_idx][idx]
                if dist < melhor_dist:
                    melhor_dist = dist
                    melhor_pos = pos

            if melhor_pos is None:
                break

            orig_idx = remaining.pop(melhor_pos)
            proximo = candidatos[orig_idx]
            disp = proximo["disponibilidade"]

            # Estimate arrival: travel time + current clock
            tempo_viagem = _tempo_deslocamento_minutos(melhor_dist)
            hora_chegada_est = _adicionar_minutos(hora_atual, tempo_viagem)

            # Must arrive within the window
            hora_chegada_real = max(hora_chegada_est, disp.hora_inicio)

            if not _janela_compativel(hora_chegada_real, _DURACAO_VISITA_MIN, disp.hora_fim):
                continue  # outside doctor's availability window

            if hora_fim_jornada is not None and not _janela_compativel(
                hora_chegada_real, _DURACAO_VISITA_MIN, hora_fim_jornada
            ):
                continue  # visit would end after rep's workday

            distancia_total += melhor_dist
            visitados.append(
                {
                    "medico": proximo["medico"],
                    "local": proximo["local"],
                    "disponibilidade": disp,
                    "hora_chegada": hora_chegada_real,
                    "distancia_km": melhor_dist,
                }
            )
            current_idx = orig_idx
            hora_atual = _adicionar_minutos(hora_chegada_real, _DURACAO_VISITA_MIN)

        # 5. Persist Rota and Visitas
        rota = Rota(
            id=str(uuid.uuid4()),
            representante_id=representante_id,
            data_rota=data,
            status="otimizada",
            distancia_total_km=round(distancia_total, 3),
            tempo_total_minutos=self._calcular_tempo_total(visitados),
            local_inicio_endereco=local_inicio_endereco,
            local_inicio_latitude=local_inicio_latitude,
            local_inicio_longitude=local_inicio_longitude,
            criado_em=datetime.datetime.now(timezone.utc).replace(tzinfo=None),
        )
        db_session.add(rota)

        visitas_resultado: list[dict] = []
        for seq, item in enumerate(visitados, start=1):
            visita_id = str(uuid.uuid4())
            visita = Visita(
                id=visita_id,
                rota_id=rota.id,
                representante_id=representante_id,
                medico_id=item["medico"].id,
                local_id=item["local"].id,
                data_visita=data,
                hora_chegada=item["hora_chegada"],
                duracao_minutos=_DURACAO_VISITA_MIN,
                status_visita="agendada",
                sequencia=seq,
            )
            db_session.add(visita)

            visitas_resultado.append(
                {
                    "id": visita_id,
                    "sequencia": seq,
                    "medico_id": item["medico"].id,
                    "medico_nome": item["medico"].nome,
                    "medico_prioridade": item["medico"].prioridade,
                    "local_id": item["local"].id,
                    "local_nome": item["local"].nome,
                    "local_endereco": item["local"].endereco,
                    "latitude": item["local"].latitude,
                    "longitude": item["local"].longitude,
                    "hora_chegada": item["hora_chegada"].strftime("%H:%M"),
                    "distancia_km": round(item["distancia_km"], 3),
                    "janela_inicio": item["disponibilidade"].hora_inicio.strftime("%H:%M"),
                    "janela_fim": item["disponibilidade"].hora_fim.strftime("%H:%M"),
                }
            )

        db_session.commit()
        db_session.refresh(rota)

        # Calculate total minutes from first arrival to last departure
        if visitados:
            primeiro_inicio = visitados[0]["hora_chegada"]
            ultimo_fim = _adicionar_minutos(visitados[-1]["hora_chegada"], _DURACAO_VISITA_MIN)
            dt_inicio = datetime.datetime.combine(data, primeiro_inicio)
            dt_fim = datetime.datetime.combine(data, ultimo_fim)
            tempo_total = int((dt_fim - dt_inicio).total_seconds() // 60)
        else:
            tempo_total = 0

        return {
            "rota_id": rota.id,
            "visitas": visitas_resultado,
            "distancia_total_km": round(distancia_total, 3),
            "tempo_total_minutos": tempo_total,
        }

    def _calcular_tempo_total(self, visitados: list[dict]) -> int:
        if not visitados:
            return 0
        primeiro_inicio = visitados[0]["hora_chegada"]
        ultimo_fim = _adicionar_minutos(visitados[-1]["hora_chegada"], _DURACAO_VISITA_MIN)
        dt_inicio = datetime.datetime.combine(datetime.date.today(), primeiro_inicio)
        dt_fim = datetime.datetime.combine(datetime.date.today(), ultimo_fim)
        return int((dt_fim - dt_inicio).total_seconds() // 60)
