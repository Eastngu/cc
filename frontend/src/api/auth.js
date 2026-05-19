import api from './index'

export function login(username, password) {
  return api.post('/auth/login/', { username, password })
}

export function refreshToken(refresh) {
  return api.post('/auth/refresh/', { refresh })
}

export function getMe() {
  return api.get('/auth/me/')
}
