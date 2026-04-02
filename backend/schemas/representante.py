from __future__ import annotations
from datetime import datetime
from pydantic import BaseModel, EmailStr


class RepresentanteBase(BaseModel):
    nome: str
    email: str
    regiao: str


class RepresentanteCreate(RepresentanteBase):
    pass


class RepresentanteUpdate(BaseModel):
    nome: str | None = None
    email: str | None = None
    regiao: str | None = None
    ativo: bool | None = None


class RepresentanteResponse(RepresentanteBase):
    id: str
    ativo: bool
    criado_em: datetime

    model_config = {"from_attributes": True}
