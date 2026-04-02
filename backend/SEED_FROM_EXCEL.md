# Carregando dados do Excel

## Visão geral

O script `seed_from_excel.py` carrega dados de médicos do arquivo `Painel 2025.xlsx` e popula o banco de dados SQLite com:

- **Médicos**: nome, CRM, especialidade
- **Locais de atendimento**: endereço, bairro, latitude, longitude (via Nominatim)
- **Disponibilidades**: horários de atendimento por dia da semana

## Formato esperado do Excel

O arquivo `Painel 2025.xlsx` deve ter as seguintes colunas:

| Col | Nome | Descrição |
|-----|------|-----------|
| 1 | SETOR | **Cor do fundo = prioridade**: <br>🟠 Laranja = Prioridade A (prioritário) <br>Branco/outro = Prioridade B |
| 2 | CRM | Identificador do médico (obrigatório) |
| 3 | NOME | Nome completo (obrigatório) |
| 4 | ESPECIALIDADE | Ex: "CRD" (cardiologia), "PED" (pediatria), "CLG" (clínica geral) |
| 5 | ENDEREÇO | Rua e número |
| 7 | BAIRRO | Bairro do Rio de Janeiro |
| 9 | SEGUNDA | Horário de disponibilidade na segunda (ex: "14x17" = 14:00-17:00) |
| 10 | TERÇA | Horário na terça |
| 11 | QUARTA | Horário na quarta |
| 12 | QUINTA | Horário na quinta |
| 13 | SEXTA | Horário na sexta |

### Prioridade (coluna SETOR - formatação)

A coluna **SETOR** não é usada pelo valor, mas pela **cor de fundo da célula**:

- 🟠 **Laranja** → Prioridade **A** (médicos prioritários)
- **Branco/sem cor** → Prioridade **B** (médicos comuns)

O script detecta automaticamente tons de laranja (RGB com R > 200, 100 ≤ G ≤ 200, B < 100).

### Formato de horários

Use o formato `HHxHH` (maiúsculas ou minúsculas):
- `14x17` → 14:00 até 17:00
- `9x11` → 09:00 até 11:00
- `9x12` → 09:00 até 12:00

Se a célula estiver vazia, aquele dia não terá disponibilidade.

## Como usar

### 1. Preparar o ambiente

```bash
cd backend
pip install -r requirements.txt
```

### 2. Resetar banco (opcional)

Para limpar o banco anterior:

```bash
rm pharma.db
```

### 3. Rodar o script

```bash
python seed_from_excel.py
```

O script:
- Lê `../Painel 2025.xlsx`
- Para cada médico com disponibilidade, resolve endereço → lat/lon via **Nominatim** (gratuito)
- Cria médicos, locais e disponibilidades no banco
- Loga cada médico criado com suas coordenadas
- Exibe relatório final

### Exemplo de saída

```
2026-04-01 14:30:45,281 - INFO - Loaded 179 médicos from Excel
2026-04-01 14:33:05,686 - INFO - ✓ EDUARDO PASTORELLI DE OLIVEIRA (RJ0937126) at -22.9699, -43.1840
...
=== SEEDING COMPLETE ===
Representante: 1
Médicos created: 179
  ├─ Priority A (orange): 63
  └─ Priority B (other): 116
Médicos skipped (geocoding failed): 1
Locais created: 179
Disponibilidades created: 389
```

## Notas importantes

### Detecção de cores (Prioridade)

O script usa **openpyxl** para ler as cores das células da coluna SETOR:

```python
def is_orange_color(hex_color: str) -> bool:
    # Detecta laranja: R > 200, 100 ≤ G ≤ 200, B < 100
    r = int(color[0:2], 16)
    g = int(color[2:4], 16)
    b = int(color[4:6], 16)
    return r > 200 and 100 <= g <= 200 and b < 100
```

**Cores reconhecidas como laranja:**
- `FFA500` (laranja padrão)
- `FFB366` (laranja claro)
- `FF9900` (laranja escuro)
- E variações próximas

Se usar um tom de laranja diferente, pode precisar ajustar a fórmula RGB no script.

### Rate limiting

O Nominatim tem limite de ~1 requisição/segundo. O script espera 1s entre cada geocoding para evitar bloqueio. Com 179 médicos, leva ~3 minutos.

### Falhas de geocoding

Se um endereço não puder ser resolvido:
- O médico é pulado (logged como warning)
- Nenhuma rota será calculada para esse médico
- Revise o endereço/bairro no Excel

