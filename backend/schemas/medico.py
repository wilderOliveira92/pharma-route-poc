from __future__ import annotations
from datetime import datetime
from typing import Literal
from pydantic import BaseModel


class MedicoBase(BaseModel):
    nome: str
    crm: str
    especialidade: str
    prioridade: Literal["A", "B", "C"]
    representante_id: str


class MedicoCreate(MedicoBase):
    pass


class MedicoUpdate(BaseModel):
    nome: str | None = None
    crm: str | None = None
    especialidade: str | None = None
    prioridade: Literal["A", "B", "C"] | None = None
    representante_id: str | None = None
    ativo: bool | None = None


class MedicoResponse(MedicoBase):
    id: str
    ativo: bool
    criado_em: datetime

    model_config = {"from_attributes": True}
