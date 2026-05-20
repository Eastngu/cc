import api from './index'

export function getReceivables(params) {
  return api.get('/receivables/', { params })
}

export function createReceivable(data) {
  return api.post('/receivables/', data)
}

export function getPayables(params) {
  return api.get('/payables/', { params })
}

export function createPayable(data) {
  return api.post('/payables/', data)
}

export function getPayments(params) {
  return api.get('/payments/', { params })
}

export function createPayment(data) {
  return api.post('/payments/', data)
}
