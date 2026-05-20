import api from './index'

export function getStatements(params) {
  return api.get('/statements/', { params })
}

export function getStatement(id) {
  return api.get(`/statements/${id}/`)
}

export function generateStatement(data) {
  return api.post('/statements/generate/', data)
}

export function confirmStatement(id) {
  return api.patch(`/statements/${id}/confirm/`)
}

export function updateStatement(id, data) {
  return api.put(`/statements/${id}/`, data)
}
