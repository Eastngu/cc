import api from './index'

export function getDashboard() {
  return api.get('/reports/dashboard/')
}

export function getRevenueTrend() {
  return api.get('/reports/revenue-trend/')
}

export function getCustomerAnalysis() {
  return api.get('/reports/customer-analysis/')
}

export function getCostAnalysis() {
  return api.get('/reports/cost-analysis/')
}
