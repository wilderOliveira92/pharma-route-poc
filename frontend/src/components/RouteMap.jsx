import React, { useMemo, useEffect, useRef } from 'react'
import {
  MapContainer,
  TileLayer,
  CircleMarker,
  Marker,
  Polyline,
  Popup,
  useMap
} from 'react-leaflet'
import L from 'leaflet'

// Fix Leaflet default icon paths broken by bundlers
delete L.Icon.Default.prototype._getIconUrl
L.Icon.Default.mergeOptions({
  iconRetinaUrl: new URL('leaflet/dist/images/marker-icon-2x.png', import.meta.url).href,
  iconUrl: new URL('leaflet/dist/images/marker-icon.png', import.meta.url).href,
  shadowUrl: new URL('leaflet/dist/images/marker-shadow.png', import.meta.url).href
})

const RIO_CENTER = [-22.9068, -43.1729]
const DEFAULT_ZOOM = 12

/**
 * Cluster pin: one map marker for N visits at the same coordinates.
 * Each sequence number is its own badge inside a shared pill body.
 * When a specific seq is selected it gets an inverted (white bg) badge.
 */
function makeClusterIcon(seqs, selectedSeq) {
  const badgesHtml = seqs
    .map((seq) => {
      const sel = seq === selectedSeq
      return `<span class="cpin-seq${sel ? ' cpin-seq--sel' : ''}">${seq}</span>`
    })
    .join('')

  const bodyClass = selectedSeq != null ? 'cpin-body cpin-body--sel' : 'cpin-body'
  const w = Math.max(36, seqs.length * 30 + 8)

  return L.divIcon({
    className: '',
    html: `<div class="cpin">
      <div class="${bodyClass}" style="min-width:${w}px">${badgesHtml}</div>
      <div class="cpin-ptr${selectedSeq != null ? ' cpin-ptr--sel' : ''}"></div>
    </div>`,
    iconSize: [w, 46],
    iconAnchor: [w / 2, 46],
    popupAnchor: [0, -46]
  })
}

function formatTime(isoString) {
  if (!isoString) return '—'
  if (/^\d{2}:\d{2}$/.test(isoString)) return isoString
  try {
    return new Date(isoString).toLocaleTimeString('pt-BR', { hour: '2-digit', minute: '2-digit' })
  } catch {
    return isoString
  }
}

function formatDistance(km) {
  if (km == null) return '—'
  if (km >= 1) return `${Number(km).toFixed(1)} km`
  return `${Math.round(km * 1000)} m`
}

function buildMedicoMap(medicos) {
  const map = {}
  medicos.forEach((m) => { map[m.id] = m })
  return map
}

// Auto-fit bounds on first render of a route
function FitBounds({ positions }) {
  const map = useMap()
  useEffect(() => {
    if (positions && positions.length > 0) {
      map.fitBounds(L.latLngBounds(positions), { padding: [50, 50], maxZoom: 15 })
    }
  }, [positions, map])
  return null
}

// Smoothly pan to a position when it changes (used for sidebar selection)
function PanToMarker({ position }) {
  const map = useMap()
  const prev = useRef(null)
  useEffect(() => {
    if (!position) return
    const key = position.join(',')
    if (key !== prev.current) {
      map.panTo(position)
      prev.current = key
    }
  }, [position, map])
  return null
}

