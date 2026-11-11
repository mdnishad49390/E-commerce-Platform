import { Navigate } from 'react-router-dom'
import { getAccessToken, getCurrentRole, getRoleHome, isSuperuser } from '../utils/auth'

export default function ProtectedRoute({ children, requiredRole, requiredRoles }) {
  const role = getCurrentRole()
  const allowedRoles = requiredRoles || (requiredRole ? [requiredRole] : [])

  if (!getAccessToken() || !role) {
    return <Navigate to="/login" replace />
  }

  const superBypass = allowedRoles.includes('admin') && isSuperuser()
  if (allowedRoles.length && !allowedRoles.includes(role) && !superBypass) {
    return <Navigate to={getRoleHome(role)} replace />
  }

  return children
}