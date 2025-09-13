// AuthContext.tsx - Contexte d'authentification avec gestion des rôles
import React, { createContext, useContext, useState, useEffect, ReactNode } from 'react';
import { toast } from 'react-hot-toast';

// Types
export interface User {
  id: number;
  username: string;
  email: string;
  first_name: string;
  last_name: string;
  full_name: string;
  role: 'admin' | 'department_head' | 'program_head' | 'teacher' | 'student';
  department?: { id: number; name: string };
  program?: { id: number; name: string };
}

export interface LoginResult {
  success: boolean;
  user?: User;
  error?: string;
}

export interface RegisterForm {
  email: string;
  username: string;
  first_name: string;
  last_name: string;
  role: string;
  phone_number?: string;
  password: string;
  password_confirm: string;
}

export interface AuthContextType {
  user: User | null;
  token: string | null;
  loading: boolean;
  isAuthenticated: boolean;
  login: (email: string, password: string) => Promise<LoginResult>;
  logout: () => void;
  refreshToken: () => Promise<boolean>;
  hasRole: (roles: string | string[]) => boolean;
  hasPermission: (permission: string) => boolean;
  updateUser: (userData: Partial<User>) => void;
  registerUser: (data: RegisterForm) => Promise<void>;
}

// Configuration API
const API_BASE_URL = import.meta.env.VITE_API_URL || 'http://127.0.0.1:8000';
const TOKEN_STORAGE_KEY = 'appget_token';
const REFRESH_TOKEN_STORAGE_KEY = 'appget_refresh_token';
const USER_STORAGE_KEY = 'appget_user';

// Contexte
const AuthContext = createContext<AuthContextType | undefined>(undefined);

// Provider
interface AuthProviderProps {
  children: ReactNode;
}

export const AuthProvider: React.FC<AuthProviderProps> = ({ children }) => {
  const [user, setUser] = useState<User | null>(null);
  const [token, setToken] = useState<string | null>(null);
  const [loading, setLoading] = useState(true);

  // Initialisation au chargement
  useEffect(() => {
    initializeAuth();
  }, []);

  // Auto-refresh du token toutes les 14 minutes
  useEffect(() => {
    if (token) {
      const interval = setInterval(() => {
        refreshTokenSilently();
      }, 14 * 60 * 1000);
      return () => clearInterval(interval);
    }
  }, [token]);

  const initializeAuth = async () => {
    try {
      const storedToken = localStorage.getItem(TOKEN_STORAGE_KEY);
      const storedUser = localStorage.getItem(USER_STORAGE_KEY);

      if (storedToken && storedUser) {
        const userData = JSON.parse(storedUser);
        setToken(storedToken);
        setUser(userData);

        const isValid = await validateToken(storedToken);
        if (!isValid) {
          const refreshed = await refreshToken();
          if (!refreshed) logout();
        }
      }
    } catch (error) {
      console.error('Erreur lors de l\'initialisation de l\'auth:', error);
      logout();
    } finally {
      setLoading(false);
    }
  };

  // Connexion
  const login = async (email: string, password: string): Promise<LoginResult> => {
    try {
      const response = await fetch(`${API_BASE_URL}/api/auth/login/`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ email, password }),
      });

      const data = await response.json();

      if (response.ok) {
        const { token, user: userData } = data;

        localStorage.setItem(TOKEN_STORAGE_KEY, token);
        localStorage.setItem(USER_STORAGE_KEY, JSON.stringify(userData));

        setToken(token);
        setUser(userData);

        toast.success(data.message || 'Connexion réussie');
        return { success: true, user: userData };
      } else {
        const errorMessage = data.detail || data.message || data.error || 'Identifiants incorrects';
        return { success: false, error: errorMessage };
      }
    } catch (error) {
      console.error('Erreur de connexion:', error);
      return { success: false, error: 'Erreur de connexion au serveur' };
    }
  };

  // Déconnexion
  const logout = () => {
    localStorage.removeItem(TOKEN_STORAGE_KEY);
    localStorage.removeItem(REFRESH_TOKEN_STORAGE_KEY);
    localStorage.removeItem(USER_STORAGE_KEY);
    setToken(null);
    setUser(null);
    toast.success('Déconnexion réussie');
  };

  // Refresh token
  const refreshToken = async (): Promise<boolean> => {
    try {
      const currentToken = localStorage.getItem(TOKEN_STORAGE_KEY);
      if (!currentToken) return false;

      const response = await fetch(`${API_BASE_URL}/api/auth/refresh/`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ token: currentToken }),
      });

      if (response.ok) {
        const data = await response.json();
        const { token: newToken, user: userData } = data;
        
        localStorage.setItem(TOKEN_STORAGE_KEY, newToken);
        if (userData) {
          localStorage.setItem(USER_STORAGE_KEY, JSON.stringify(userData));
          setUser(userData);
        }
        setToken(newToken);
        return true;
      } else {
        return false;
      }
    } catch (error) {
      console.error('Erreur lors du refresh du token:', error);
      return false;
    }
  };

  const refreshTokenSilently = async () => {
    const success = await refreshToken();
    if (!success) logout();
  };

  const validateToken = async (tokenToValidate: string): Promise<boolean> => {
    try {
      const response = await fetch(`${API_BASE_URL}/api/auth/verify/`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ token: tokenToValidate }),
      });
      return response.ok;
    } catch {
      return false;
    }
  };

  // Vérification rôle et permissions
  const hasRole = (roles: string | string[]): boolean => {
    if (!user) return false;
    const roleArray = Array.isArray(roles) ? roles : [roles];
    return roleArray.includes(user.role);
  };

  const hasPermission = (permission: string): boolean => {
    if (!user) return false;

    const rolePermissions: Record<string, string[]> = {
      admin: [
        'all', 'read', 'write', 'delete',
        'manage_users', 'manage_departments', 'manage_programs',
        'manage_schedules', 'import_excel', 'generate_timetable',
        'view_statistics', 'export_data'
      ],
      department_head: [
        'read', 'write',
        'manage_teachers', 'manage_subjects', 'manage_rooms',
        'manage_schedules_department', 'view_statistics_department',
        'export_data'
      ],
      program_head: [
        'read', 'write',
        'manage_students', 'manage_schedules_program',
        'view_statistics_program', 'export_data'
      ],
      teacher: [
        'read', 'view_own_schedule', 'update_own_profile',
        'view_own_students', 'export_own_data'
      ],
      student: [
        'read', 'view_own_schedule', 'update_own_profile',
        'export_own_data'
      ]
    };

    const userPermissions = rolePermissions[user.role] || [];
    return userPermissions.includes('all') || userPermissions.includes(permission);
  };

  // Mettre à jour l'utilisateur
  const updateUser = (userData: Partial<User>) => {
    if (user) {
      const updatedUser = { ...user, ...userData };
      setUser(updatedUser);
      localStorage.setItem(USER_STORAGE_KEY, JSON.stringify(updatedUser));
    }
  };

  // Inscription
  const registerUser = async (data: RegisterForm): Promise<void> => {
    try {
      const response = await fetch(`${API_BASE_URL}/api/auth/register/`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(data),
      });

      const resData = await response.json();
      if (!response.ok) throw resData;
    } catch (error: any) {
      throw error;
    }
  };

  const contextValue: AuthContextType = {
    user,
    token,
    loading,
    isAuthenticated: !!token && !!user,
    login,
    logout,
    refreshToken,
    hasRole,
    hasPermission,
    updateUser,
    registerUser
  };

  return <AuthContext.Provider value={contextValue}>{children}</AuthContext.Provider>;
};

