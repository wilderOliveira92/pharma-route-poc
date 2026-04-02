# Pharma Route — Otimizador de Visitas

POC de roteirização inteligente para representantes de vendas farmacêuticas.
Otimiza a sequência de visitas a médicos considerando localização, janelas de tempo e prioridade.

## Stack

| Camada | Tecnologia |
|--------|------------|
| Backend | FastAPI + Python 3.11 |
| Banco de dados | SQLite (arquivo local) |
| ORM | SQLAlchemy 2.0 |
| Distâncias | Haversine (embutida) + OSRM demo (HTTP, gratuito) |
| Frontend | React 18 + Vite |
| Mapas | React-Leaflet + OpenStreetMap |

Sem Docker, sem API keys, sem custos.

---

## Pré-requisitos

- Python 3.11+
- Node.js 18+
- pip

---

## Setup

### 1. Configurar variáveis de ambiente

```bash
cp .env.example .env
# Edite .env se necessário (os valores padrão já funcionam para dev local)
```

### 2. Backend

```bash
cd backend

# Instalar dependências
pip install -r requirements.txt

# Popular banco com 20 médicos fictícios em SP
python seed.py

# Iniciar servidor (http://localhost:8000)
uvicorn main:app --reload --port 8000
```

### 3. Frontend (outro terminal)

```bash
cd frontend

# Instalar dependências
npm install

# Iniciar dev server (http://localhost:5173)
npm run dev
```

Abra **http://localhost:5173** no navegador.

---

## Uso

1. Selecione uma data no campo superior
2. Marque os médicos que deseja visitar na lista à esquerda (ou mantenha todos)
3. Clique em **"Otimizar Rota"**
4. O mapa exibe a rota otimizada com numeração e polyline
5. No painel direito, atualize o status de cada visita conforme o dia avança

---

## API

Swagger disponível em **http://localhost:8000/docs**

Endpoints principais:

| Método | Rota | Descrição |
|--------|------|-----------|
| GET | `/medicos` | Listar médicos (filtros: prioridade, especialidade) |
| POST | `/medicos` | Cadastrar médico |
| GET | `/medicos/{id}/locais` | Locais de atendimento do médico |
| POST | `/rotas/otimizar` | Gerar rota otimizada |
| GET | `/rotas/{id}` | Detalhe da rota |
| PUT | `/rotas/{id}/visitas/{visita_id}/status` | Atualizar status da visita |

### Exemplo — otimizar rota

```bash
curl -X POST http://localhost:8000/rotas/otimizar \
  -H "Content-Type: application/json" \
  -d '{
    "representante_id": "<uuid-do-representante>",
    "data": "2026-04-07",
    "medico_ids": null
  }'
```

---

## Testes

```bash
cd backend
pytest tests/ -v
```

33 testes cobrindo:
- Cálculo de distância Haversine
- Algoritmo nearest-neighbor
- Filtragem por janela de tempo
- Endpoints CRUD (SQLite em memória)

---

## Estrutura de pastas

```
pharma-route-poc/
├── .env.example
├── README.md
├── CLAUDE.md                        ← instruções para o agente de IA
├── skills/
│   ├── pharma-domain/SKILL.md       ← contexto de domínio farmacêutico
│   └── vrp-optimizer/SKILL.md       ← contexto do otimizador VRP
├── backend/
│   ├── main.py                      ← FastAPI app
│   ├── database.py                  ← SQLite engine + session
│   ├── seed.py                      ← 20 médicos fictícios em SP
│   ├── requirements.txt
│   ├── models/                      ← SQLAlchemy 2.0 models
│   │   ├── representante.py
│   │   ├── medico.py
│   │   ├── local_atendimento.py
│   │   ├── disponibilidade.py
│   │   ├── visita.py
│   │   └── rota.py
│   ├── schemas/                     ← Pydantic v2 request/response
│   ├── routers/
│   │   ├── medicos.py
│   │   └── rotas.py
│   ├── optimizer/
│   │   ├── distance.py              ← Haversine + OSRM
│   │   └── route_optimizer.py       ← nearest-neighbor greedy
│   └── tests/
│       ├── test_optimizer.py
│       └── test_endpoints.py
└── frontend/
    ├── package.json
    ├── vite.config.js
    └── src/
        ├── main.jsx
        ├── App.jsx
        ├── App.css
        ├── api/
        │   └── client.js
        └── components/
            ├── MedicoList.jsx
            ├── RouteMap.jsx
            └── RotaResult.jsx
```

---

## Algoritmo de otimização

O otimizador usa **nearest-neighbor greedy** com restrições de janela de tempo:

1. Filtra médicos com disponibilidade no dia da semana solicitado
2. Ordena por prioridade: A → B → C
3. Começa no médico de maior prioridade mais próximo da origem
4. A cada passo, vai para o médico não visitado mais próximo
5. Descarta médicos cuja janela de tempo não comporta a chegada estimada (`hora_chegada + 20min > hora_fim`)
6. Velocidade média estimada: 30 km/h (tráfego SP)
7. Distâncias: tenta OSRM demo (rotas reais), fallback para Haversine

Para substituir por um algoritmo mais sofisticado (OR-Tools, 2-opt), edite `backend/optimizer/route_optimizer.py`.

---

## Evoluções futuras

- [ ] Autenticação JWT para múltiplos representantes
- [ ] Trocar SQLite por PostgreSQL (só mudar `DATABASE_URL`)
- [ ] Algoritmo 2-opt ou OR-Tools para rotas maiores
- [ ] Notificações push quando status de visita mudar
- [ ] Histórico de rotas por semana/mês
- [ ] Export PDF da rota do dia