Exemplo:
```
2026-04-01 14:34:14,879 - WARNING - Could not geocode MARIA BERNADETE TEIXEIRA... at PRAIA DO FLAMENGO, CATETE — skipping
```

### Representante padrão

Um representante padrão é criado automaticamente:
- Nome: "Representante Padrão"
- Email: "rep@pharma.com"
- Região: "Rio de Janeiro"

Para alterar, edite as constantes no topo de `seed_from_excel.py`.

### Especialidades

O script mantém a especialidade do Excel (ex: "CRD", "PED", "CLG") conforme é.

Para mapear para especialidades padrão, edite a função `load_medicos_from_excel()`.

### Prioridade detectada por cor

A prioridade é **automaticamente detectada** pela cor da célula SETOR:
- 🟠 **Laranja** = Prioridade A
- **Branco/sem cor** = Prioridade B

Se não detectar a cor corretamente:
1. Verifique se a célula tem fundo sólido (não gradiente)
2. Se usar Excel em português, salve como `.xlsx` padrão (não xls)
3. Teste a cor com Python:
```python
from seed_from_excel import is_orange_color
is_orange_color("FFA500")  # True
is_orange_color("FFFFFF")  # False
```

### Tipo de local padrão

Todos os locais são criados como **"consultorio"**.

Para mudar, edite a linha:
```python
tipo="consultorio",  # Default type
```

## Troubleshooting

### Erro: "No module named 'openpyxl'"

Instale as dependências:
```bash
pip install -r requirements.txt
```

### Erro: "File not found: .../Painel 2025.xlsx"

Certifique-se de que:
- O arquivo está na pasta raiz do projeto (`/home/wilder/projetos/pharma-route-poc/`)
- O nome exato é `Painel 2025.xlsx` (maiúsculas e espaço)

### Nenhum médico foi criado

Verifique:
1. Tem dados nas colunas SEGUNDA-SEXTA?
2. Os horários estão no formato `14x17`?
3. O Excel tem mais de 2 linhas (header + dados)?

Use o script de debug em Python:
```python
from seed_from_excel import load_medicos_from_excel
medicos = load_medicos_from_excel("../Painel 2025.xlsx")
print(f"Loaded {len(medicos)} médicos")
for m in medicos[:3]:
    print(m)
```

### Lentidão

O script é lento por design (rate limiting do Nominatim). ~3 minutos para 179 médicos é normal.

Para acelerar (não recomendado), altere:
```python
time.sleep(1)  # Reduza para 0.5
```

Mas risco bloqueio temporário do Nominatim.

## Casos de uso prático

### Verificar quantos médicos prioritários foram carregados

```bash
python3 << 'EOF'
from database import SessionLocal
from models.medico import Medico
from sqlalchemy import select

db = SessionLocal()
all_medicos = db.execute(select(Medico)).scalars().all()
priority_a = len([m for m in all_medicos if m.prioridade == "A"])
priority_b = len([m for m in all_medicos if m.prioridade == "B"])

print(f"Prioridade A: {priority_a}")
print(f"Prioridade B: {priority_b}")
db.close()
EOF
```

### Listar apenas médicos prioritários (A) com suas disponibilidades

```bash
python3 << 'EOF'
from database import SessionLocal
from models.medico import Medico
from models.local_atendimento import LocalAtendimento
from models.disponibilidade import Disponibilidade
from sqlalchemy import select

db = SessionLocal()
priority_a_medicos = db.execute(
    select(Medico).where(Medico.prioridade == "A")
).scalars().all()

for m in priority_a_medicos[:5]:  # primeiros 5
    locais = db.execute(
        select(LocalAtendimento).where(LocalAtendimento.medico_id == m.id)
    ).scalars().all()
    
    if locais:
        local = locais[0]
        disps = db.execute(
            select(Disponibilidade).where(Disponibilidade.local_id == local.id)
        ).scalars().all()
        
        print(f"⭐ {m.nome} ({m.crm})")
        print(f"   Local: {local.endereco}")
        print(f"   Horários: {len(disps)} disponibilidades")
        print()

db.close()
EOF
```

## API de geolocalização customizada

Se quiser usar outro geocodificador (Google Maps, OpenStreetMap), altere a função `geocode_address()`:

```python
def geocode_address(endereco: str, bairro: str) -> tuple[float, float] | None:
    # Sua implementação aqui
    pass
```

Nominatim foi escolhido por ser:
- ✅ Gratuito
- ✅ Sem API key
- ✅ OpenStreetMap (aberto)
- ⚠️ Rate limited (1 req/sec)
