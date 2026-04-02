"""
Route optimization and management endpoints.
"""
from __future__ import annotations

import datetime
from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy import select
from sqlalchemy.orm import Session

from database import get_db
from models.rota import Rota
from models.visita import Visita
from optimizer.route_optimizer import RouteOptimizer
from schemas.rota import OtimizarRotaRequest, RotaResponse
from schemas.visita import VisitaStatusUpdate, VisitaResponse

router = APIRouter(prefix="/rotas", tags=["rotas"])

_optimizer = RouteOptimizer()


# ---------------------------------------------------------------------------
# Route optimization
# ---------------------------------------------------------------------------


@router.post("/otimizar", status_code=201)
def otimizar_rota(
    payload: OtimizarRotaRequest,
    db: Session = Depends(get_db),
) -> dict:
    """
    Run the nearest-neighbor optimizer and persist the resulting Rota + Visitas.
    Returns the Rota with the ordered list of Visitas.

    Accepts optional starting point (local_inicio_*) to begin the route from a specific location.
    """
    resultado = _optimizer.otimizar(
        representante_id=payload.representante_id,
        data=payload.data,
        db_session=db,
        medico_ids=payload.medico_ids,
        local_inicio_endereco=payload.local_inicio_endereco,
        local_inicio_latitude=payload.local_inicio_latitude,
        local_inicio_longitude=payload.local_inicio_longitude,
        hora_inicio_jornada=payload.hora_inicio_jornada,
        hora_fim_jornada=payload.hora_fim_jornada,
    )

    if not resultado["rota_id"]:
        return {
            "mensagem": "Nenhum médico disponível para a data e representante informados.",
            "visitas": [],
            "distancia_total_km": 0.0,
            "tempo_total_minutos": 0,
        }

    # Reload the rota to return full relational data
    rota = db.get(Rota, resultado["rota_id"])
    return {
        "id": rota.id,
        "representante_id": rota.representante_id,
        "data": rota.data_rota.isoformat(),
        "data_rota": rota.data_rota.isoformat(),
        "status": rota.status,
        "distancia_total_km": rota.distancia_total_km,
        "distancia_total_metros": int((rota.distancia_total_km or 0) * 1000),
        "tempo_total_minutos": rota.tempo_total_minutos,
        "criado_em": rota.criado_em.isoformat(),
        "visitas": resultado["visitas"],
    }


# ---------------------------------------------------------------------------
# Rota retrieval
# ---------------------------------------------------------------------------


@router.get("", response_model=list[RotaResponse])
def listar_rotas(
    representante_id: Optional[str] = Query(None),
    data_inicio: Optional[datetime.date] = Query(None),
    data_fim: Optional[datetime.date] = Query(None),
    db: Session = Depends(get_db),
) -> list[RotaResponse]:
    stmt = select(Rota)
    if representante_id:
        stmt = stmt.where(Rota.representante_id == representante_id)
    if data_inicio:
        stmt = stmt.where(Rota.data_rota >= data_inicio)
    if data_fim:
        stmt = stmt.where(Rota.data_rota <= data_fim)
    stmt = stmt.order_by(Rota.data_rota.desc())
    return db.execute(stmt).scalars().all()


@router.get("/{rota_id}", response_model=RotaResponse)
def obter_rota(rota_id: str, db: Session = Depends(get_db)) -> RotaResponse:
    rota = db.get(Rota, rota_id)
    if not rota:
        raise HTTPException(status_code=404, detail="Rota não encontrada.")
    return rota


# ---------------------------------------------------------------------------
# Visit status update
# ---------------------------------------------------------------------------


@router.put("/{rota_id}/visitas/{visita_id}/status", response_model=VisitaResponse)
def atualizar_status_visita(
    rota_id: str,
    visita_id: str,
    payload: VisitaStatusUpdate,
    db: Session = Depends(get_db),
) -> VisitaResponse:
    rota = db.get(Rota, rota_id)
    if not rota:
        raise HTTPException(status_code=404, detail="Rota não encontrada.")

    visita = db.get(Visita, visita_id)
    if not visita or visita.rota_id != rota_id:
        raise HTTPException(
            status_code=404,
            detail="Visita não encontrada para esta rota.",
        )

    visita.status_visita = payload.status_visita
    if payload.observacao is not None:
        visita.observacao = payload.observacao
    db.commit()
    db.refresh(visita)
    return visita
