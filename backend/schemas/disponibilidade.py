from __future__ import annotations
from datetime import time
from pydantic import BaseModel, model_validator


class DisponibilidadeBase(BaseModel):
    local_id: str
    dia_semana: int  # 0=Mon .. 6=Sun
    hora_inicio: time
    hora_fim: time

    @model_validator(mode="after")
    def validar_janela_minima(self) -> "DisponibilidadeBase":
        from datetime import datetime, date
        inicio = datetime.combine(date.today(), self.hora_inicio)
        fim = datetime.combine(date.today(), self.hora_fim)
        diff = (fim - inicio).total_seconds() / 60
        if diff < 20:
            raise ValueError("A janela de atendimento deve ser de no mínimo 20 minutos.")
        return self


class DisponibilidadeCreate(DisponibilidadeBase):
    pass


class DisponibilidadeUpdate(BaseModel):
    dia_semana: int | None = None
    hora_inicio: time | None = None
    hora_fim: time | None = None


class DisponibilidadeResponse(DisponibilidadeBase):
    id: str

    model_config = {"from_attributes": True}
