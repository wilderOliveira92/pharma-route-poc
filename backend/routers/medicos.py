"""
CRUD endpoints for Medico, LocalAtendimento, and Disponibilidade.
"""
from __future__ import annotations

import uuid
import datetime
from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, Query
from fastapi.responses import Response
from sqlalchemy import select, exists
from sqlalchemy.orm import Session

from database import get_db
from models.medico import Medico
from models.local_atendimento import LocalAtendimento
from models.disponibilidade import Disponibilidade
from schemas.medico import MedicoCreate, MedicoUpdate, MedicoResponse
from schemas.local_atendimento import LocalAtendimentoCreate, LocalAtendimentoResponse
from schemas.disponibilidade import DisponibilidadeCreate, DisponibilidadeResponse

router = APIRouter(prefix="/medicos", tags=["medicos"])


# ---------------------------------------------------------------------------
# Medicos CRUD
# ---------------------------------------------------------------------------


@router.get("", response_model=list[MedicoResponse])
def listar_medicos(
    prioridade: Optional[str] = Query(None, description="Filtrar por prioridade (A, B ou C)"),
    especialidade: Optional[str] = Query(None, description="Filtrar por especialidade"),
    rep_id: Optional[str] = Query(None, description="Filtrar por representante_id"),
    data: Optional[str] = Query(None, description="Filtrar por data (YYYY-MM-DD): retorna apenas médicos com disponibilidade nesse dia"),
    ativo: bool = Query(True, description="Mostrar apenas médicos ativos"),
    db: Session = Depends(get_db),
) -> list[MedicoResponse]:
    stmt = select(Medico).where(Medico.ativo == ativo)
    if prioridade:
        stmt = stmt.where(Medico.prioridade == prioridade.upper())
    if especialidade:
        stmt = stmt.where(Medico.especialidade.ilike(f"%{especialidade}%"))
    if rep_id:
        stmt = stmt.where(Medico.representante_id == rep_id)

    if data:
        try:
            target_date = datetime.datetime.strptime(data, "%Y-%m-%d").date()
            dia_semana = target_date.weekday()  # 0=Monday, 6=Sunday
            stmt = stmt.where(
                exists(
                    select(Disponibilidade.id)
                    .join(LocalAtendimento, Disponibilidade.local_id == LocalAtendimento.id)
                    .where(
                        LocalAtendimento.medico_id == Medico.id,
                        Disponibilidade.dia_semana == dia_semana,
                    )
                )
            )
        except ValueError:
            pass

    return db.execute(stmt).scalars().all()


@router.post("", response_model=MedicoResponse, status_code=201)
def criar_medico(payload: MedicoCreate, db: Session = Depends(get_db)) -> MedicoResponse:
    medico = Medico(
        id=str(uuid.uuid4()),
        **payload.model_dump(),
    )
    db.add(medico)
    db.commit()
    db.refresh(medico)
    return medico


@router.get("/{medico_id}", response_model=MedicoResponse)
def obter_medico(medico_id: str, db: Session = Depends(get_db)) -> MedicoResponse:
    medico = db.get(Medico, medico_id)
    if not medico:
        raise HTTPException(status_code=404, detail="Médico não encontrado.")
    return medico


@router.put("/{medico_id}", response_model=MedicoResponse)
def atualizar_medico(
    medico_id: str,
    payload: MedicoUpdate,
    db: Session = Depends(get_db),
) -> MedicoResponse:
    medico = db.get(Medico, medico_id)
    if not medico:
        raise HTTPException(status_code=404, detail="Médico não encontrado.")
    for field, value in payload.model_dump(exclude_unset=True).items():
        setattr(medico, field, value)
    db.commit()
    db.refresh(medico)
    return medico


@router.delete("/{medico_id}", status_code=204, response_class=Response)
def deletar_medico(medico_id: str, db: Session = Depends(get_db)) -> Response:
    """Soft delete: sets ativo=False."""
    medico = db.get(Medico, medico_id)
    if not medico:
        raise HTTPException(status_code=404, detail="Médico não encontrado.")
    medico.ativo = False
    db.commit()
    return Response(status_code=204)


# ---------------------------------------------------------------------------
# Locais de Atendimento
# ---------------------------------------------------------------------------


@router.get("/{medico_id}/locais", response_model=list[LocalAtendimentoResponse])
def listar_locais(medico_id: str, db: Session = Depends(get_db)) -> list[LocalAtendimentoResponse]:
    medico = db.get(Medico, medico_id)
    if not medico:
        raise HTTPException(status_code=404, detail="Médico não encontrado.")
    stmt = select(LocalAtendimento).where(LocalAtendimento.medico_id == medico_id)
    return db.execute(stmt).scalars().all()


@router.post("/{medico_id}/locais", response_model=LocalAtendimentoResponse, status_code=201)
def adicionar_local(
    medico_id: str,
    payload: LocalAtendimentoCreate,
    db: Session = Depends(get_db),
) -> LocalAtendimentoResponse:
    medico = db.get(Medico, medico_id)
    if not medico:
        raise HTTPException(status_code=404, detail="Médico não encontrado.")
    # Ensure medico_id in path matches payload
    local = LocalAtendimento(
        id=str(uuid.uuid4()),
        medico_id=medico_id,
        nome=payload.nome,
        endereco=payload.endereco,
        latitude=payload.latitude,
        longitude=payload.longitude,
        tipo=payload.tipo,
    )
    db.add(local)
    db.commit()
    db.refresh(local)
    return local


# ---------------------------------------------------------------------------
# Disponibilidades
# ---------------------------------------------------------------------------


@router.post(
    "/{medico_id}/locais/{local_id}/disponibilidades",
    response_model=DisponibilidadeResponse,
    status_code=201,
)
def adicionar_disponibilidade(
    medico_id: str,
    local_id: str,
    payload: DisponibilidadeCreate,
    db: Session = Depends(get_db),
) -> DisponibilidadeResponse:
    # Validate local belongs to medico
    local = db.get(LocalAtendimento, local_id)
    if not local or local.medico_id != medico_id:
        raise HTTPException(
            status_code=404,
            detail="Local de atendimento não encontrado para este médico.",
        )
    disponibilidade = Disponibilidade(
        id=str(uuid.uuid4()),
        local_id=local_id,
        dia_semana=payload.dia_semana,
        hora_inicio=payload.hora_inicio,
        hora_fim=payload.hora_fim,
    )
    db.add(disponibilidade)
    db.commit()
    db.refresh(disponibilidade)
    return disponibilidade
