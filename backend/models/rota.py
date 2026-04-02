import uuid
import datetime
from datetime import timezone
from sqlalchemy import String, Integer, Float, Date, DateTime, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship
from database import Base


class Rota(Base):
    __tablename__ = "rotas"

    id: Mapped[str] = mapped_column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    representante_id: Mapped[str] = mapped_column(String, ForeignKey("representantes.id"), nullable=False)
    data_rota: Mapped[datetime.date] = mapped_column(Date, nullable=False)
    status: Mapped[str] = mapped_column(String, default="rascunho", nullable=False)
    distancia_total_km: Mapped[float | None] = mapped_column(Float, nullable=True)
    tempo_total_minutos: Mapped[int | None] = mapped_column(Integer, nullable=True)
    # Local de início da rota (ponto de partida do representante)
    local_inicio_endereco: Mapped[str | None] = mapped_column(String, nullable=True)
    local_inicio_latitude: Mapped[float | None] = mapped_column(Float, nullable=True)
    local_inicio_longitude: Mapped[float | None] = mapped_column(Float, nullable=True)
    criado_em: Mapped[datetime.datetime] = mapped_column(
        DateTime,
        default=lambda: datetime.datetime.now(timezone.utc).replace(tzinfo=None),
        nullable=False,
    )

    representante: Mapped["Representante"] = relationship("Representante", back_populates="rotas")
    visitas: Mapped[list["Visita"]] = relationship(
        "Visita",
        back_populates="rota",
        order_by="Visita.sequencia",
    )

    def __repr__(self) -> str:
        return (
            f"<Rota id={self.id!r} data={self.data_rota} "
            f"status={self.status!r} distancia={self.distancia_total_km}km>"
        )