// Hook pour utiliser le contexte
export const useAuth = (): AuthContextType => {
  const context = useContext(AuthContext);
  if (!context) throw new Error('useAuth doit être utilisé dans un AuthProvider');
  return context;
};

// Hook pour les requêtes API authentifiées
export const useAuthenticatedFetch = () => {
  const { token, logout } = useAuth();

  return async (url: string, options: RequestInit = {}): Promise<Response> => {
    const headers: Record<string, string> = {
      'Content-Type': 'application/json',
      ...(options.headers as Record<string, string>),
    };

    if (token) headers['Authorization'] = `Bearer ${token}`;

    const response = await fetch(`${API_BASE_URL}${url}`, { ...options, headers });

    if (response.status === 401) {
      logout();
      throw new Error('Session expirée');
    }

    return response;
  };
};

// Utilitaires pour rôles
export const roleDisplayNames: Record<string, string> = {
  admin: 'Administrateur',
  department_head: 'Chef de Département',
  program_head: 'Chef de Filière',
  teacher: 'Enseignant',
  student: 'Étudiant'
};

export const roleColors: Record<string, string> = {
  admin: 'bg-red-100 text-red-800 border-red-200',
  department_head: 'bg-blue-100 text-blue-800 border-blue-200',
  program_head: 'bg-green-100 text-green-800 border-green-200',
  teacher: 'bg-purple-100 text-purple-800 border-purple-200',
  student: 'bg-indigo-100 text-indigo-800 border-indigo-200'
};

export const getDefaultRoute = (role: string): string => {
  const routes: Record<string, string> = {
    admin: '/admin/dashboard',
    department_head: '/admin/dashboard',
    program_head: '/admin/dashboard',
    teacher: '/teacher/dashboard',
    student: '/student/dashboard'
  };
  return routes[role] || '/dashboard';
};

// HOC pour composants protégés
interface WithAuthProps {
  requiredRole?: string | string[];
  requiredPermission?: string;
  fallback?: React.ComponentType;
}

export const withAuth = <P extends object>(
  Component: React.ComponentType<P>,
  options: WithAuthProps = {}
) => {
  return (props: P) => {
    const { user, loading, hasRole, hasPermission } = useAuth();
    const { requiredRole, requiredPermission, fallback: Fallback } = options;

    if (loading) {
      return (
        <div className="min-h-screen flex items-center justify-center">
          <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-primary-600"></div>
        </div>
      );
    }

    if (!user) {
      return (
        <div className="min-h-screen flex items-center justify-center">
          <p className="text-gray-500 text-center">Vous devez être connecté pour accéder à cette page.</p>
        </div>
      );
    }

    if (requiredRole && !hasRole(requiredRole)) {
      if (Fallback) return <Fallback />;
      return (
        <div className="min-h-screen flex items-center justify-center">
          <p className="text-gray-500 text-center">Vous n'avez pas les permissions nécessaires.</p>
        </div>
      );
    }

    if (requiredPermission && !hasPermission(requiredPermission)) {
      if (Fallback) return <Fallback />;
      return (
        <div className="min-h-screen flex items-center justify-center">
          <p className="text-gray-500 text-center">Permission insuffisante.</p>
        </div>
      );
    }

    return <Component {...props} />;
  };
};
