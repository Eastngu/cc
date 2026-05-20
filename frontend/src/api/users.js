import api from './index'

export function getUsers(params) {
  return api.get('/auth/users/', { params })
}

export function createUser(data) {
  return api.post('/auth/users/', data)
}

export function updateUser(id, data) {
  return api.put(`/auth/users/${id}/`, data)
}

export function deleteUser(id) {
  return api.delete(`/auth/users/${id}/`)
}

export function resetPassword(id, password) {
  return api.post(`/auth/users/${id}/reset-password/`, { password })
}

export function changePassword(oldPassword, newPassword) {
  return api.post('/auth/change-password/', {
    old_password: oldPassword,
    new_password: newPassword,
  })
}
