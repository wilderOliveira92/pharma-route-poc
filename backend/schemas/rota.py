from __future__ import annotations
from datetime import date, datetime, time
from pydantic import BaseModel
from schemas.visita import VisitaResponse


class RotaBase(BaseModel):
    representante_id: str
    data_rota: date
    status: str = "rascunho"
    distancia_total_km: float | None = None
    tempo_total_minutos: int | None = None


class RotaCreate(RotaBase):
    pass


class RotaUpdate(BaseModel):
    status: str | None = None
    distancia_total_km: float | None = None
    tempo_total_minutos: int | None = None


class RotaResponse(RotaBase):
    id: str
    criado_em: datetime
    visitas: list[VisitaResponse] = []
    distancia_total_metros: int | None = None
    data: str | None = None  # ISO format string for API responses

    model_config = {"from_attributes": True}


class OtimizarRotaRequest(BaseModel):
    representante_id: str
    data: date
    medico_ids: list[str] | None = None
    # Ponto de partida da rota
    local_inicio_endereco: str | None = None
    local_inicio_latitude: float | None = None
    local_inicio_longitude: float | None = None
    # Horário de início da jornada (default 08:00)
    hora_inicio_jornada: time | None = None
    # Horário limite de fim da jornada (sem default — sem limite se não informado)
    hora_fim_jornada: time | None = None
