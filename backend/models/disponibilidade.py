import uuid
from sqlalchemy import String, Integer, Time, ForeignKey, CheckConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship
from database import Base
import datetime


class Disponibilidade(Base):
    __tablename__ = "disponibilidades"
    __table_args__ = (
        # Enforce that the time window is at least 20 minutes
        # SQLite stores time as text, so we use strftime comparison
        CheckConstraint(
            "hora_fim > hora_inicio",
            name="ck_disponibilidade_janela_positiva",
        ),
    )

    id: Mapped[str] = mapped_column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    local_id: Mapped[str] = mapped_column(String, ForeignKey("locais_atendimento.id"), nullable=False)
    dia_semana: Mapped[int] = mapped_column(Integer, nullable=False)  # 0=Mon .. 6=Sun
    hora_inicio: Mapped[datetime.time] = mapped_column(Time, nullable=False)
    hora_fim: Mapped[datetime.time] = mapped_column(Time, nullable=False)

    local: Mapped["LocalAtendimento"] = relationship("LocalAtendimento", back_populates="disponibilidades")

    def janela_minutos(self) -> int:
        """Returns the total window size in minutes."""
        inicio = datetime.datetime.combine(datetime.date.today(), self.hora_inicio)
        fim = datetime.datetime.combine(datetime.date.today(), self.hora_fim)
        return int((fim - inicio).total_seconds() // 60)

    def __repr__(self) -> str:
        return (
            f"<Disponibilidade id={self.id!r} dia_semana={self.dia_semana} "
            f"{self.hora_inicio}-{self.hora_fim}>"
        )
