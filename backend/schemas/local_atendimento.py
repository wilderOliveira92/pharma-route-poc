from __future__ import annotations
from typing import Literal
from pydantic import BaseModel


class LocalAtendimentoBase(BaseModel):
    medico_id: str
    nome: str
    endereco: str
    latitude: float
    longitude: float
    tipo: Literal["consultorio", "hospital", "clinica", "ubs"]


class LocalAtendimentoCreate(LocalAtendimentoBase):
    pass


class LocalAtendimentoUpdate(BaseModel):
    nome: str | None = None
    endereco: str | None = None
    latitude: float | None = None
    longitude: float | None = None
    tipo: Literal["consultorio", "hospital", "clinica", "ubs"] | None = None


class LocalAtendimentoResponse(LocalAtendimentoBase):
    id: str

    model_config = {"from_attributes": True}
