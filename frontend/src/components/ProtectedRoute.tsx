// ProtectedRoute.tsx - Composant de protection des routes selon les rôles
import React from 'react';
import { Navigate, useLocation } from 'react-router-dom';
import { useAuth } from '../contexts/AuthContext';
import AccessDenied from './AccessDenied';

interface ProtectedRouteProps {
  children: React.ReactNode;
  requiredRole?: string | string[];
  requiredPermission?: string;
  fallbackPath?: string;
}

const ProtectedRoute: React.FC<ProtectedRouteProps> = ({
  children,
  requiredRole,
  requiredPermission,
  fallbackPath = '/login'
}) => {
  const { user, loading, hasRole, hasPermission } = useAuth();
  const location = useLocation();

  // Loading state
  if (loading) {
    return (
      <div className="min-h-screen flex items-center justify-center bg-gray-50">
        <div className="text-center">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-primary-600 mx-auto"></div>
          <p className="mt-4 text-gray-600">Vérification des permissions...</p>
        </div>
      </div>
    );
  }

  // Not authenticated
  if (!user) {
    return <Navigate to={fallbackPath} state={{ from: location }} replace />;
  }

  // Check role permission
  if (requiredRole && !hasRole(requiredRole)) {
    return (
      <AccessDenied 
        userRole={user.role}
        requiredRole={Array.isArray(requiredRole) ? requiredRole.join(', ') : requiredRole}
        returnPath="/dashboard"
      />
    );
  
  }

  // Check specific permission
  if (requiredPermission && !hasPermission(requiredPermission)) {
    return (
      <AccessDenied 
        userRole={user.role}
        requiredRole={`Permission: ${requiredPermission}`}
        returnPath="/dashboard"
      />
    );
  }

  // All checks passed, render children
  return <>{children}</>;
};

export default ProtectedRoute;
