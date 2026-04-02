import React from 'react'

const STATUS_OPTIONS = [
  { value: 'agendada', label: 'Agendada' },
  { value: 'realizada', label: 'Realizada' },
  { value: 'cancelada', label: 'Cancelada' },
  { value: 'nao_encontrado', label: 'Não encontrado' }
]

function formatDate(isoDate) {
  if (!isoDate) return '—'
  try {
    const [y, m, d] = isoDate.split('-')
    return `${d}/${m}/${y}`
  } catch {
    return isoDate
  }
}

function formatTime(isoString) {
  if (!isoString) return '—'
  try {
    const d = new Date(isoString)
    return d.toLocaleTimeString('pt-BR', { hour: '2-digit', minute: '2-digit' })
  } catch {
    return isoString
  }
}

function formatDistance(metros) {
  if (metros == null) return '—'
  if (metros >= 1000) return `${(metros / 1000).toFixed(1)} km`
  return `${Math.round(metros)} m`
}

export default function RotaResult({ rota, onStatusUpdate, selectedVisitaId, onSelectVisita }) {
  if (!rota) {
    return (
      <div className="rota-placeholder">
        <p>Nenhuma rota otimizada ainda.</p>
        <p className="rota-placeholder-hint">
          Selecione os médicos e clique em "Otimizar Rota".
        </p>
      </div>
    )
  }

  const visitas = rota.visitas || []
  const totalKm = rota.distancia_total_km != null
    ? `${Number(rota.distancia_total_km).toFixed(1)} km`
    : (rota.distancia_total_metros != null
        ? `${(rota.distancia_total_metros / 1000).toFixed(1)} km`
        : '—')
  const totalMin = rota.tempo_total_minutos != null ? `${Math.round(rota.tempo_total_minutos)} min` : '—'

  return (
    <div className="rota-result">
      <div className="rota-header">
        <h3>Rota — {formatDate(rota.data)}</h3>
        <div className="rota-stats">
          <span>{visitas.length} visita{visitas.length !== 1 ? 's' : ''}</span>
          <span>{totalKm}</span>
          <span>{totalMin}</span>
        </div>
      </div>

      <div className="visitas-list">
        {visitas.map((visita) => (
          <div
            key={visita.id || visita.medico_id}
            className={`visita-item${visita.id === selectedVisitaId ? ' visita-item--selected' : ''}`}
            onClick={() => onSelectVisita?.(visita.id === selectedVisitaId ? null : visita.id)}
            style={{ cursor: 'pointer' }}
          >
            <span className="visita-seq">{visita.sequencia}</span>
            <div className="visita-info">
              <span className="visita-nome">{visita.medico_nome || visita.medico_id}</span>
              {visita.local_nome && (
                <span className="visita-local">{visita.local_nome}</span>
              )}
              <span className="visita-horario">
                Chegada: {formatTime(visita.horario_estimado)}
              </span>
              {visita.distancia_anterior_metros != null && (
                <span className="visita-distancia">
                  Anterior: {formatDistance(visita.distancia_anterior_metros)}
                </span>
              )}
            </div>
            <select
              className="visita-status"
              value={visita.status_visita || 'agendada'}
              onChange={(e) => onStatusUpdate(visita.id, e.target.value)}
            >
              {STATUS_OPTIONS.map((opt) => (
                <option key={opt.value} value={opt.value}>{opt.label}</option>
              ))}
            </select>
          </div>
        ))}
      </div>

      <div className="rota-totais">
        <strong>Total:</strong> {visitas.length} visitas &bull; {totalKm} &bull; {totalMin}
      </div>
    </div>
  )
}
