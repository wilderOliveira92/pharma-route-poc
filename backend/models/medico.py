import uuid
from datetime import datetime, timezone
from sqlalchemy import String, Boolean, DateTime, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship
from database import Base


class Medico(Base):
    __tablename__ = "medicos"

    id: Mapped[str] = mapped_column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    nome: Mapped[str] = mapped_column(String, nullable=False)
    crm: Mapped[str] = mapped_column(String, unique=True, nullable=False)
    especialidade: Mapped[str] = mapped_column(String, nullable=False)
    prioridade: Mapped[str] = mapped_column(String, nullable=False)  # 'A' | 'B' | 'C'
    representante_id: Mapped[str] = mapped_column(String, ForeignKey("representantes.id"), nullable=False)
    ativo: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    criado_em: Mapped[datetime] = mapped_column(DateTime, default=lambda: datetime.now(timezone.utc).replace(tzinfo=None), nullable=False)

    representante: Mapped["Representante"] = relationship("Representante", back_populates="medicos")
    locais: Mapped[list["LocalAtendimento"]] = relationship("LocalAtendimento", back_populates="medico")
    visitas: Mapped[list["Visita"]] = relationship("Visita", back_populates="medico")

    def __repr__(self) -> str:
        return f"<Medico id={self.id!r} nome={self.nome!r} crm={self.crm!r} prioridade={self.prioridade!r}>"
