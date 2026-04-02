import React from 'react'

const PRIORIDADE_LABELS = { A: 'Alta', B: 'Média', C: 'Baixa' }

function PrioridadeBadge({ prioridade }) {
  const cls = `badge badge-${prioridade}`
  return <span className={cls}>{prioridade} — {PRIORIDADE_LABELS[prioridade] || prioridade}</span>
}

export default function MedicoList({ medicos, selecionados, onToggle }) {
  const todosIds = medicos.map((m) => m.id)
  const todosSelecionados = todosIds.length > 0 && todosIds.every((id) => selecionados.has(id))

  function selecionarTodos() {
    todosIds.forEach((id) => {
      if (!selecionados.has(id)) onToggle(id)
    })
  }

  function limparTodos() {
    todosIds.forEach((id) => {
      if (selecionados.has(id)) onToggle(id)
    })
  }

  return (
    <div className="medico-list">
      <div className="medico-list-controls">
        <button className="btn-sm" onClick={selecionarTodos} disabled={todosSelecionados}>
          Selecionar todos
        </button>
        <button className="btn-sm" onClick={limparTodos} disabled={selecionados.size === 0}>
          Limpar
        </button>
      </div>
      <p className="medico-count">
        {selecionados.size} médico{selecionados.size !== 1 ? 's' : ''} selecionado{selecionados.size !== 1 ? 's' : ''}
      </p>
      <div className="medico-scroll">
        {medicos.length === 0 && (
          <p className="medico-empty">Nenhum médico encontrado.</p>
        )}
        {medicos.map((medico) => (
          <label key={medico.id} className="medico-item">
            <input
              type="checkbox"
              checked={selecionados.has(medico.id)}
              onChange={() => onToggle(medico.id)}
            />
            <span className="medico-info">
              <span className="medico-nome">{medico.nome}</span>
              <span className="medico-especialidade">{medico.especialidade}</span>
            </span>
            <PrioridadeBadge prioridade={medico.prioridade} />
          </label>
        ))}
      </div>
    </div>
  )
}
