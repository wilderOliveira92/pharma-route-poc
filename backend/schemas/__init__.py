from schemas.representante import (
    RepresentanteCreate,
    RepresentanteUpdate,
    RepresentanteResponse,
)
from schemas.medico import (
    MedicoCreate,
    MedicoUpdate,
    MedicoResponse,
)
from schemas.local_atendimento import (
    LocalAtendimentoCreate,
    LocalAtendimentoUpdate,
    LocalAtendimentoResponse,
)
from schemas.disponibilidade import (
    DisponibilidadeCreate,
    DisponibilidadeUpdate,
    DisponibilidadeResponse,
)
from schemas.visita import (
    VisitaCreate,
    VisitaUpdate,
    VisitaStatusUpdate,
    VisitaResponse,
)
from schemas.rota import (
    RotaCreate,
    RotaUpdate,
    RotaResponse,
    OtimizarRotaRequest,
)

__all__ = [
    "RepresentanteCreate",
    "RepresentanteUpdate",
    "RepresentanteResponse",
    "MedicoCreate",
    "MedicoUpdate",
    "MedicoResponse",
    "LocalAtendimentoCreate",
    "LocalAtendimentoUpdate",
    "LocalAtendimentoResponse",
    "DisponibilidadeCreate",
    "DisponibilidadeUpdate",
    "DisponibilidadeResponse",
    "VisitaCreate",
    "VisitaUpdate",
    "VisitaStatusUpdate",
    "VisitaResponse",
    "RotaCreate",
    "RotaUpdate",
    "RotaResponse",
    "OtimizarRotaRequest",
]
