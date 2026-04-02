import axios from 'axios'

// Em produção (Vercel), VITE_API_URL aponta para o backend no Render.
// Em dev local, usa o proxy do Vite (/api → http://localhost:8000).
const api = axios.create({
  baseURL: import.meta.env.VITE_API_URL || '/api',
  headers: {
    'Content-Type': 'application/json'
  }
})

export function getMedicos(params) {
  return api.get('/medicos', { params })
}

export function getMedico(id) {
  return api.get(`/medicos/${id}`)
}

export function criarMedico(data) {
  return api.post('/medicos', data)
}

export function otimizarRota(data) {
  // data: { representante_id, data, medico_ids }
  return api.post('/rotas/otimizar', data)
}

export function getRota(id) {
  return api.get(`/rotas/${id}`)
}

export function listarRotas(params) {
  return api.get('/rotas', { params })
}

export function atualizarStatusVisita(rotaId, visitaId, status) {
  return api.put(`/rotas/${rotaId}/visitas/${visitaId}/status`, { status_visita: status })
}

export default api
