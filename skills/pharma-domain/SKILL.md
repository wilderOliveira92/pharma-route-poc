# Skill: pharma-domain

## Modelo recomendado
**Haiku** para geração de boilerplate, seeds, e estruturas repetitivas com este contexto.
**Sonnet** quando a tarefa envolver lógica de negócio, validações de regra ou integração entre módulos.

---

## Quando usar esta skill
Leia este arquivo SEMPRE que for executar qualquer uma das tarefas abaixo:
- Criar ou modificar modelos de dados (ORM, schemas Pydantic)
- Gerar dados de seed ou fixtures para testes
- Escrever endpoints relacionados a médicos, visitas ou rotas
- Criar documentação ou comentários de código do domínio
- Nomear variáveis, tabelas, funções ou rotas da API

---

## Contexto do domínio farmacêutico

### Atores principais
| Ator | Descrição |
|------|-----------|
| `Representante` | Vendedor farmacêutico. Possui uma região de atuação e uma carteira de médicos sob sua responsabilidade. |
| `Médico` | Profissional que o representante visita. Pode atender em múltiplos locais (consultório, hospital, clínica). |
| `Local de atendimento` | Endereço físico onde o médico atende. Um médico pode ter 1–N locais. |
| `Disponibilidade` | Janela de tempo em que o médico atende num local específico (dia da semana + hora início + hora fim). |
| `Visita` | Evento agendado ou realizado: representante encontra médico num local e horário específicos. |
| `Rota` | Sequência ordenada de visitas para um representante em um dia, otimizada por distância e janelas de tempo. |

### Regras de negócio críticas
1. **Um médico pode atender em locais diferentes em dias diferentes.** Nunca assuma endereço fixo.
2. **Disponibilidade é por local**, não por médico globalmente. O médico Dr. Silva pode estar no Hospital A às segundas e na Clínica B às quartas.
3. **Visitas têm duração estimada padrão de 20 minutos.** Este valor pode ser sobrescrito por especialidade.
4. **Representante não pode visitar o mesmo médico mais de uma vez por dia** no mesmo local.
5. **Janela de tempo do médico é rígida**: uma visita só pode ser agendada se `hora_chegada + 20min <= hora_fim_atendimento`.
6. **Prioridade de visita**: cada médico tem um nível (A, B, C) que indica frequência mínima de visitas por mês (A=4x, B=2x, C=1x).

### Especialidades médicas relevantes para seed
```
Cardiologia, Clínica Geral, Dermatologia, Endocrinologia,
Gastroenterologia, Ginecologia, Neurologia, Oncologia,
Ortopedia, Pediatria, Psiquiatria, Reumatologia, Urologia
```

### Nomenclatura obrigatória
Use sempre estes nomes em código (português, snake_case):

```python
# Modelos
Representante, Medico, LocalAtendimento, Disponibilidade, Visita, Rota

# Campos
rep_id, medico_id, local_id, visita_id, rota_id
dia_semana          # int 0=segunda ... 6=domingo
hora_inicio         # time (HH:MM)
hora_fim            # time (HH:MM)
duracao_minutos     # int, default=20
prioridade          # str enum: 'A' | 'B' | 'C'
status_visita       # str enum: 'agendada' | 'realizada' | 'cancelada' | 'nao_encontrado'
distancia_km        # float
tempo_deslocamento  # int (minutos)
sequencia           # int (posição na rota: 1, 2, 3...)
```

---

## Modelo de dados canônico

```python
# Hierarquia: Representante → (muitos) Médicos
#             Médico → (muitos) LocaisAtendimento
#             LocalAtendimento → (muitas) Disponibilidades
#             Representante + Data → Rota → (muitas) Visitas ordenadas

class Medico(Base):
    __tablename__ = "medicos"
    id: UUID (PK)
    nome: str
    crm: str (unique)
    especialidade: str
    prioridade: str  # 'A' | 'B' | 'C'
    representante_id: UUID (FK → representantes.id)
    ativo: bool = True
    criado_em: datetime

class LocalAtendimento(Base):
    __tablename__ = "locais_atendimento"
    id: UUID (PK)
    medico_id: UUID (FK → medicos.id)
    nome: str          # ex: "Hospital Albert Einstein"
    endereco: str
    latitude: float
    longitude: float   # OBRIGATÓRIO — usado pelo otimizador
    tipo: str          # 'consultorio' | 'hospital' | 'clinica' | 'ubs'

class Disponibilidade(Base):
    __tablename__ = "disponibilidades"
    id: UUID (PK)
    local_id: UUID (FK → locais_atendimento.id)
    dia_semana: int    # 0=segunda, 6=domingo
    hora_inicio: time
    hora_fim: time
    # Constraint: hora_fim - hora_inicio >= 20min
```

---

## Dados de seed realistas (padrão para uso em testes)

Ao gerar seeds, use SEMPRE esta distribuição para simular realidade:
- **40% médicos prioridade A** (cardiologistas, oncologistas, endocrinologistas)
- **40% médicos prioridade B** (clínicos gerais, neurologistas, gastro)
- **20% médicos prioridade C** (especialidades menos frequentadas)

Cada médico deve ter **1–3 locais de atendimento** e **2–4 disponibilidades por semana**.

Exemplo de disponibilidade realista:
```python
# Dr. Carlos Mendes — Cardiologista — Prioridade A
# Local 1: Hospital Sírio-Libanês, SP
#   Segunda: 08:00–12:00
#   Quarta:  14:00–18:00
# Local 2: Consultório próprio, SP
#   Terça:   09:00–13:00
#   Quinta:  09:00–13:00
```

---

## O que NUNCA fazer

- ❌ Nunca usar `address` ou `location` — use `endereco` e `local_atendimento`
- ❌ Nunca criar disponibilidade sem `latitude` e `longitude` no local (o otimizador precisa)
- ❌ Nunca modelar "horário do médico" sem vincular ao local específico
- ❌ Nunca usar `doctor`, `rep`, `visit` em inglês — o domínio é em português
- ❌ Nunca assumir que um médico tem apenas um endereço
- ❌ Nunca criar visita sem verificar se existe disponibilidade no dia/local

---

## Checklist antes de entregar qualquer artefato deste domínio

- [ ] Todos os campos usam a nomenclatura canônica definida acima?
- [ ] LocalAtendimento tem `latitude` e `longitude`?
- [ ] Disponibilidade está vinculada ao local (não ao médico diretamente)?
- [ ] Seed inclui a distribuição A/B/C correta?
- [ ] Nenhuma regra de negócio crítica foi violada?
- [ ] Enums de `status_visita` e `prioridade` estão corretos?