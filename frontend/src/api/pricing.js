import api from './index'

export function getPricingRules(params) {
  return api.get('/pricing-rules/', { params })
}

export function createPricingRule(data) {
  return api.post('/pricing-rules/', data)
}

export function updatePricingRule(id, data) {
  return api.put(`/pricing-rules/${id}/`, data)
}

export function deletePricingRule(id) {
  return api.delete(`/pricing-rules/${id}/`)
}
