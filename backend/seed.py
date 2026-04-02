"""
Seed script: populates the database with realistic Rio de Janeiro data.

Run with:
    cd backend && python seed.py
"""
from __future__ import annotations

import sys
import os
import uuid
import datetime

# Allow imports from the backend directory
sys.path.insert(0, os.path.dirname(__file__))

from database import SessionLocal, Base, engine
import models  # noqa: F401 — registers all models with Base.metadata

from models.representante import Representante
from models.medico import Medico
from models.local_atendimento import LocalAtendimento
from models.disponibilidade import Disponibilidade


# ---------------------------------------------------------------------------
# Seed data
# ---------------------------------------------------------------------------

REPRESENTANTE = {
    "id": str(uuid.uuid4()),
    "nome": "Ana Paula Ferreira",
    "email": "ana.ferreira@pharma.com",
    "regiao": "Rio de Janeiro - Zona Sul",
}

# 20 médicos: 8 priority A, 8 priority B, 4 priority C
# Realistic RJ neighborhoods with lat/lon centred around -22.90, -43.17
MEDICOS_DATA = [
    # Priority A — cardiologists, oncologists, endocrinologists (index 0–7)
    {
        "nome": "Dr. Carlos Eduardo Martins",
        "crm": "CRM/RJ-123456",
        "especialidade": "Cardiologia",
        "prioridade": "A",
        "locais": [
            {
                "nome": "Clínica CardioVida Copacabana",
                "endereco": "Av. Nossa Sra. de Copacabana, 680, Copacabana, Rio de Janeiro",
                "latitude": -22.9711,
                "longitude": -43.1863,
                "tipo": "clinica",
                "disponibilidades": [
                    {"dia_semana": 0, "hora_inicio": datetime.time(8, 0), "hora_fim": datetime.time(12, 0)},
                    {"dia_semana": 2, "hora_inicio": datetime.time(14, 0), "hora_fim": datetime.time(18, 0)},
                    {"dia_semana": 4, "hora_inicio": datetime.time(8, 0), "hora_fim": datetime.time(12, 0)},
                ],
            },
            {
                "nome": "Hospital Copa D'Or",
                "endereco": "Rua Figueiredo de Magalhães, 875, Copacabana, Rio de Janeiro",
                "latitude": -22.9660,
                "longitude": -43.1810,
                "tipo": "hospital",
                "disponibilidades": [
                    {"dia_semana": 1, "hora_inicio": datetime.time(9, 0), "hora_fim": datetime.time(13, 0)},
                    {"dia_semana": 3, "hora_inicio": datetime.time(9, 0), "hora_fim": datetime.time(13, 0)},
                ],
            },
        ],
    },
    {
        "nome": "Dra. Fernanda Lima Souza",
        "crm": "CRM/RJ-234567",
        "especialidade": "Oncologia",
        "prioridade": "A",
        "locais": [
            {
                "nome": "Instituto Nacional de Câncer (INCA)",
                "endereco": "Praça Cruz Vermelha, 23, Centro, Rio de Janeiro",
                "latitude": -22.9100,
                "longitude": -43.1820,
                "tipo": "hospital",
                "disponibilidades": [
                    {"dia_semana": 1, "hora_inicio": datetime.time(7, 0), "hora_fim": datetime.time(11, 0)},
                    {"dia_semana": 3, "hora_inicio": datetime.time(7, 0), "hora_fim": datetime.time(11, 0)},
                    {"dia_semana": 5, "hora_inicio": datetime.time(8, 0), "hora_fim": datetime.time(12, 0)},
                ],
            },
        ],
    },
    {
        "nome": "Dr. Roberto Alves Neto",
        "crm": "CRM/RJ-345678",
        "especialidade": "Endocrinologia",
        "prioridade": "A",
        "locais": [
            {
                "nome": "Consultório Dr. Roberto Alves",
                "endereco": "Rua Visconde de Pirajá, 572, Ipanema, Rio de Janeiro",
                "latitude": -22.9838,
                "longitude": -43.2045,
                "tipo": "consultorio",
                "disponibilidades": [
                    {"dia_semana": 0, "hora_inicio": datetime.time(9, 0), "hora_fim": datetime.time(13, 0)},
                    {"dia_semana": 2, "hora_inicio": datetime.time(9, 0), "hora_fim": datetime.time(13, 0)},
                    {"dia_semana": 4, "hora_inicio": datetime.time(14, 0), "hora_fim": datetime.time(18, 0)},
                ],
            },
            {
                "nome": "Clínica Endocrin Leblon",
                "endereco": "Av. Ataulfo de Paiva, 135, Leblon, Rio de Janeiro",
                "latitude": -22.9845,
                "longitude": -43.2240,
                "tipo": "clinica",
                "disponibilidades": [
                    {"dia_semana": 1, "hora_inicio": datetime.time(8, 30), "hora_fim": datetime.time(12, 30)},
                    {"dia_semana": 3, "hora_inicio": datetime.time(14, 0), "hora_fim": datetime.time(17, 0)},
                ],
            },
        ],
    },
    {
        "nome": "Dra. Patrícia Gonçalves",
        "crm": "CRM/RJ-456789",
        "especialidade": "Cardiologia",
        "prioridade": "A",
        "locais": [
            {
                "nome": "Hospital Samaritano Botafogo",
                "endereco": "Rua Bambina, 98, Botafogo, Rio de Janeiro",
                "latitude": -22.9528,
                "longitude": -43.1870,
                "tipo": "hospital",
                "disponibilidades": [
                    {"dia_semana": 0, "hora_inicio": datetime.time(8, 0), "hora_fim": datetime.time(12, 0)},
                    {"dia_semana": 2, "hora_inicio": datetime.time(8, 0), "hora_fim": datetime.time(12, 0)},
                    {"dia_semana": 4, "hora_inicio": datetime.time(8, 0), "hora_fim": datetime.time(12, 0)},
                ],
            },
        ],
    },
    {
        "nome": "Dr. Marcelo Cunha",
        "crm": "CRM/RJ-567890",
        "especialidade": "Oncologia",
        "prioridade": "A",
        "locais": [
            {
                "nome": "Hospital Federal da Lagoa",
                "endereco": "Rua Jardim Botânico, 501, Jardim Botânico, Rio de Janeiro",
                "latitude": -22.9670,
                "longitude": -43.2130,
                "tipo": "hospital",
                "disponibilidades": [
                    {"dia_semana": 1, "hora_inicio": datetime.time(13, 0), "hora_fim": datetime.time(17, 0)},
                    {"dia_semana": 3, "hora_inicio": datetime.time(13, 0), "hora_fim": datetime.time(17, 0)},
                ],
            },
            {
                "nome": "Clínica Oncológica da Tijuca",
                "endereco": "Rua Conde de Bonfim, 370, Tijuca, Rio de Janeiro",
                "latitude": -22.9250,
                "longitude": -43.2330,
                "tipo": "clinica",
                "disponibilidades": [
                    {"dia_semana": 5, "hora_inicio": datetime.time(9, 0), "hora_fim": datetime.time(13, 0)},
                ],
            },
        ],
    },
    {
        "nome": "Dra. Camila Torres",
        "crm": "CRM/RJ-678901",
        "especialidade": "Endocrinologia",
        "prioridade": "A",
        "locais": [
            {
                "nome": "Clínica Metabólica Barra",
                "endereco": "Av. das Américas, 3500, Barra da Tijuca, Rio de Janeiro",
                "latitude": -22.9990,
                "longitude": -43.3650,
                "tipo": "clinica",
                "disponibilidades": [
                    {"dia_semana": 0, "hora_inicio": datetime.time(8, 0), "hora_fim": datetime.time(12, 0)},
                    {"dia_semana": 2, "hora_inicio": datetime.time(14, 0), "hora_fim": datetime.time(18, 0)},
                    {"dia_semana": 4, "hora_inicio": datetime.time(8, 0), "hora_fim": datetime.time(11, 0)},
                ],
            },
        ],
    },
    {
        "nome": "Dr. Eduardo Pires",
        "crm": "CRM/RJ-789012",
        "especialidade": "Cardiologia",
        "prioridade": "A",
        "locais": [
            {
                "nome": "Consultório Cardiológico Flamengo",
                "endereco": "Rua do Catete, 311, Flamengo, Rio de Janeiro",
                "latitude": -22.9268,
                "longitude": -43.1762,
                "tipo": "consultorio",
                "disponibilidades": [
                    {"dia_semana": 1, "hora_inicio": datetime.time(8, 0), "hora_fim": datetime.time(12, 0)},
                    {"dia_semana": 3, "hora_inicio": datetime.time(8, 0), "hora_fim": datetime.time(12, 0)},
                    {"dia_semana": 5, "hora_inicio": datetime.time(8, 0), "hora_fim": datetime.time(11, 0)},
                ],
            },
            {
                "nome": "UBS Catete",
                "endereco": "Rua Pedro Américo, 32, Catete, Rio de Janeiro",
                "latitude": -22.9282,
                "longitude": -43.1778,
                "tipo": "ubs",
                "disponibilidades": [
                    {"dia_semana": 2, "hora_inicio": datetime.time(7, 0), "hora_fim": datetime.time(11, 0)},
                ],
            },
        ],
    },
    {
        "nome": "Dra. Juliana Mota",
        "crm": "CRM/RJ-890123",
        "especialidade": "Oncologia",
        "prioridade": "A",
        "locais": [
            {
                "nome": "Centro Oncológico de Niterói",
                "endereco": "Rua Marquês de Paraná, 303, Centro, Niterói",
                "latitude": -22.8953,
                "longitude": -43.1244,
                "tipo": "clinica",
                "disponibilidades": [
                    {"dia_semana": 0, "hora_inicio": datetime.time(9, 0), "hora_fim": datetime.time(13, 0)},
                    {"dia_semana": 2, "hora_inicio": datetime.time(9, 0), "hora_fim": datetime.time(13, 0)},
                    {"dia_semana": 4, "hora_inicio": datetime.time(9, 0), "hora_fim": datetime.time(13, 0)},
                ],
            },
        ],
    },
    # Priority B — general practitioners, neurologists, gastroenterologists (index 8–15)
    {
        "nome": "Dr. André Carvalho",
        "crm": "CRM/RJ-901234",
        "especialidade": "Clínica Médica",
        "prioridade": "B",
        "locais": [
            {
                "nome": "UBS Laranjeiras",
                "endereco": "Rua das Laranjeiras, 488, Laranjeiras, Rio de Janeiro",
                "latitude": -22.9350,
                "longitude": -43.1847,
                "tipo": "ubs",
                "disponibilidades": [
                    {"dia_semana": 0, "hora_inicio": datetime.time(7, 0), "hora_fim": datetime.time(11, 0)},
                    {"dia_semana": 3, "hora_inicio": datetime.time(13, 0), "hora_fim": datetime.time(17, 0)},
                ],
            },
        ],
    },
    {
        "nome": "Dra. Letícia Araújo",
        "crm": "CRM/RJ-012345",
        "especialidade": "Neurologia",
        "prioridade": "B",
        "locais": [
            {
                "nome": "Instituto de Neurologia Deolindo Couto (UFRJ)",
                "endereco": "Av. Venceslau Brás, 95, Botafogo, Rio de Janeiro",
                "latitude": -22.9510,
                "longitude": -43.1750,
                "tipo": "hospital",
                "disponibilidades": [
                    {"dia_semana": 1, "hora_inicio": datetime.time(10, 0), "hora_fim": datetime.time(14, 0)},
                    {"dia_semana": 4, "hora_inicio": datetime.time(10, 0), "hora_fim": datetime.time(14, 0)},
                ],
            },
            {
                "nome": "Consultório Dra. Letícia Araújo",
                "endereco": "Rua Voluntários da Pátria, 445, Botafogo, Rio de Janeiro",
                "latitude": -22.9517,
                "longitude": -43.1868,
                "tipo": "consultorio",
                "disponibilidades": [
                    {"dia_semana": 2, "hora_inicio": datetime.time(8, 0), "hora_fim": datetime.time(12, 0)},
                ],
            },
        ],
    },
    {
        "nome": "Dr. Felipe Mendes",
        "crm": "CRM/RJ-111222",
        "especialidade": "Gastroenterologia",
        "prioridade": "B",
        "locais": [
            {
                "nome": "Clínica GastroRio",
                "endereco": "Rua São Clemente, 303, Botafogo, Rio de Janeiro",
                "latitude": -22.9488,
                "longitude": -43.1920,
                "tipo": "clinica",
                "disponibilidades": [
                    {"dia_semana": 0, "hora_inicio": datetime.time(14, 0), "hora_fim": datetime.time(18, 0)},
                    {"dia_semana": 2, "hora_inicio": datetime.time(8, 0), "hora_fim": datetime.time(12, 0)},
                    {"dia_semana": 4, "hora_inicio": datetime.time(14, 0), "hora_fim": datetime.time(18, 0)},
                ],
            },
        ],
    },
    {
        "nome": "Dra. Renata Lopes",
        "crm": "CRM/RJ-222333",
        "especialidade": "Clínica Médica",
        "prioridade": "B",
        "locais": [
            {
                "nome": "UBS Humaitá",
                "endereco": "Rua Humaitá, 275, Humaitá, Rio de Janeiro",
                "latitude": -22.9560,
                "longitude": -43.1980,
                "tipo": "ubs",
                "disponibilidades": [
                    {"dia_semana": 1, "hora_inicio": datetime.time(7, 0), "hora_fim": datetime.time(11, 0)},
                    {"dia_semana": 3, "hora_inicio": datetime.time(7, 0), "hora_fim": datetime.time(11, 0)},
                ],
            },
        ],
    },
    {
        "nome": "Dr. Thiago Nascimento",
        "crm": "CRM/RJ-333444",
        "especialidade": "Neurologia",
        "prioridade": "B",
        "locais": [
            {
                "nome": "Clínica Neurológica Méier",
                "endereco": "Rua Dias da Cruz, 190, Méier, Rio de Janeiro",
                "latitude": -22.9026,
                "longitude": -43.2810,
                "tipo": "clinica",
                "disponibilidades": [
                    {"dia_semana": 0, "hora_inicio": datetime.time(8, 0), "hora_fim": datetime.time(12, 0)},
                    {"dia_semana": 2, "hora_inicio": datetime.time(14, 0), "hora_fim": datetime.time(18, 0)},
                ],
            },
        ],
    },
    {
        "nome": "Dra. Simone Ribeiro",
        "crm": "CRM/RJ-444555",
        "especialidade": "Gastroenterologia",
        "prioridade": "B",
        "locais": [
            {
                "nome": "Consultório Dra. Simone",
                "endereco": "Rua General San Martin, 505, Leblon, Rio de Janeiro",
                "latitude": -22.9810,
                "longitude": -43.2260,
                "tipo": "consultorio",
                "disponibilidades": [
                    {"dia_semana": 1, "hora_inicio": datetime.time(9, 0), "hora_fim": datetime.time(13, 0)},
                    {"dia_semana": 3, "hora_inicio": datetime.time(9, 0), "hora_fim": datetime.time(13, 0)},
                    {"dia_semana": 5, "hora_inicio": datetime.time(9, 0), "hora_fim": datetime.time(12, 0)},
                ],
            },
        ],
    },
    {
        "nome": "Dr. Luciano Ferraz",
        "crm": "CRM/RJ-555666",
        "especialidade": "Clínica Médica",
        "prioridade": "B",
        "locais": [
            {
                "nome": "Hospital Municipal Souza Aguiar",
                "endereco": "Praça da República, 111, Centro, Rio de Janeiro",
                "latitude": -22.9086,
                "longitude": -43.1870,
                "tipo": "hospital",
                "disponibilidades": [
                    {"dia_semana": 2, "hora_inicio": datetime.time(7, 30), "hora_fim": datetime.time(11, 30)},
                    {"dia_semana": 4, "hora_inicio": datetime.time(7, 30), "hora_fim": datetime.time(11, 30)},
                ],
            },
            {
                "nome": "Consultório Dr. Luciano",
                "endereco": "Rua da Glória, 190, Glória, Rio de Janeiro",
                "latitude": -22.9210,
                "longitude": -43.1770,
                "tipo": "consultorio",
                "disponibilidades": [
                    {"dia_semana": 0, "hora_inicio": datetime.time(13, 0), "hora_fim": datetime.time(17, 0)},
                ],
            },
        ],
    },
    {
        "nome": "Dra. Beatriz Costa",
        "crm": "CRM/RJ-666777",
        "especialidade": "Neurologia",
        "prioridade": "B",
        "locais": [
            {
                "nome": "Clínica NeuroGávea",
                "endereco": "Rua Marquês de São Vicente, 225, Gávea, Rio de Janeiro",
                "latitude": -22.9790,
                "longitude": -43.2320,
                "tipo": "clinica",
                "disponibilidades": [
                    {"dia_semana": 1, "hora_inicio": datetime.time(14, 0), "hora_fim": datetime.time(18, 0)},
                    {"dia_semana": 3, "hora_inicio": datetime.time(14, 0), "hora_fim": datetime.time(18, 0)},
                    {"dia_semana": 5, "hora_inicio": datetime.time(8, 0), "hora_fim": datetime.time(12, 0)},
                ],
            },
        ],
    },
    # Priority C — other specialties (index 16–19)
    {
        "nome": "Dr. Henrique Fonseca",
        "crm": "CRM/RJ-777888",
        "especialidade": "Ortopedia",
        "prioridade": "C",
        "locais": [
            {
                "nome": "Consultório Dr. Henrique Fonseca",
                "endereco": "Rua Real Grandeza, 108, Botafogo, Rio de Janeiro",
                "latitude": -22.9530,
                "longitude": -43.1950,
                "tipo": "consultorio",
                "disponibilidades": [
                    {"dia_semana": 0, "hora_inicio": datetime.time(9, 0), "hora_fim": datetime.time(13, 0)},
                    {"dia_semana": 4, "hora_inicio": datetime.time(9, 0), "hora_fim": datetime.time(13, 0)},
                ],
            },
        ],
    },
    {
        "nome": "Dra. Maria Clara Santos",
        "crm": "CRM/RJ-888999",
        "especialidade": "Dermatologia",
        "prioridade": "C",
        "locais": [
            {
                "nome": "Clínica DermaRio",
                "endereco": "Rua Siqueira Campos, 43, Copacabana, Rio de Janeiro",
                "latitude": -22.9640,
                "longitude": -43.1780,
                "tipo": "clinica",
                "disponibilidades": [
                    {"dia_semana": 2, "hora_inicio": datetime.time(10, 0), "hora_fim": datetime.time(14, 0)},
                    {"dia_semana": 5, "hora_inicio": datetime.time(10, 0), "hora_fim": datetime.time(13, 0)},
                ],
            },
            {
                "nome": "Hospital São Lucas Copacabana",
                "endereco": "Rua Barata Ribeiro, 489, Copacabana, Rio de Janeiro",
                "latitude": -22.9650,
                "longitude": -43.1790,
                "tipo": "hospital",
                "disponibilidades": [
                    {"dia_semana": 1, "hora_inicio": datetime.time(7, 0), "hora_fim": datetime.time(10, 0)},
                ],
            },
        ],
    },
    {
        "nome": "Dr. Rodrigo Braga",
        "crm": "CRM/RJ-999000",
        "especialidade": "Psiquiatria",
        "prioridade": "C",
        "locais": [
            {
                "nome": "Consultório Dr. Rodrigo Braga",
                "endereco": "Rua Tonelero, 350, Copacabana, Rio de Janeiro",
                "latitude": -22.9630,
                "longitude": -43.1838,
                "tipo": "consultorio",
                "disponibilidades": [
                    {"dia_semana": 3, "hora_inicio": datetime.time(9, 0), "hora_fim": datetime.time(13, 0)},
                ],
            },
        ],
    },
    {
        "nome": "Dra. Vanessa Moreira",
        "crm": "CRM/RJ-100200",
        "especialidade": "Reumatologia",
        "prioridade": "C",
        "locais": [
            {
                "nome": "Clínica Reumatológica Tijuca",
                "endereco": "Rua Haddock Lobo, 369, Tijuca, Rio de Janeiro",
                "latitude": -22.9209,
                "longitude": -43.2376,
                "tipo": "clinica",
                "disponibilidades": [
                    {"dia_semana": 0, "hora_inicio": datetime.time(14, 0), "hora_fim": datetime.time(17, 0)},
                    {"dia_semana": 2, "hora_inicio": datetime.time(8, 0), "hora_fim": datetime.time(12, 0)},
                ],
            },
        ],
    },
]


