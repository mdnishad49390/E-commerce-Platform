import { useEffect, useState } from 'react'
import { API_BASE_URL, getAccessToken } from '../../utils/auth'

export default function AdminUsers() {
  const [users, setUsers] = useState([])
  const [logs, setLogs] = useState([])
  const [search, setSearch] = useState('')
  const [roleFilter, setRoleFilter] = useState('all')
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState('')

  const headers = () => ({
    Authorization: `Bearer ${getAccessToken()}`,
    'Content-Type': 'application/json',
  })

  const loadData = async () => {
    setLoading(true)
    setError('')
    try {
      const params = new URLSearchParams()
      if (search) params.set('search', search)
      if (roleFilter !== 'all') params.set('role', roleFilter)

      const [usersRes, logsRes] = await Promise.all([
        fetch(`${API_BASE_URL}/api/admin/users/?${params}`, { headers: headers() }),
        fetch(`${API_BASE_URL}/api/admin/audit-logs/?limit=50`, { headers: headers() }),
      ])

      const usersData = await usersRes.json()
      const logsData = await logsRes.json()
      if (!usersRes.ok) throw new Error(usersData.error || 'Failed to load users.')

      setUsers(Array.isArray(usersData) ? usersData : [])
      setLogs(Array.isArray(logsData) ? logsData : [])
    } catch (err) {
      setError(err.message)
    } finally {
      setLoading(false)
    }
  }

  useEffect(() => {
    loadData()
  }, [roleFilter])

  const patchUser = async (userId, payload) => {
    const response = await fetch(`${API_BASE_URL}/api/admin/users/${userId}/`, {
      method: 'PATCH',
      headers: headers(),
      body: JSON.stringify(payload),
    })
    const data = await response.json()
    if (!response.ok) throw new Error(data.error || 'Update failed.')
    await loadData()
  }

  const resetPassword = async (userId) => {
    const newPassword = window.prompt('New password (min 8 chars):')
    if (!newPassword) return
    const response = await fetch(`${API_BASE_URL}/api/admin/users/${userId}/reset-password/`, {
      method: 'POST',
      headers: headers(),
      body: JSON.stringify({ new_password: newPassword }),
    })
    const data = await response.json()
    if (!response.ok) throw new Error(data.error || 'Password reset failed.')
    window.alert(data.message || 'Password updated.')
    await loadData()
  }

  return (
    <section className="admin-page">
      <header className="admin-page-header">
        <h1>User Control</h1>
        <p>Manage roles, access, and audit trail.</p>
      </header>

      <div className="admin-toolbar">
        <input
          type="search"
          placeholder="Search users..."
          value={search}
          onChange={(event) => setSearch(event.target.value)}
          onKeyDown={(event) => event.key === 'Enter' && loadData()}
        />
        <select value={roleFilter} onChange={(event) => setRoleFilter(event.target.value)}>
          <option value="all">All roles</option>
          <option value="admin">Admin</option>
          <option value="employee">Employee</option>
          <option value="customer">Customer</option>
        </select>
        <button type="button" onClick={loadData}>Refresh</button>
      </div>

      {error ? <p className="admin-error">{error}</p> : null}
      {loading ? <p>Loading...</p> : null}

      <div className="admin-table-wrap">
        <table className="admin-table">
          <thead>
            <tr>
              <th>User</th>
              <th>Role</th>
              <th>Status</th>
              <th>Superuser</th>
              <th>Actions</th>
            </tr>
          </thead>
          <tbody>
            {users.map((user) => (
              <tr key={user.id}>
                <td>
                  <strong>{user.username}</strong>
                  <div>{user.email}</div>
                  {user.is_primary_super_admin ? <small>Primary super admin</small> : null}
                </td>
                <td>
                  <select
                    value={user.role}
                    disabled={user.is_primary_super_admin}
                    onChange={(event) => patchUser(user.id, { role: event.target.value })}
                  >
                    <option value="customer">customer</option>
                    <option value="employee">employee</option>
                    <option value="admin">admin</option>
                  </select>
                </td>
                <td>
                  <button
                    type="button"
                    disabled={user.is_primary_super_admin}
                    onClick={() => patchUser(user.id, { is_active: !user.is_active })}
                  >
                    {user.is_active ? 'Active' : 'Inactive'}
                  </button>
                </td>
                <td>{user.is_superuser ? 'Yes' : 'No'}</td>
                <td>
                  <button type="button" onClick={() => resetPassword(user.id)}>Reset password</button>
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>

      <section className="admin-audit-panel">
        <h2>Recent audit trail</h2>
        <ul className="admin-audit-list">
          {logs.map((entry) => (
            <li key={entry.id}>
              <strong>{entry.created_at}</strong> — {entry.actor}: {entry.action} ({entry.target_type} #{entry.target_id}) {entry.detail}
            </li>
          ))}
        </ul>
      </section>
    </section>
  )
}
