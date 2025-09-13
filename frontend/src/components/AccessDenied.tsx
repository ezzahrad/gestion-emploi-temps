// AccessDenied.tsx - Composant pour afficher un message d'accès refusé
import React from 'react';
import { Lock } from 'lucide-react';
import { useNavigate } from 'react-router-dom';

interface AccessDeniedProps {
  userRole?: string;
  requiredRole?: string;
  returnPath?: string;
}

const AccessDenied: React.FC<AccessDeniedProps> = ({
  userRole = '',
  requiredRole = '',
  returnPath = '/dashboard'
}) => {
  const navigate = useNavigate();

  return (
    <div className="min-h-screen flex items-center justify-center bg-gray-50">
      <div className="max-w-md w-full bg-white rounded-lg shadow-lg p-8 text-center">
        <Lock className="h-16 w-16 text-red-500 mx-auto mb-4" />
        <h2 className="text-2xl font-bold text-gray-900 mb-2">Accès refusé</h2>
        <p className="text-gray-600 mb-6">
          Vous n'avez pas les permissions nécessaires pour accéder à cette page.
        </p>
        <div className="space-y-2 text-sm text-gray-500 mb-6">
          <p><strong>Votre rôle:</strong> {userRole}</p>
          <p><strong>Rôle requis:</strong> {requiredRole}</p>
        </div>
        <button
          onClick={() => navigate(returnPath)}
          className="w-full bg-primary-600 text-white py-2 px-4 rounded-lg hover:bg-primary-700 transition-colors duration-200"
        >
          Retour
        </button>
      </div>
    </div>
  );
};

export default AccessDenied;