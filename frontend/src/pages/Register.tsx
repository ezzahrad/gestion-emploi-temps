import React, { useState } from 'react';
import { Link, useNavigate } from 'react-router-dom';
import { useForm } from 'react-hook-form';
import { motion } from 'framer-motion';
import { UserPlus, Mail, Lock, User, Phone, BookOpen } from 'lucide-react';
import toast from 'react-hot-toast';
import { useAuth } from '../contexts/AuthContext';

interface RegisterForm {
  email: string;
  username: string;
  first_name: string;
  last_name: string;
  role: string;
  phone_number: string;
  password: string;
  password_confirm: string;
}

export const Register: React.FC = () => {
  const {registerUser } = useAuth();
  const navigate = useNavigate();
  const [isLoading, setIsLoading] = useState(false);
  
  const {
    register,
    handleSubmit,
    formState: { errors },
    watch
  } = useForm<RegisterForm>();

  const password = watch('password');

  const onSubmit = async (data: RegisterForm) => {
    setIsLoading(true);
    try {
      await registerUser(data);
      toast.success('Compte créé avec succès!');
      navigate('/dashboard');
    } catch (error: any) {
      const message = error.response?.data?.email?.[0] || 
                     error.response?.data?.username?.[0] ||
                     error.response?.data?.detail || 
                     'Erreur lors de la création du compte';
      toast.error(message);
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <div className="min-h-screen flex items-center justify-center bg-gradient-to-br from-blue-600 via-purple-600 to-indigo-700 py-12">
      <div className="absolute inset-0 bg-black bg-opacity-20"></div>
      
      <motion.div
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ duration: 0.5 }}
        className="relative z-10 max-w-md w-full mx-4"
      >
        <div className="bg-white/95 backdrop-blur-sm rounded-2xl shadow-2xl p-8">
          {/* Logo and title */}
          <div className="text-center mb-8">
            <div className="mx-auto w-16 h-16 bg-gradient-to-br from-blue-600 to-indigo-600 rounded-2xl flex items-center justify-center mb-4">
              <BookOpen className="w-8 h-8 text-white" />
            </div>
            <h1 className="text-2xl font-bold text-gray-900 mb-2">Créer un compte</h1>
            <p className="text-gray-600">Rejoignez SchedulePro</p>
          </div>

          <form onSubmit={handleSubmit(onSubmit)} className="space-y-4">
            {/* Name fields */}
            <div className="grid grid-cols-2 gap-4">
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">
                  Prénom
                </label>
                <div className="relative">
                  <User className="absolute left-3 top-1/2 transform -translate-y-1/2 w-4 h-4 text-gray-400" />
                  <input
                    type="text"
                    {...register('first_name', { required: 'Prénom requis' })}
                    className={`w-full pl-9 pr-3 py-2 border rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500 text-sm ${
                      errors.first_name ? 'border-red-300' : 'border-gray-300'
                    }`}
                    placeholder="Prénom"
                  />
                </div>
                {errors.first_name && (
                  <p className="mt-1 text-xs text-red-600">{errors.first_name.message}</p>
                )}
              </div>

              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">
                  Nom
                </label>
                <input
                  type="text"
                  {...register('last_name', { required: 'Nom requis' })}
                  className={`w-full px-3 py-2 border rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500 text-sm ${
                    errors.last_name ? 'border-red-300' : 'border-gray-300'
                  }`}
                  placeholder="Nom"
                />
                {errors.last_name && (
                  <p className="mt-1 text-xs text-red-600">{errors.last_name.message}</p>
                )}
              </div>
            </div>

            {/* Email field */}
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">
                Email
              </label>
              <div className="relative">
                <Mail className="absolute left-3 top-1/2 transform -translate-y-1/2 w-4 h-4 text-gray-400" />
                <input
                  type="email"
                  {...register('email', { 
                    required: 'Email requis',
                    pattern: {
                      value: /^\S+@\S+$/i,
                      message: 'Email invalide'
                    }
                  })}
                  className={`w-full pl-9 pr-3 py-2 border rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500 text-sm ${
                    errors.email ? 'border-red-300' : 'border-gray-300'
                  }`}
                  placeholder="votre@email.com"
                />
              </div>
              {errors.email && (
                <p className="mt-1 text-xs text-red-600">{errors.email.message}</p>
              )}
            </div>

            {/* Username field */}
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">
                Nom d'utilisateur
              </label>
              <input
                type="text"
                {...register('username', { required: 'Nom d\'utilisateur requis' })}
                className={`w-full px-3 py-2 border rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500 text-sm ${
                  errors.username ? 'border-red-300' : 'border-gray-300'
                }`}
                placeholder="nom_utilisateur"
              />
              {errors.username && (
                <p className="mt-1 text-xs text-red-600">{errors.username.message}</p>
              )}
            </div>

            {/* Role field */}
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">
                Rôle
              </label>
              <select
                {...register('role', { required: 'Rôle requis' })}
                className={`w-full px-3 py-2 border rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500 text-sm ${
                  errors.role ? 'border-red-300' : 'border-gray-300'
                }`}
              >
                <option value="">Sélectionner un rôle</option>
                <option value="admin">Administrateur Pédagogique</option>
                <option value="department_head">Chef de Département</option>
                <option value="program_head">Chef de Filière</option>
                <option value="teacher">Enseignant</option>
                <option value="student">Étudiant</option>
              </select>
              {errors.role && (
                <p className="mt-1 text-xs text-red-600">{errors.role.message}</p>
              )}
            </div>

            {/* Phone field */}
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">
                Téléphone (optionnel)
              </label>
              <div className="relative">
                <Phone className="absolute left-3 top-1/2 transform -translate-y-1/2 w-4 h-4 text-gray-400" />
                <input
                  type="tel"
                  {...register('phone_number')}
                  className="w-full pl-9 pr-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500 text-sm"
                  placeholder="+33 6 12 34 56 78"
                />
              </div>
            </div>

            {/* Password fields */}
            <div className="grid grid-cols-1 gap-4">
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">
                  Mot de passe
                </label>
                <div className="relative">
                  <Lock className="absolute left-3 top-1/2 transform -translate-y-1/2 w-4 h-4 text-gray-400" />
                  <input
                    type="password"
                    {...register('password', { 
                      required: 'Mot de passe requis',
                      minLength: {
                        value: 8,
                        message: 'Minimum 8 caractères'
                      }
                    })}
                    className={`w-full pl-9 pr-3 py-2 border rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500 text-sm ${
                      errors.password ? 'border-red-300' : 'border-gray-300'
                    }`}
                    placeholder="••••••••"
                  />
                </div>
                {errors.password && (
                  <p className="mt-1 text-xs text-red-600">{errors.password.message}</p>
                )}
              </div>

              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">
                  Confirmer le mot de passe
                </label>
                <div className="relative">
                  <Lock className="absolute left-3 top-1/2 transform -translate-y-1/2 w-4 h-4 text-gray-400" />
                  <input
                    type="password"
                    {...register('password_confirm', { 
                      required: 'Confirmation requise',
                      validate: value => value === password || 'Les mots de passe ne correspondent pas'
                    })}
                    className={`w-full pl-9 pr-3 py-2 border rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500 text-sm ${
                      errors.password_confirm ? 'border-red-300' : 'border-gray-300'
                    }`}
                    placeholder="••••••••"
                  />
                </div>
                {errors.password_confirm && (
                  <p className="mt-1 text-xs text-red-600">{errors.password_confirm.message}</p>
                )}
              </div>
            </div>

            {/* Submit button */}
            <motion.button
              whileHover={{ scale: 1.01 }}
              whileTap={{ scale: 0.99 }}
              type="submit"
              disabled={isLoading}
              className="w-full bg-gradient-to-r from-blue-600 to-indigo-600 text-white py-3 px-4 rounded-lg font-medium hover:from-blue-700 hover:to-indigo-700 focus:ring-2 focus:ring-blue-500 focus:ring-offset-2 transition-all duration-200 disabled:opacity-50 disabled:cursor-not-allowed flex items-center justify-center"
            >
              {isLoading ? (
                <div className="w-5 h-5 border-2 border-white border-t-transparent rounded-full animate-spin" />
              ) : (
                <>
                  <UserPlus className="w-5 h-5 mr-2" />
                  Créer le compte
                </>
              )}
            </motion.button>
          </form>

          {/* Login link */}
          <div className="mt-6 text-center">
            <p className="text-sm text-gray-600">
              Déjà un compte?{' '}
              <Link 
                to="/login" 
                className="text-blue-600 hover:text-blue-700 font-medium transition-colors"
              >
                Se connecter
              </Link>
            </p>
          </div>
        </div>
      </motion.div>
    </div>
  );
};