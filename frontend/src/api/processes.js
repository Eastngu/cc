import api from './index'

export function getProcesses(params) {
  return api.get('/processes/', { params })
}

export function getProcess(id) {
  return api.get(`/processes/${id}/`)
}

export function createProcess(data) {
  return api.post('/processes/', data)
}

export function updateProcess(id, data) {
  return api.put(`/processes/${id}/`, data)
}

export function deleteProcess(id) {
  return api.delete(`/processes/${id}/`)
}
