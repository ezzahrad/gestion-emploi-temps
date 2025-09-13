// Test de la liaison Backend/Frontend
import React, { useState, useEffect } from 'react';
import { api, authAPI, coreAPI, scheduleAPI } from '../services/api';
import { useAuth } from '../contexts/AuthContext';
import { CheckCircle, XCircle, Clock, RefreshCw, AlertTriangle, Zap } from 'lucide-react';

interface TestResult {
  name: string;
  status: 'pending' | 'success' | 'error';
  message: string;
  duration?: number;
}

const ConnectionTest: React.FC = () => {
  const { user } = useAuth();
  const [tests, setTests] = useState<TestResult[]>([]);
  const [isRunning, setIsRunning] = useState(false);
  const [summary, setSummary] = useState({ total: 0, passed: 0, failed: 0 });

  const testCases = [
    {
      name: 'Connexion API de base',
      test: async () => {
        const response = await fetch(api.defaults.baseURL + '/');
        if (response.ok || response.status === 404) return 'Backend accessible';
        throw new Error(`Status: ${response.status}`);
      }
    },
    {
      name: 'Authentification JWT',
      test: async () => {
        if (!user) throw new Error('Utilisateur non connecté');
        const response = await authAPI.getProfile();
        return `Profil récupéré: ${response.data.full_name}`;
      }
    },
    {
      name: 'API Départements',
      test: async () => {
        const response = await coreAPI.getDepartments();
        return `${response.data.length || 0} départements trouvés`;
      }
    },
    {
      name: 'API Programmes',
      test: async () => {
        const response = await coreAPI.getPrograms();
        return `${response.data.length || 0} programmes trouvés`;
      }
    },
    {
      name: 'API Enseignants',
      test: async () => {
        const response = await coreAPI.getTeachers();
        return `${response.data.length || 0} enseignants trouvés`;
      }
    },
    {
      name: 'API Étudiants',
      test: async () => {
        const response = await coreAPI.getStudents();
        return `${response.data.length || 0} étudiants trouvés`;
      }
    },
    {
      name: 'API Salles',
      test: async () => {
        const response = await coreAPI.getRooms();
        return `${response.data.length || 0} salles trouvées`;
      }
    },
    {
      name: 'API Matières',
      test: async () => {
        const response = await coreAPI.getSubjects();
        return `${response.data.length || 0} matières trouvées`;
      }
    },
    {
      name: 'API Emplois du temps',
      test: async () => {
        const response = await scheduleAPI.getSchedules();
        return `${response.data.length || 0} emplois du temps trouvés`;
      }
    },
    {
      name: 'Configuration CORS',
      test: async () => {
        // Test d'une requête cross-origin
        const response = await api.get('/');
        return 'CORS configuré correctement';
      }
    }
  ];

  const runSingleTest = async (testCase: any, index: number): Promise<TestResult> => {
    const startTime = Date.now();
    
    try {
      const message = await testCase.test();
      const duration = Date.now() - startTime;
      
      return {
        name: testCase.name,
        status: 'success',
        message,
        duration
      };
    } catch (error: any) {
      const duration = Date.now() - startTime;
      
      return {
        name: testCase.name,
        status: 'error',
        message: error.message || 'Erreur inconnue',
        duration
      };
    }
  };

  const runAllTests = async () => {
    setIsRunning(true);
    setTests([]);
    
    // Initialize tests with pending status
    const initialTests = testCases.map(testCase => ({
      name: testCase.name,
      status: 'pending' as const,
      message: 'En cours...'
    }));
    setTests(initialTests);

    const results: TestResult[] = [];
    
    // Run tests sequentially with updates
    for (let i = 0; i < testCases.length; i++) {
      const result = await runSingleTest(testCases[i], i);
      results.push(result);
      
      // Update the specific test result
      setTests(prev => 
        prev.map((test, index) => 
          index === i ? result : test
        )
      );
    }

    // Calculate summary
    const passed = results.filter(r => r.status === 'success').length;
    const failed = results.filter(r => r.status === 'error').length;
    
    setSummary({
      total: results.length,
      passed,
      failed
    });

    setIsRunning(false);
  };

  const getStatusIcon = (status: TestResult['status']) => {
    switch (status) {
      case 'pending':
        return <Clock className="h-5 w-5 text-yellow-500 animate-spin" />;
      case 'success':
        return <CheckCircle className="h-5 w-5 text-green-500" />;
      case 'error':
        return <XCircle className="h-5 w-5 text-red-500" />;
    }
  };

  const getStatusColor = (status: TestResult['status']) => {
    switch (status) {
      case 'pending':
        return 'border-yellow-200 bg-yellow-50';
      case 'success':
        return 'border-green-200 bg-green-50';
      case 'error':
        return 'border-red-200 bg-red-50';
    }
  };

  useEffect(() => {
    // Auto-run tests on component mount
    runAllTests();
  }, []);

  return (
    <div className="min-h-screen bg-gray-50">
      <div className="max-w-4xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        
        {/* Header */}
        <div className="mb-8">
          <div className="flex items-center justify-between">
            <div>
              <h1 className="text-3xl font-bold text-gray-900 flex items-center">
                <Zap className="h-8 w-8 text-blue-600 mr-3" />
                Test de Liaison Backend/Frontend
              </h1>
              <p className="text-gray-600 mt-2">
                Vérification de la connectivité et des API
              </p>
            </div>
            <button
              onClick={runAllTests}
              disabled={isRunning}
              className="btn-primary flex items-center"
            >
              <RefreshCw className={`h-4 w-4 mr-2 ${isRunning ? 'animate-spin' : ''}`} />
              {isRunning ? 'Tests en cours...' : 'Relancer les tests'}
            </button>
          </div>
        </div>

        {/* Summary */}
        {summary.total > 0 && (
          <div className="mb-8 grid grid-cols-1 md:grid-cols-3 gap-4">
            <div className="bg-white rounded-xl shadow-sm border border-gray-200 p-6">
              <div className="flex items-center">
                <div className="flex-shrink-0">
                  <div className="h-10 w-10 bg-blue-100 rounded-lg flex items-center justify-center">
                    <Clock className="h-6 w-6 text-blue-600" />
                  </div>
                </div>
                <div className="ml-4">
                  <p className="text-sm font-medium text-gray-500">Total</p>
                  <p className="text-2xl font-bold text-gray-900">{summary.total}</p>
                </div>
              </div>
            </div>

            <div className="bg-white rounded-xl shadow-sm border border-gray-200 p-6">
              <div className="flex items-center">
                <div className="flex-shrink-0">
                  <div className="h-10 w-10 bg-green-100 rounded-lg flex items-center justify-center">
                    <CheckCircle className="h-6 w-6 text-green-600" />
                  </div>
                </div>
                <div className="ml-4">
                  <p className="text-sm font-medium text-gray-500">Réussis</p>
                  <p className="text-2xl font-bold text-green-600">{summary.passed}</p>
                </div>
              </div>
            </div>

            <div className="bg-white rounded-xl shadow-sm border border-gray-200 p-6">
              <div className="flex items-center">
                <div className="flex-shrink-0">
                  <div className="h-10 w-10 bg-red-100 rounded-lg flex items-center justify-center">
                    <XCircle className="h-6 w-6 text-red-600" />
                  </div>
                </div>
                <div className="ml-4">
                  <p className="text-sm font-medium text-gray-500">Échoués</p>
                  <p className="text-2xl font-bold text-red-600">{summary.failed}</p>
                </div>
              </div>
            </div>
          </div>
        )}

        {/* Test Results */}
        <div className="bg-white rounded-xl shadow-sm border border-gray-200 overflow-hidden">
          <div className="px-6 py-4 border-b border-gray-200">
            <h2 className="text-lg font-semibold text-gray-900">Résultats des tests</h2>
          </div>
          
          <div className="divide-y divide-gray-200">
            {tests.map((test, index) => (
              <div key={index} className={`p-6 border-l-4 ${getStatusColor(test.status)}`}>
                <div className="flex items-start justify-between">
                  <div className="flex items-start">
                    <div className="flex-shrink-0 pt-0.5">
                      {getStatusIcon(test.status)}
                    </div>
                    <div className="ml-3">
                      <h3 className="text-sm font-medium text-gray-900">
                        {test.name}
                      </h3>
                      <p className={`text-sm mt-1 ${
                        test.status === 'error' ? 'text-red-600' :
                        test.status === 'success' ? 'text-green-600' :
                        'text-yellow-600'
                      }`}>
                        {test.message}
                      </p>
                    </div>
                  </div>
                  {test.duration && (
                    <div className="flex-shrink-0">
                      <span className="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium bg-gray-100 text-gray-800">
                        {test.duration}ms
                      </span>
                    </div>
                  )}
                </div>
              </div>
            ))}
          </div>
        </div>

        {/* Configuration Info */}
        <div className="mt-8 bg-blue-50 border border-blue-200 rounded-xl p-6">
          <div className="flex items-start">
            <div className="flex-shrink-0">
              <AlertTriangle className="h-5 w-5 text-blue-600" />
            </div>
            <div className="ml-3">
              <h3 className="text-sm font-medium text-blue-800">
                Configuration actuelle
              </h3>
              <div className="mt-2 text-sm text-blue-700">
                <ul className="space-y-1">
                  <li><strong>API URL:</strong> {api.defaults.baseURL}</li>
                  <li><strong>Utilisateur connecté:</strong> {user?.full_name || 'Non connecté'}</li>
                  <li><strong>Rôle:</strong> {user?.role || 'N/A'}</li>
                  <li><strong>Frontend URL:</strong> {window.location.origin}</li>
                </ul>
              </div>
            </div>
          </div>
        </div>

        {/* Troubleshooting */}
        {summary.failed > 0 && (
          <div className="mt-8 bg-red-50 border border-red-200 rounded-xl p-6">
            <div className="flex items-start">
              <div className="flex-shrink-0">
                <XCircle className="h-5 w-5 text-red-600" />
              </div>
              <div className="ml-3">
                <h3 className="text-sm font-medium text-red-800">
                  Dépannage
                </h3>
                <div className="mt-2 text-sm text-red-700">
                  <p className="mb-2">Si des tests échouent, vérifiez :</p>
                  <ul className="list-disc list-inside space-y-1">
                    <li>Le backend Django est démarré (port 8000)</li>
                    <li>La base de données est accessible</li>
                    <li>Les migrations sont appliquées</li>
                    <li>La configuration CORS est correcte</li>
                    <li>L'utilisateur a les permissions nécessaires</li>
                  </ul>
                </div>
              </div>
            </div>
          </div>
        )}

      </div>
    </div>
  );
};

export default ConnectionTest;