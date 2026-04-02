import React, { useState, useEffect, useCallback } from 'react'
import MedicoList from './components/MedicoList'
import RouteMap from './components/RouteMap'
import RotaResult from './components/RotaResult'
import {
  getMedicos,
  getRota,
  otimizarRota,
  atualizarStatusVisita
} from './api/client'

function getTodayDate() {
  return new Date().toISOString().split('T')[0]
}

export default function App() {
  const [medicos, setMedicos] = useState([])
  const [selecionados, setSelecionados] = useState(new Set())
  const [rotaSelecionada, setRotaSelecionada] = useState(null)
  const [selectedVisitaId, setSelectedVisitaId] = useState(null)
  const [dataVisita, setDataVisita] = useState(getTodayDate())
  const [loading, setLoading] = useState(false)
  const [representanteId, setRepresentanteId] = useState(null)
  const [erro, setErro] = useState(null)
  // Local e horário de início da rota (ponto de partida)
  const [localInicio, setLocalInicio] = useState({
    endereco: '',
    latitude: '',
    longitude: '',
    hora_inicio: '08:00',
    hora_fim: ''
  })

  // Fetch medicos on mount and when date changes
  useEffect(() => {
    async function init() {
      setLoading(true)
      setErro(null)
      try {
        // Filter medicos by selected date (availability on that weekday)
        const res = await getMedicos({ ativo: true, data: dataVisita })
        const lista = res.data?.items || res.data || []
        setMedicos(lista)

        // Extract representante_id from first doctor
        if (lista.length > 0 && lista[0].representante_id) {
          setRepresentanteId(lista[0].representante_id)
        }

        // Clear selections, route and map pins when changing date
        setSelecionados(new Set())
        setRotaSelecionada(null)
        setSelectedVisitaId(null)
      } catch (e) {
        console.error('Erro ao carregar médicos:', e)
        setErro('Erro ao carregar médicos. Verifique se o backend está rodando.')
      } finally {
        setLoading(false)
      }
    }
    init()
  }, [dataVisita])

  function toggleMedico(id) {
    setSelecionados((prev) => {
      const next = new Set(prev)
      if (next.has(id)) {
        next.delete(id)
      } else {
        next.add(id)
      }
      return next
    })
  }

  async function handleOtimizar() {
    if (selecionados.size === 0) {
      alert('Selecione ao menos um médico para otimizar a rota.')
      return
    }
    if (!representanteId) {
      alert('Representante não identificado. Verifique se há médicos cadastrados.')
      return
    }

    setLoading(true)
    setErro(null)
    try {
      const payload = {
        representante_id: representanteId,
        data: dataVisita,
        medico_ids: Array.from(selecionados),
        local_inicio_endereco: localInicio.endereco || null,
        local_inicio_latitude: localInicio.latitude ? parseFloat(localInicio.latitude) : null,
        local_inicio_longitude: localInicio.longitude ? parseFloat(localInicio.longitude) : null,
        hora_inicio_jornada: localInicio.hora_inicio || null,
        hora_fim_jornada: localInicio.hora_fim || null,
      }
      const res = await otimizarRota(payload)
      const rota = res.data
      setRotaSelecionada(rota)
      setSelectedVisitaId(null)
    } catch (e) {
      console.error('Erro ao otimizar rota:', e)
      const msg = e.response?.data?.detail || e.message || 'Erro desconhecido'
      alert(`Erro ao otimizar rota: ${msg}`)
    } finally {
      setLoading(false)
    }
  }

  async function handleStatusUpdate(visitaId, status) {
    if (!rotaSelecionada) return
    setLoading(true)
    try {
      await atualizarStatusVisita(rotaSelecionada.id, visitaId, status)

      if (status === 'cancelada') {
        // Re-optimize with remaining non-canceled doctors
        const visitasRestantes = rotaSelecionada.visitas.filter(
          v => v.id !== visitaId && v.status_visita !== 'cancelada'
        )

        if (visitasRestantes.length === 0) {
          // No visits left — just update status locally
          setRotaSelecionada(prev => ({
            ...prev,
            visitas: prev.visitas.map(v => v.id === visitaId ? { ...v, status_visita: status } : v)
          }))
          return
        }

        const payload = {
          representante_id: rotaSelecionada.representante_id,
          data: rotaSelecionada.data || rotaSelecionada.data_rota,
          medico_ids: visitasRestantes.map(v => v.medico_id),
          local_inicio_endereco: localInicio.endereco || null,
          local_inicio_latitude: localInicio.latitude ? parseFloat(localInicio.latitude) : null,
          local_inicio_longitude: localInicio.longitude ? parseFloat(localInicio.longitude) : null,
          hora_inicio_jornada: localInicio.hora_inicio || null,
          hora_fim_jornada: localInicio.hora_fim || null,
        }
        const res = await otimizarRota(payload)
        setRotaSelecionada(res.data)
        setSelectedVisitaId(null)
      } else {
        // For realizada / nao_encontrado — update locally to preserve lat/lon
        setRotaSelecionada(prev => ({
          ...prev,
          visitas: prev.visitas.map(v =>
            v.id === visitaId ? { ...v, status_visita: status } : v
          )
        }))
      }
    } catch (e) {
      console.error('Erro ao atualizar status:', e)
      alert('Erro ao atualizar status da visita.')
    } finally {
      setLoading(false)
    }
  }

  return (
    <div className="app">
      {loading && (
        <div className="loading-overlay">
          <div className="spinner" />
        </div>
      )}

      <header className="header">
        <h1>Pharma Route — Otimizador</h1>
        <div className="header-controls">
          <div className="control-group">
            <label htmlFor="data-visita">Data da visita:</label>
            <input
              id="data-visita"
              type="date"
              value={dataVisita}
              onChange={(e) => setDataVisita(e.target.value)}
            />
          </div>

          <div className="control-group">
            <label htmlFor="hora-inicio-jornada">Início:</label>
            <input
              id="hora-inicio-jornada"
              type="time"
              value={localInicio.hora_inicio}
              onChange={(e) => setLocalInicio({ ...localInicio, hora_inicio: e.target.value })}
            />
          </div>

          <div className="control-group">
            <label htmlFor="hora-fim-jornada">Fim:</label>
            <input
              id="hora-fim-jornada"
              type="time"
              value={localInicio.hora_fim}
              placeholder="—"
              onChange={(e) => setLocalInicio({ ...localInicio, hora_fim: e.target.value })}
            />
          </div>

          <div className="control-group">
            <label htmlFor="local-inicio-endereco">Local de início:</label>
            <input
              id="local-inicio-endereco"
              type="text"
              placeholder="Endereço (opcional)"
              value={localInicio.endereco}
              onChange={(e) => setLocalInicio({ ...localInicio, endereco: e.target.value })}
            />
          </div>

          <div className="control-group">
            <label htmlFor="local-inicio-latitude">Latitude:</label>
            <input
              id="local-inicio-latitude"
              type="number"
              step="0.0001"
              placeholder="-22.9xxx"
              value={localInicio.latitude}
              onChange={(e) => setLocalInicio({ ...localInicio, latitude: e.target.value })}
            />
          </div>

          <div className="control-group">
            <label htmlFor="local-inicio-longitude">Longitude:</label>
            <input
              id="local-inicio-longitude"
              type="number"
              step="0.0001"
              placeholder="-43.1xxx"
              value={localInicio.longitude}
              onChange={(e) => setLocalInicio({ ...localInicio, longitude: e.target.value })}
            />
          </div>
        </div>
      </header>

      {erro && (
        <div className="erro-banner">
          {erro}
        </div>
      )}

      <div className="content">
        <aside className="panel-left">
          <h2 className="panel-title">Médicos</h2>
          <MedicoList
            medicos={medicos}
            selecionados={selecionados}
            onToggle={toggleMedico}
          />
          <button
            className="btn-primary btn-otimizar"
            onClick={handleOtimizar}
            disabled={loading || selecionados.size === 0}
          >
            {loading ? 'Processando...' : 'Otimizar Rota'}
          </button>
        </aside>

        <main className="map-container">
          <RouteMap medicos={medicos} rota={rotaSelecionada} selectedVisitaId={selectedVisitaId} />
        </main>

        <aside className="panel-right">
          <h2 className="panel-title">Resultado da Rota</h2>
          <RotaResult
            rota={rotaSelecionada}
            onStatusUpdate={handleStatusUpdate}
            selectedVisitaId={selectedVisitaId}
            onSelectVisita={setSelectedVisitaId}
          />
        </aside>
      </div>
    </div>
  )
}