export default function RouteMap({ medicos, rota, selectedVisitaId }) {
  const medicoMap = useMemo(() => buildMedicoMap(medicos), [medicos])

  // Medico ids that appear in the route (to grey-out the rest)
  const visitaIds = useMemo(() => {
    if (!rota?.visitas) return new Set()
    return new Set(rota.visitas.map((v) => v.medico_id))
  }, [rota])

  // Polyline: original coords in visit order
  const polylinePositions = useMemo(() => {
    if (!rota?.visitas) return []
    return rota.visitas
      .filter((v) => v.latitude != null && v.longitude != null)
      .map((v) => [v.latitude, v.longitude])
  }, [rota])

  // Group visitas by exact coordinate — produces one pin per unique location
  const grupos = useMemo(() => {
    if (!rota?.visitas) return []
    const byCoord = {}
    rota.visitas.forEach((v) => {
      if (v.latitude == null || v.longitude == null) return
      const key = `${v.latitude},${v.longitude}`
      if (!byCoord[key]) byCoord[key] = { lat: v.latitude, lon: v.longitude, visitas: [] }
      byCoord[key].visitas.push(v)
    })
    return Object.values(byCoord)
  }, [rota])

  // Position of selected visita → used by PanToMarker
  const selectedPosition = useMemo(() => {
    if (!selectedVisitaId || !rota?.visitas) return null
    const v = rota.visitas.find((v) => v.id === selectedVisitaId)
    if (!v || v.latitude == null) return null
    return [v.latitude, v.longitude]
  }, [selectedVisitaId, rota])

  return (
    <>
      <style>{`
        /* ── Cluster pin ─────────────────────────────────────── */
        .cpin {
          display: flex;
          flex-direction: column;
          align-items: center;
          filter: drop-shadow(0 2px 5px rgba(0,0,0,0.45));
        }
        .cpin-body {
          display: flex;
          gap: 5px;
          padding: 0 6px;
          height: 32px;
          align-items: center;
          background: linear-gradient(135deg, #dc2626, #b91c1c);
          border-radius: 16px;
          border: 3px solid #fff;
          box-sizing: border-box;
        }
        .cpin-body--sel {
          background: linear-gradient(135deg, #d97706, #b45309);
        }
        .cpin-seq {
          min-width: 22px;
          height: 22px;
          display: flex;
          align-items: center;
          justify-content: center;
          font-weight: 800;
          font-size: 13px;
          color: #fff;
          border-radius: 50%;
          padding: 0 2px;
        }
        .cpin-seq--sel {
          background: #fff;
          color: #b91c1c;
        }
        .cpin-body--sel .cpin-seq--sel {
          color: #b45309;
        }
        .cpin-ptr {
          width: 0;
          height: 0;
          border-left: 8px solid transparent;
          border-right: 8px solid transparent;
          border-top: 14px solid #fff;
          margin-top: -3px;
        }
        .cpin-ptr--sel {
          border-top-color: #fff;
        }

        /* ── Popup for clusters ──────────────────────────────── */
        .cluster-popup-item {
          padding: 4px 0;
          border-bottom: 1px solid #e5e7eb;
        }
        .cluster-popup-item:last-child { border-bottom: none; }
      `}</style>

      <MapContainer
        center={RIO_CENTER}
        zoom={DEFAULT_ZOOM}
        style={{ width: '100%', height: '100%' }}
      >
        <TileLayer
          attribution='&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors'
          url="https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png"
        />

        {rota && polylinePositions.length > 0 && (
          <FitBounds positions={polylinePositions} />
        )}

        {selectedPosition && (
          <PanToMarker position={selectedPosition} />
        )}

        {/* No route: all medicos as blue dots */}
        {!rota && medicos.map((medico) => {
          if (medico.latitude == null || medico.longitude == null) return null
          return (
            <CircleMarker
              key={medico.id}
              center={[medico.latitude, medico.longitude]}
              radius={10}
              pathOptions={{ color: '#1d4ed8', fillColor: '#3b82f6', fillOpacity: 0.8 }}
            >
              <Popup>
                <strong>{medico.nome}</strong><br />
                {medico.especialidade}<br />
                Prioridade: <strong>{medico.prioridade}</strong>
              </Popup>
            </CircleMarker>
          )
        })}

        {/* Route: one cluster pin per unique coordinate */}
        {rota && grupos.map((grupo) => {
          const seqs = grupo.visitas.map((v) => v.sequencia)
          const selVisita = grupo.visitas.find((v) => v.id === selectedVisitaId)
          const selectedSeq = selVisita?.sequencia ?? null
          const icon = makeClusterIcon(seqs, selectedSeq)

          return (
            <Marker
              key={`${grupo.lat},${grupo.lon}`}
              position={[grupo.lat, grupo.lon]}
              icon={icon}
            >
              <Popup minWidth={200}>
                {grupo.visitas.map((visita) => {
                  const medico = medicoMap[visita.medico_id]
                  const nome = medico?.nome || visita.medico_nome || 'Médico'
                  const esp = medico?.especialidade || ''
                  return (
                    <div key={visita.id} className="cluster-popup-item">
                      <strong>#{visita.sequencia} — {nome}</strong><br />
                      {esp && <span style={{ color: '#6b7280', fontSize: '0.85em' }}>{esp}<br /></span>}
                      <span style={{ fontSize: '0.85em' }}>
                        {visita.local_nome && <><strong>{visita.local_nome}</strong><br /></>}
                        Chegada: <strong>{formatTime(visita.hora_chegada)}</strong>
                        {visita.distancia_km != null && (
                          <> · {formatDistance(visita.distancia_km)}</>
                        )}
                      </span>
                    </div>
                  )
                })}
              </Popup>
            </Marker>
          )
        })}

        {/* Grey dots for medicos NOT in the current route */}
        {rota && medicos
          .filter((m) => !visitaIds.has(m.id))
          .map((medico) => {
            if (medico.latitude == null || medico.longitude == null) return null
            return (
              <CircleMarker
                key={medico.id}
                center={[medico.latitude, medico.longitude]}
                radius={7}
                pathOptions={{ color: '#9ca3af', fillColor: '#d1d5db', fillOpacity: 0.7 }}
              >
                <Popup>
                  <strong>{medico.nome}</strong><br />
                  {medico.especialidade}<br />
                  <em>Não incluído na rota</em>
                </Popup>
              </CircleMarker>
            )
          })}

        {polylinePositions.length > 1 && (
          <Polyline
            positions={polylinePositions}
            pathOptions={{ color: '#dc2626', weight: 3, dashArray: '6 4' }}
          />
        )}
      </MapContainer>
    </>
  )
}
