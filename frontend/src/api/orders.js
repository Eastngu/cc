import api from './index'

export function getOrders(params) {
  return api.get('/orders/', { params })
}

export function getOrder(id) {
  return api.get(`/orders/${id}/`)
}

export function createOrder(data) {
  return api.post('/orders/', data)
}

export function updateOrder(id, data) {
  return api.put(`/orders/${id}/`, data)
}

export function changeOrderStatus(id, status) {
  return api.patch(`/orders/${id}/status/`, { status })
}
