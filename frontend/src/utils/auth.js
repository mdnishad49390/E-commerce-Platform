export const API_BASE_URL = (import.meta.env.VITE_API_URL || 'http://127.0.0.1:8000').replace(/\/$/, '')

const ACCESS_STORAGE_KEY = 'access_token'
let accessTokenMemory = null

export function getAccessToken() {
  if (accessTokenMemory) return accessTokenMemory
  const sessionToken = sessionStorage.getItem(ACCESS_STORAGE_KEY)
  if (sessionToken) {
    accessTokenMemory = sessionToken
    return sessionToken
  }
  const legacy = localStorage.getItem(ACCESS_STORAGE_KEY)
  if (legacy) {
    setAccessToken(legacy)
    localStorage.removeItem(ACCESS_STORAGE_KEY)
    localStorage.removeItem('refresh_token')
    return legacy
  }
  return null
}

export function setAccessToken(token) {
  accessTokenMemory = token || null
  if (token) {
    sessionStorage.setItem(ACCESS_STORAGE_KEY, token)
  } else {
    sessionStorage.removeItem(ACCESS_STORAGE_KEY)
  }
}

export function getRoleFromToken(token = getAccessToken()) {
  if (!token) return null

  try {
    const payload = token.split('.')[1]
    const claims = JSON.parse(atob(payload.replace(/-/g, '+').replace(/_/g, '/')))
    if (claims.role) return claims.role
    if (claims.is_superuser || claims.is_staff) return 'admin'
    return 'customer'
  } catch {
    return null
  }
}

export function isSuperuser() {
  const stored = localStorage.getItem('is_superuser')
  if (stored === 'true') return true
  if (stored === 'false') return false
  const token = getAccessToken()
  if (!token) return false
  try {
    const payload = token.split('.')[1]
    const claims = JSON.parse(atob(payload.replace(/-/g, '+').replace(/_/g, '/')))
    return Boolean(claims.is_superuser)
  } catch {
    return false
  }
}

export function getCurrentRole() {
  const role = localStorage.getItem('user_role') || getRoleFromToken()
  if (isSuperuser()) return 'admin'
  return role
}

function getUserIdFromToken(token) {
  if (!token) return null

  try {
    const payload = token.split('.')[1]
    const claims = JSON.parse(atob(payload.replace(/-/g, '+').replace(/_/g, '/')))
    const userId = claims.user_id ?? claims.sub
    return userId === undefined || userId === null ? null : String(userId)
  } catch {
    return null
  }
}

export function getCurrentUserId() {
  const storedUserId = localStorage.getItem('user_id')
  if (storedUserId) return storedUserId

  const userId = getUserIdFromToken(getAccessToken())
  if (userId) localStorage.setItem('user_id', userId)
  return userId
}

export function getRoleHome(role) {
  if (role === 'admin') return '/admin'
  if (role === 'employee') return '/employee'
  return '/'
}

export function saveAuthData(payload, usernameFallback = '') {
  const user = payload.user || payload
  const role = user.role || payload.role || getRoleFromToken(payload.access) || 'customer'
  const username = user.username || payload.username || usernameFallback || 'user'
  const userId = user.id ?? payload.id ?? getUserIdFromToken(payload.access)

  setAccessToken(payload.access)
  localStorage.removeItem('refresh_token')

  const superFlag = Boolean(user.is_superuser ?? payload.is_superuser)
  const effectiveRole = superFlag ? 'admin' : role

  localStorage.setItem('username', username)
  localStorage.setItem('user_role', effectiveRole)
  localStorage.setItem('is_superuser', String(superFlag))
  if (userId !== undefined && userId !== null) {
    localStorage.setItem('user_id', String(userId))
  } else {
    localStorage.removeItem('user_id')
  }
  window.dispatchEvent(new Event('auth-change'))
  return { ...user, role, username }
}

export async function logout() {
  try {
    await fetch(`${API_BASE_URL}/api/accounts/logout/`, {
      method: 'POST',
      credentials: 'include',
    })
  } catch {
    // best effort
  }
  clearAuthData()
}

export function clearAuthData() {
  setAccessToken(null)
  for (const key of ['refresh_token', 'username', 'user_role', 'user_id', 'is_staff', 'is_superuser']) {
    localStorage.removeItem(key)
  }
  window.dispatchEvent(new Event('auth-change'))
}

export function updateStoredUsername(username) {
  localStorage.setItem('username', username)
  window.dispatchEvent(new Event('auth-change'))
}

export async function bootstrapAuth() {
  if (getAccessToken()) return Boolean(getAccessToken())
  try {
    const refreshResponse = await fetch(`${API_BASE_URL}/api/accounts/token/refresh/`, {
      method: 'POST',
      credentials: 'include',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({}),
    })
    const refreshData = await refreshResponse.json().catch(() => ({}))
    if (refreshResponse.ok && refreshData.access) {
      setAccessToken(refreshData.access)
      if (!localStorage.getItem('user_role')) {
        localStorage.setItem('user_role', getRoleFromToken(refreshData.access) || 'customer')
      }
      return true
    }
  } catch {
    return false
  }
  return false
}

export async function fetchWithTokenRefresh(url, options = {}) {
  const sendRequest = (accessToken) => fetch(url, {
    ...options,
    credentials: 'include',
    headers: {
      ...options.headers,
      Authorization: `Bearer ${accessToken}`,
    },
  })

  const accessToken = getAccessToken()
  if (!accessToken) {
    const bootstrapped = await bootstrapAuth()
    if (!bootstrapped) {
      clearAuthData()
      const error = new Error('Session expired. Please login again.')
      error.status = 401
      throw error
    }
  }

  let token = getAccessToken()
  let response = await sendRequest(token)
  if (response.status !== 401) return response

  try {
    const refreshResponse = await fetch(`${API_BASE_URL}/api/accounts/token/refresh/`, {
      method: 'POST',
      credentials: 'include',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({}),
    })
    const refreshData = await refreshResponse.json().catch(() => ({}))
    if (!refreshResponse.ok || !refreshData.access) {
      clearAuthData()
      return response
    }
    setAccessToken(refreshData.access)
  } catch {
    clearAuthData()
    return response
  }

  response = await sendRequest(getAccessToken())
  if (response.status === 401) clearAuthData()
  return response
}

export function authHeaders(extra = {}) {
  const token = getAccessToken()
  return {
    ...extra,
    ...(token ? { Authorization: `Bearer ${token}` } : {}),
  }
}
