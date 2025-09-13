// Login.tsx - Composant de connexion DESKTOP optimisé
import React, { useState, useEffect } from 'react';
import { useNavigate, useLocation } from 'react-router-dom';
import { useAuth } from '../contexts/AuthContext';
import { User, Lock, Eye, EyeOff, AlertCircle, LogIn, Calendar, Shield, GraduationCap } from 'lucide-react';
import { toast } from 'react-hot-toast';

interface LoginForm {
  email: string;
  password: string;
  rememberMe: boolean;
}

const Login: React.FC = () => {
  const navigate = useNavigate();
  const location = useLocation();
  const { login, user, loading } = useAuth();

  const [formData, setFormData] = useState<LoginForm>({
    email: '',
    password: '',
    rememberMe: false
  });

  const [showPassword, setShowPassword] = useState(false);
  const [isLoading, setIsLoading] = useState(false);
  const [errors, setErrors] = useState<Partial<LoginForm>>({});

  // Redirection si déjà connecté
  useEffect(() => {
    if (user && !loading) {
      const redirectTo = (location.state as any)?.from || getDashboardRoute(user.role);
      navigate(redirectTo, { replace: true });
    }
  }, [user, loading, navigate, location]);

  const getDashboardRoute = (role: string): string => {
    const roleRoutes: Record<string, string> = {
      'admin': '/admin/dashboard',
      'department_head': '/admin/dashboard',
      'program_head': '/admin/dashboard', 
      'teacher': '/teacher/dashboard',
      'student': '/student/dashboard'
    };
    return roleRoutes[role] || '/dashboard';
  };

  const validateForm = (): boolean => {
    const newErrors: Partial<LoginForm> = {};
    
    if (!formData.email.trim()) {
      newErrors.email = 'L\'email est requis';
    } else if (!/\S+@\S+\.\S+/.test(formData.email)) {
      newErrors.email = 'Format d\'email invalide';
    }
    
    if (!formData.password.trim()) {
      newErrors.password = 'Le mot de passe est requis';
    } else if (formData.password.length < 6) {
      newErrors.password = 'Le mot de passe doit contenir au moins 6 caractères';
    }
    
    setErrors(newErrors);
    return Object.keys(newErrors).length === 0;
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    
    if (!validateForm()) {
      toast.error('Veuillez corriger les erreurs dans le formulaire');
      return;
    }

    setIsLoading(true);
    setErrors({});

    try {
      await login(formData.email, formData.password, formData.rememberMe);
      
      const redirectTo = (location.state as any)?.from || getDashboardRoute(user?.role || 'student');
      navigate(redirectTo, { replace: true });
      
      toast.success('Connexion réussie !');
    } catch (error: any) {
      console.error('Erreur de connexion:', error);
      
      let errorMessage = 'Une erreur est survenue lors de la connexion';
      
      if (error.response?.status === 401) {
        errorMessage = 'Email ou mot de passe incorrect';
      } else if (error.response?.status === 403) {
        errorMessage = 'Accès refusé. Contactez l\'administrateur.';
      } else if (error.response?.status === 429) {
        errorMessage = 'Trop de tentatives. Veuillez réessayer plus tard.';
      } else if (error.response?.data?.message) {
        errorMessage = error.response.data.message;
      } else if (!error.response) {
        errorMessage = 'Impossible de se connecter au serveur. Vérifiez votre connexion internet.';
      }
      
      toast.error(errorMessage);
      setErrors({ password: 'Vérifiez vos identifiants' });
    } finally {
      setIsLoading(false);
    }
  };

  const handleInputChange = (field: keyof LoginForm, value: string | boolean) => {
    setFormData(prev => ({ ...prev, [field]: value }));
    
    // Effacer l'erreur du champ modifié
    if (errors[field]) {
      setErrors(prev => ({ ...prev, [field]: undefined }));
    }
  };

  // Comptes de démonstration
  const demoAccounts = [
    {
      role: 'Administrateur',
      email: 'admin@appget.local',
      password: 'admin123',
      icon: <Shield className="h-5 w-5" />,
      color: 'from-red-500 to-red-600'
    },
    {
      role: 'Enseignant',
      email: 'teacher@appget.local',
      password: 'teacher123',
      icon: <GraduationCap className="h-5 w-5" />,
      color: 'from-blue-500 to-blue-600'
    },
    {
      role: 'Étudiant',
      email: 'student@appget.local',
      password: 'student123',
      icon: <User className="h-5 w-5" />,
      color: 'from-green-500 to-green-600'
    }
  ];

  const fillDemoAccount = (email: string, password: string) => {
    setFormData(prev => ({ ...prev, email, password }));
    setErrors({});
  };

  if (loading) {
    return (
      <div className="min-h-screen bg-gradient-to-br from-primary-50 via-blue-50 to-indigo-100 flex items-center justify-center force-desktop w-full">
        <div className="text-center">
          <div className="animate-spin rounded-full h-16 w-16 border-b-2 border-primary-600 mx-auto"></div>
          <p className="mt-4 text-lg text-gray-600">Vérification de l'authentification...</p>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gradient-to-br from-primary-50 via-blue-50 to-indigo-100 force-desktop w-full">
      <div className="min-h-screen flex">
        
        {/* PARTIE GAUCHE - PRÉSENTATION */}
        <div className="hidden lg:flex lg:flex-1 bg-gradient-to-br from-primary-600 via-blue-600 to-indigo-700 p-12 text-white relative overflow-hidden">
          
          {/* Éléments décoratifs */}
          <div className="absolute inset-0 bg-black bg-opacity-10"></div>
          <div className="absolute -top-4 -left-4 w-72 h-72 bg-white bg-opacity-10 rounded-full blur-3xl"></div>
          <div className="absolute -bottom-8 -right-8 w-96 h-96 bg-blue-300 bg-opacity-20 rounded-full blur-3xl"></div>
          
          <div className="relative z-10 flex flex-col justify-center max-w-lg">
            
            {/* Logo et titre */}
            <div className="flex items-center mb-8">
              <div className="w-16 h-16 bg-white bg-opacity-20 rounded-2xl flex items-center justify-center backdrop-blur-sm">
                <Calendar className="h-8 w-8 text-white" />
              </div>
              <div className="ml-4">
                <h1 className="text-4xl font-bold">AppGET</h1>
                <p className="text-xl text-blue-100">Gestion des Emplois du Temps</p>
              </div>
            </div>
            
            <div className="space-y-6">
              <h2 className="text-3xl font-bold leading-tight">
                Optimisez la gestion de votre établissement universitaire
              </h2>
              
              <p className="text-xl text-blue-100 leading-relaxed">
                Une interface moderne et intuitive pour gérer les emplois du temps, 
                les salles, les enseignants et les étudiants en toute simplicité.
              </p>
              
              <div className="space-y-4">
                <div className="flex items-center">
                  <div className="w-2 h-2 bg-green-400 rounded-full mr-4"></div>
                  <span className="text-blue-100">Génération automatique des plannings</span>
                </div>
                <div className="flex items-center">
                  <div className="w-2 h-2 bg-green-400 rounded-full mr-4"></div>
                  <span className="text-blue-100">Interface responsive multi-appareils</span>
                </div>
                <div className="flex items-center">
                  <div className="w-2 h-2 bg-green-400 rounded-full mr-4"></div>
                  <span className="text-blue-100">Rapports et analytics avancés</span>
                </div>
                <div className="flex items-center">
                  <div className="w-2 h-2 bg-green-400 rounded-full mr-4"></div>
                  <span className="text-blue-100">Gestion des conflits intelligente</span>
                </div>
              </div>
            </div>
          </div>
        </div>

        {/* PARTIE DROITE - FORMULAIRE */}
        <div className="flex-1 flex flex-col justify-center px-8 sm:px-12 lg:px-16 xl:px-24 bg-white">
          
          <div className="w-full max-w-md mx-auto">
            
            {/* Header mobile */}
            <div className="lg:hidden text-center mb-8">
              <div className="w-12 h-12 bg-gradient-to-br from-primary-500 to-primary-600 rounded-xl flex items-center justify-center mx-auto mb-4">
                <Calendar className="h-6 w-6 text-white" />
              </div>
              <h1 className="text-2xl font-bold text-gray-900">AppGET</h1>
              <p className="text-gray-600">Gestion des Emplois du Temps</p>
            </div>

            <div className="text-center mb-8">
              <h2 className="text-3xl font-bold text-gray-900 mb-2">
                Connexion à votre compte
              </h2>
              <p className="text-gray-600">
                Accédez à votre interface de gestion personnalisée
              </p>
            </div>

            {/* Formulaire de connexion */}
            <form onSubmit={handleSubmit} className="space-y-6">
              
              {/* Email */}
              <div>
                <label htmlFor="email" className="block text-sm font-medium text-gray-700 mb-2">
                  Adresse email
                </label>
                <div className="relative">
                  <User className="absolute left-3 top-1/2 transform -translate-y-1/2 h-5 w-5 text-gray-400" />
                  <input
                    id="email"
                    name="email"
                    type="email"
                    autoComplete="email"
                    required
                    value={formData.email}
                    onChange={(e) => handleInputChange('email', e.target.value)}
                    className={`
                      w-full pl-10 pr-4 py-3 border rounded-lg text-gray-900 placeholder-gray-500
                      focus:outline-none focus:ring-2 focus:ring-primary-500 focus:border-primary-500
                      transition-all duration-200
                      ${errors.email ? 'border-red-300 bg-red-50' : 'border-gray-300'}
                    `}
                    placeholder="votre@email.com"
                  />
                  {errors.email && (
                    <div className="absolute inset-y-0 right-0 flex items-center pr-3">
                      <AlertCircle className="h-5 w-5 text-red-500" />
                    </div>
                  )}
                </div>
                {errors.email && (
                  <p className="mt-1 text-sm text-red-600 flex items-center">
                    <AlertCircle className="h-3 w-3 mr-1" />
                    {errors.email}
                  </p>
                )}
              </div>

              {/* Mot de passe */}
              <div>
                <label htmlFor="password" className="block text-sm font-medium text-gray-700 mb-2">
                  Mot de passe
                </label>
                <div className="relative">
                  <Lock className="absolute left-3 top-1/2 transform -translate-y-1/2 h-5 w-5 text-gray-400" />
                  <input
                    id="password"
                    name="password"
                    type={showPassword ? 'text' : 'password'}
                    autoComplete="current-password"
                    required
                    value={formData.password}
                    onChange={(e) => handleInputChange('password', e.target.value)}
                    className={`
                      w-full pl-10 pr-12 py-3 border rounded-lg text-gray-900 placeholder-gray-500
                      focus:outline-none focus:ring-2 focus:ring-primary-500 focus:border-primary-500
                      transition-all duration-200
                      ${errors.password ? 'border-red-300 bg-red-50' : 'border-gray-300'}
                    `}
                    placeholder="Votre mot de passe"
                  />
                  <button
                    type="button"
                    onClick={() => setShowPassword(!showPassword)}
                    className="absolute right-3 top-1/2 transform -translate-y-1/2 text-gray-400 hover:text-gray-600"
                  >
                    {showPassword ? (
                      <EyeOff className="h-5 w-5" />
                    ) : (
                      <Eye className="h-5 w-5" />
                    )}
                  </button>
                </div>
                {errors.password && (
                  <p className="mt-1 text-sm text-red-600 flex items-center">
                    <AlertCircle className="h-3 w-3 mr-1" />
                    {errors.password}
                  </p>
                )}
              </div>

              {/* Remember me */}
              <div className="flex items-center justify-between">
                <div className="flex items-center">
                  <input
                    id="rememberMe"
                    name="rememberMe"
                    type="checkbox"
                    checked={formData.rememberMe}
                    onChange={(e) => handleInputChange('rememberMe', e.target.checked)}
                    className="h-4 w-4 text-primary-600 focus:ring-primary-500 border-gray-300 rounded"
                  />
                  <label htmlFor="rememberMe" className="ml-2 text-sm text-gray-700">
                    Se souvenir de moi
                  </label>
                </div>
                <a href="#" className="text-sm text-primary-600 hover:text-primary-700">
                  Mot de passe oublié ?
                </a>
              </div>

              {/* Bouton de connexion */}
              <button
                type="submit"
                disabled={isLoading}
                className={`
                  w-full flex items-center justify-center px-4 py-3 border border-transparent 
                  text-sm font-medium rounded-lg text-white transition-all duration-200
                  ${isLoading 
                    ? 'bg-gray-400 cursor-not-allowed' 
                    : 'bg-gradient-to-r from-primary-600 to-primary-700 hover:from-primary-700 hover:to-primary-800 shadow-lg hover:shadow-xl transform hover:-translate-y-0.5'
                  }
                  focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-primary-500
                `}
              >
                {isLoading ? (
                  <>
                    <div className="animate-spin rounded-full h-4 w-4 border-b-2 border-white mr-2"></div>
                    Connexion en cours...
                  </>
                ) : (
                  <>
                    <LogIn className="h-4 w-4 mr-2" />
                    Se connecter
                  </>
                )}
              </button>
            </form>

            {/* Comptes de démonstration */}
            <div className="mt-8">
              <div className="text-center">
                <p className="text-sm text-gray-500 mb-4">Comptes de démonstration</p>
              </div>
              
              <div className="grid grid-cols-1 gap-3">
                {demoAccounts.map((account) => (
                  <button
                    key={account.role}
                    onClick={() => fillDemoAccount(account.email, account.password)}
                    className={`
                      w-full flex items-center justify-between p-3 rounded-lg border-2 border-dashed
                      border-gray-200 hover:border-primary-300 hover:bg-primary-50
                      transition-all duration-200 text-sm
                    `}
                  >
                    <div className="flex items-center">
                      <div className={`w-8 h-8 bg-gradient-to-r ${account.color} rounded-lg flex items-center justify-center mr-3`}>
                        <div className="text-white">
                          {account.icon}
                        </div>
                      </div>
                      <div className="text-left">
                        <p className="font-medium text-gray-900">{account.role}</p>
                        <p className="text-gray-500">{account.email}</p>
                      </div>
                    </div>
                    <span className="text-primary-600 font-medium">Utiliser</span>
                  </button>
                ))}
              </div>
            </div>

            {/* Footer */}
            <div className="mt-8 text-center text-xs text-gray-500">
              <p>© 2024 AppGET. Tous droits réservés.</p>
              <p className="mt-1">
                Application développée pour la gestion universitaire moderne
              </p>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

export default Login;