import uuid
import datetime
from sqlalchemy import String, Integer, Date, Time, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship
from database import Base


class Visita(Base):
    __tablename__ = "visitas"

    id: Mapped[str] = mapped_column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    rota_id: Mapped[str | None] = mapped_column(String, ForeignKey("rotas.id"), nullable=True)
    representante_id: Mapped[str] = mapped_column(String, ForeignKey("representantes.id"), nullable=False)
    medico_id: Mapped[str] = mapped_column(String, ForeignKey("medicos.id"), nullable=False)
    local_id: Mapped[str] = mapped_column(String, ForeignKey("locais_atendimento.id"), nullable=False)
    data_visita: Mapped[datetime.date] = mapped_column(Date, nullable=False)
    hora_chegada: Mapped[datetime.time | None] = mapped_column(Time, nullable=True)
    duracao_minutos: Mapped[int] = mapped_column(Integer, default=20, nullable=False)
    status_visita: Mapped[str] = mapped_column(String, default="agendada", nullable=False)
    # 'agendada' | 'realizada' | 'cancelada' | 'nao_encontrado'
    observacao: Mapped[str | None] = mapped_column(String, nullable=True)
    sequencia: Mapped[int | None] = mapped_column(Integer, nullable=True)

    rota: Mapped["Rota | None"] = relationship("Rota", back_populates="visitas")
    representante: Mapped["Representante"] = relationship("Representante", back_populates="visitas")
    medico: Mapped["Medico"] = relationship("Medico", back_populates="visitas")
    local: Mapped["LocalAtendimento"] = relationship("LocalAtendimento", back_populates="visitas")

    def __repr__(self) -> str:
        return (
            f"<Visita id={self.id!r} data={self.data_visita} "
            f"status={self.status_visita!r} seq={self.sequencia}>"
        )
