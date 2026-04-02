"""
Quick test to verify the fixes work
"""
import sys
import datetime
sys.path.insert(0, 'backend')

from database import SessionLocal
from models.medico import Medico
from models.disponibilidade import Disponibilidade
from models.local_atendimento import LocalAtendimento
from sqlalchemy import select

db = SessionLocal()

# Test 1: Filter medicos by weekday availability
print("=" * 70)
print("TEST 1: Filter médicos by date/weekday availability")
print("=" * 70)

# Pick a date (e.g., Monday = 0, Tuesday = 1, etc)
test_date = datetime.date(2026, 4, 6)  # This is a Monday
dia_semana = test_date.weekday()  # 0 = Monday

print(f"\nSelected date: {test_date} (weekday: {dia_semana})")

# Get all medicos
all_medicos = db.execute(select(Medico)).scalars().all()
print(f"Total medicos in DB: {len(all_medicos)}")

# Filter by availability on that weekday
medicos_with_availability = []
for medico in all_medicos:
    stmt = select(Disponibilidade).join(
        LocalAtendimento,
        Disponibilidade.local_id == LocalAtendimento.id
    ).where(
        LocalAtendimento.medico_id == medico.id,
        Disponibilidade.dia_semana == dia_semana
    )
    if db.execute(stmt).scalars().first():
        medicos_with_availability.append(medico)

print(f"Médicos with availability on {test_date.strftime('%A')}: {len(medicos_with_availability)}")

if medicos_with_availability:
    print(f"\n✓ First 3 médicos with availability:")
    for m in medicos_with_availability[:3]:
        print(f"  - {m.nome} (Prioridade: {m.prioridade})")

# Test 2: Check status field in Visita
print("\n" + "=" * 70)
print("TEST 2: Check Visita status field")
print("=" * 70)

from models.visita import Visita

all_visitas = db.execute(select(Visita)).scalars().all()
if all_visitas:
    v = all_visitas[0]
    print(f"\n✓ First visita found:")
    print(f"  - ID: {v.id}")
    print(f"  - Status field: status_visita = '{v.status_visita}'")
    print(f"  - Has 'status' field: {hasattr(v, 'status')}")
else:
    print("\nℹ No visitas found (expected if no routes created yet)")

print("\n" + "=" * 70)
print("✅ TESTS COMPLETE")
print("=" * 70)

db.close()
