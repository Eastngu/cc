import api from './index'

export function getCosts(params) {
  return api.get('/costing/', { params })
}

export function createCost(data) {
  return api.post('/costing/', data)
}

export function updateCost(id, data) {
  return api.put(`/costing/${id}/`, data)
}

export function getCostSummary(params) {
  return api.get('/costing/summary/', { params })
}
