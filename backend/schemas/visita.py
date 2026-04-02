from __future__ import annotations
from datetime import date, time
from typing import Literal
from pydantic import BaseModel


class VisitaBase(BaseModel):
    representante_id: str
    medico_id: str
    local_id: str
    data_visita: date
    hora_chegada: time | None = None
    duracao_minutos: int = 20
    status_visita: Literal["agendada", "realizada", "cancelada", "nao_encontrado"] = "agendada"
    observacao: str | None = None
    sequencia: int | None = None


class VisitaCreate(VisitaBase):
    rota_id: str | None = None


class VisitaUpdate(BaseModel):
    hora_chegada: time | None = None
    duracao_minutos: int | None = None
    status_visita: Literal["agendada", "realizada", "cancelada", "nao_encontrado"] | None = None
    observacao: str | None = None
    sequencia: int | None = None


class VisitaStatusUpdate(BaseModel):
    status_visita: Literal["agendada", "realizada", "cancelada", "nao_encontrado"]
    observacao: str | None = None


class VisitaResponse(VisitaBase):
    id: str
    rota_id: str | None = None

    model_config = {"from_attributes": True}