# ---------------------------------------------------------------------------
# Seed function
# ---------------------------------------------------------------------------


def seed() -> None:
    Base.metadata.create_all(bind=engine)
    db = SessionLocal()

    try:
        # Check if already seeded
        from sqlalchemy import select
        existing = db.execute(select(Representante)).scalars().first()
        if existing:
            print("Database already seeded. Skipping.")
            return

        # Create representante
        rep = Representante(
            id=REPRESENTANTE["id"],
            nome=REPRESENTANTE["nome"],
            email=REPRESENTANTE["email"],
            regiao=REPRESENTANTE["regiao"],
        )
        db.add(rep)
        db.flush()

        # Create medicos, locais and disponibilidades
        for m_data in MEDICOS_DATA:
            locais_data = m_data.pop("locais")
            medico = Medico(
                id=str(uuid.uuid4()),
                representante_id=rep.id,
                nome=m_data["nome"],
                crm=m_data["crm"],
                especialidade=m_data["especialidade"],
                prioridade=m_data["prioridade"],
            )
            db.add(medico)
            db.flush()

            for l_data in locais_data:
                disps_data = l_data.pop("disponibilidades")
                local = LocalAtendimento(
                    id=str(uuid.uuid4()),
                    medico_id=medico.id,
                    nome=l_data["nome"],
                    endereco=l_data["endereco"],
                    latitude=l_data["latitude"],
                    longitude=l_data["longitude"],
                    tipo=l_data["tipo"],
                )
                db.add(local)
                db.flush()

                for d_data in disps_data:
                    disp = Disponibilidade(
                        id=str(uuid.uuid4()),
                        local_id=local.id,
                        dia_semana=d_data["dia_semana"],
                        hora_inicio=d_data["hora_inicio"],
                        hora_fim=d_data["hora_fim"],
                    )
                    db.add(disp)

        db.commit()
        print(
            f"Seeded: 1 representante, {len(MEDICOS_DATA)} médicos "
            f"with their locais and disponibilidades."
        )
    except Exception as e:
        db.rollback()
        print(f"Error during seeding: {e}")
        raise
    finally:
        db.close()


if __name__ == "__main__":
    seed()
