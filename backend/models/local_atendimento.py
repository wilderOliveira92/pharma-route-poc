import uuid
from sqlalchemy import String, Float, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship
from database import Base


class LocalAtendimento(Base):
    __tablename__ = "locais_atendimento"

    id: Mapped[str] = mapped_column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    medico_id: Mapped[str] = mapped_column(String, ForeignKey("medicos.id"), nullable=False)
    nome: Mapped[str] = mapped_column(String, nullable=False)
    endereco: Mapped[str] = mapped_column(String, nullable=False)
    latitude: Mapped[float] = mapped_column(Float, nullable=False)
    longitude: Mapped[float] = mapped_column(Float, nullable=False)
    tipo: Mapped[str] = mapped_column(String, nullable=False)  # 'consultorio'|'hospital'|'clinica'|'ubs'

    medico: Mapped["Medico"] = relationship("Medico", back_populates="locais")
    disponibilidades: Mapped[list["Disponibilidade"]] = relationship("Disponibilidade", back_populates="local")
    visitas: Mapped[list["Visita"]] = relationship("Visita", back_populates="local")

    def __repr__(self) -> str:
        return f"<LocalAtendimento id={self.id!r} nome={self.nome!r} tipo={self.tipo!r}>"
