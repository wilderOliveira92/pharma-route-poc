# CLAUDE.md — pharma-route-poc

## O projeto
Sistema de roteirização inteligente para representantes de vendas farmacêuticas.
Permite otimizar a sequência de visitas a médicos considerando disponibilidade,
localização e janelas de tempo.

## Stack 100% gratuita (POC)

| Camada | Tecnologia | Por quê |
|--------|------------|---------|
| Backend | FastAPI + Python 3.11 | Rápido, tipado, Swagger automático |
| Banco de dados | SQLite (arquivo local) | Zero configuração, sem servidor |
| ORM | SQLAlchemy 2.0 | Migrations fáceis, troca para Postgres depois |
| Migrations | Alembic | Versionamento do schema |
| Cache distâncias | Dicionário Python em memória | Sem Redis na POC |
| Distâncias | Euclidiana × 1.4 (embutida) | Sem Google Maps API |
| Roteamento avançado | OSRM demo server (HTTP, gratuito) | Quando quiser distâncias reais |
| Frontend | React + Vite | Dev server embutido |
| Mapas | React-Leaflet + OpenStreetMap | Gratuito, sem API key |
| Containerização | Nenhuma na POC | Rodar direto com uvicorn + vite |
| Testes | pytest | Padrão Python |

## Estrutura de pastas
```
pharma-route-poc/
├── CLAUDE.md                    ← este arquivo
├── skills/
│   ├── pharma-domain/SKILL.md   ← ler SEMPRE ao tocar em modelos/seeds/endpoints
│   └── vrp-optimizer/SKILL.md   ← ler SEMPRE ao tocar no otimizador
├── backend/
│   ├── main.py
│   ├── database.py              ← SQLite engine + session
│   ├── models/
│   │   ├── representante.py
│   │   ├── medico.py
│   │   ├── local_atendimento.py
│   │   ├── disponibilidade.py
│   │   ├── visita.py
│   │   └── rota.py
│   ├── schemas/                 ← Pydantic request/response
│   ├── routers/
│   │   ├── medicos.py
│   │   ├── disponibilidades.py
│   │   └── rotas.py
│   ├── optimizer/
│   │   ├── route_optimizer.py   ← algoritmo principal
│   │   └── distance.py          ← euclidiana + OSRM
│   ├── seed.py                  ← 20 médicos fictícios no RJ
│   ├── requirements.txt
│   └── tests/
│       ├── test_optimizer.py
│       └── test_endpoints.py
└── frontend/
    ├── src/
    │   ├── App.jsx
    │   ├── components/
    │   │   ├── MedicoList.jsx
    │   │   ├── RouteMap.jsx      ← react-leaflet
    │   │   └── RotaResult.jsx
    │   └── api/
    │       └── client.js
    ├── package.json
    └── vite.config.js
```

## Como rodar (sem Docker)

```bash
# Backend
cd backend
pip install -r requirements.txt
python seed.py          # popular banco pela primeira vez
uvicorn main:app --reload --port 8000

# Frontend (outro terminal)
cd frontend
npm install
npm run dev             # http://localhost:5173
```

## Comandos úteis no Claude Code

```bash
# Ver Swagger da API
open http://localhost:8000/docs

# Rodar testes
cd backend && pytest tests/ -v

# Resetar banco
rm backend/pharma.db && python backend/seed.py
```

## Skills obrigatórias

Antes de qualquer tarefa, verifique se deve ler uma skill:

| Tarefa | Skill a ler |
|--------|------------|
| Modelos, seeds, endpoints de médicos/visitas | `skills/pharma-domain/SKILL.md` |
| Qualquer coisa no `optimizer/` | `skills/vrp-optimizer/SKILL.md` |
| Componentes de mapa no frontend | nenhuma skill ainda |

## Modelo padrão por tipo de tarefa

| Tipo | Modelo |
|------|--------|
| Boilerplate, CRUD, seed, config | `claude-haiku-4-5-20251001` |
| Endpoints, frontend, debug, integração | `claude-sonnet-4-5` |
| Algoritmo de otimização, revisão de arquitetura | `claude-opus-4-6` |