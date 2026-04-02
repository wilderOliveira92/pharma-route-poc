import uuid
from datetime import datetime, timezone
from sqlalchemy import String, Boolean, DateTime
from sqlalchemy.orm import Mapped, mapped_column, relationship
from database import Base


class Representante(Base):
    __tablename__ = "representantes"

    id: Mapped[str] = mapped_column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    nome: Mapped[str] = mapped_column(String, nullable=False)
    email: Mapped[str] = mapped_column(String, unique=True, nullable=False)
    regiao: Mapped[str] = mapped_column(String, nullable=False)
    ativo: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    criado_em: Mapped[datetime] = mapped_column(DateTime, default=lambda: datetime.now(timezone.utc).replace(tzinfo=None), nullable=False)

    medicos: Mapped[list["Medico"]] = relationship("Medico", back_populates="representante")
    visitas: Mapped[list["Visita"]] = relationship("Visita", back_populates="representante")
    rotas: Mapped[list["Rota"]] = relationship("Rota", back_populates="representante")

    def __repr__(self) -> str:
        return f"<Representante id={self.id!r} nome={self.nome!r} regiao={self.regiao!r}>"
