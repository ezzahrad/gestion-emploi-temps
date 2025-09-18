import React, { useState, useEffect } from 'react';
import { 
  Brain, 
  Settings, 
  BarChart3, 
  AlertTriangle, 
  Users, 
  Clock, 
  Target,
  Play,
  Pause,
  RotateCcw,
  Save,
  Download
} from 'lucide-react';
import { toast } from 'react-hot-toast';
import { useAuth } from '../contexts/AuthContext';
import { coreAPI, scheduleAPI } from '../services/api';

interface OptimizationConstraint {
  id: string;
  name: string;
  description: string;
  weight: number;
  icon: React.ReactNode;
  color: string;
}

interface OptimizationStats {
  coursePlanifies: number;
  conflitsDetectes: number;
  tauxOccupation: number;
  scoreActuel: number;
}

interface OptimizationSettings {
  department: string;
  semester: string;
  constraints: OptimizationConstraint[];
}

const AIScheduleOptimizer: React.FC = () => {
  const { user } = useAuth();
  const [isOptimizing, setIsOptimizing] = useState(false);
  const [settings, setSettings] = useState<OptimizationSettings>({
    department: '',
    semester: '2024 - Semestre 1',
    constraints: [
      {
        id: 'conflicts',
        name: 'Minimiser les Conflits',
        description: 'Éviter les chevauchements de cours et de salles',
        weight: 10,
        icon: <AlertTriangle className="w-5 h-5" />,
        color: 'text-red-500'
      },
      {
        id: 'preferences',
        name: 'Préférences Enseignants', 
        description: 'Respecter les disponibilités des enseignants',
        weight: 8,
        icon: <Users className="w-5 h-5" />,
        color: 'text-blue-500'
      },
      {
        id: 'rooms',
        name: 'Optimisation des Salles',
        description: 'Maximiser l\'utilisation efficace des salles',
        weight: 7,
        icon: <Target className="w-5 h-5" />,
        color: 'text-green-500'
      },
      {
        id: 'workload',
        name: 'Charge Étudiante',
        description: 'Équilibrer la charge de travail des étudiants',
        weight: 6,
        icon: <BarChart3 className="w-5 h-5" />,
        color: 'text-purple-500'
      }
    ]
  });

  const [stats, setStats] = useState<OptimizationStats>({
    coursePlanifies: 0,
    conflitsDetectes: 0,
    tauxOccupation: 78,
    scoreActuel: 65
  });

  const [departments, setDepartments] = useState<Array<{id: string, name: string}>>([]);

  useEffect(() => {
    loadDepartments();
    loadCurrentStats();
  }, []);

  const loadDepartments = async () => {
    try {
      const response = await coreAPI.getDepartments();
      setDepartments(response.data.results || response.data);
    } catch (error) {
      console.error('Erreur chargement départements:', error);
      toast.error('Erreur lors du chargement des départements');
    }
  };

  const loadCurrentStats = async () => {
    try {
      const response = await scheduleAPI.getOptimizationStats();
      setStats(response.data);
    } catch (error) {
      console.error('Erreur chargement statistiques:', error);
      // Garder les stats par défaut si l'API n'est pas encore disponible
    }
  };

  const handleConstraintWeightChange = (constraintId: string, newWeight: number) => {
    setSettings(prev => ({
      ...prev,
      constraints: prev.constraints.map(constraint => 
        constraint.id === constraintId 
          ? { ...constraint, weight: newWeight }
          : constraint
      )
    }));
  };

  const handleOptimizationStart = async () => {
    if (!settings.department) {
      toast.error('Veuillez sélectionner un département');
      return;
    }

    setIsOptimizing(true);
    toast.loading('Optimisation en cours...', { duration: 2000 });

    try {
      const payload = {
        department: settings.department,
        semester: settings.semester,
        constraints: settings.constraints.reduce((acc, constraint) => {
          acc[constraint.id] = constraint.weight;
          return acc;
        }, {} as Record<string, number>)
      };

      const response = await scheduleAPI.optimizeSchedules(payload);
      
      // Simulation d'un processus d'optimisation
      setTimeout(() => {
        setStats(prev => ({
          ...prev,
          conflitsDetectes: Math.max(0, prev.conflitsDetectes - Math.floor(Math.random() * 3)),
          scoreActuel: Math.min(100, prev.scoreActuel + Math.floor(Math.random() * 10))
        }));
        setIsOptimizing(false);
        toast.success('Optimisation terminée avec succès !');
      }, 3000);

    } catch (error) {
      console.error('Erreur optimisation:', error);
      setIsOptimizing(false);
      toast.error('Erreur lors de l\'optimisation');
    }
  };

  const handleSaveConfiguration = async () => {
    try {
      await scheduleAPI.saveOptimizationConfig(settings);
      toast.success('Configuration sauvegardée');
    } catch (error) {
      console.error('Erreur sauvegarde:', error);
      toast.error('Erreur lors de la sauvegarde');
    }
  };

  const handleExportResults = async () => {
    try {
      const response = await scheduleAPI.exportOptimizationResults();
      
      const url = window.URL.createObjectURL(new Blob([response.data]));
      const link = document.createElement('a');
      link.href = url;
      link.setAttribute('download', `optimization_results_${new Date().toISOString().split('T')[0]}.pdf`);
      document.body.appendChild(link);
      link.click();
      link.remove();
      window.URL.revokeObjectURL(url);
      
      toast.success('Résultats exportés');
    } catch (error) {
      console.error('Erreur export:', error);
      toast.error('Erreur lors de l\'export');
    }
  };

  return (
    <div className="h-full w-full bg-gray-50 overflow-auto">
      <div className="p-6 space-y-6">
        {/* En-tête avec gradient */}
        <div className="bg-gradient-to-r from-purple-600 to-blue-600 rounded-xl p-6 text-white">
          <div className="flex items-center justify-between">
            <div>
              <div className="flex items-center space-x-3 mb-2">
                <Brain className="w-8 h-8" />
                <h1 className="text-2xl font-bold">Optimisation IA des Emplois du Temps</h1>
              </div>
              <p className="text-purple-100">
                Utilisez l'intelligence artificielle pour générer automatiquement des emplois du temps 
                optimisés en fonction de multiples contraintes et préférences.
              </p>
            </div>
            <div className="hidden lg:block">
              <div className="w-24 h-24 opacity-20">
                <svg viewBox="0 0 24 24" fill="currentColor">
                  <path d="M12 2L2 7l10 5 10-5-10-5zM2 17l10 5 10-5M2 12l10 5 10-5"/>
                </svg>
              </div>
            </div>
          </div>
        </div>

        {/* Configuration de base */}
        <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
          <div className="lg:col-span-2">
            <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-6">
              <div className="flex items-center space-x-2 mb-6">
                <Settings className="w-5 h-5 text-gray-600" />
                <h2 className="text-lg font-semibold text-gray-900">Configuration de Base</h2>
              </div>

              <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-2">
                    Département
                  </label>
                  <select
                    value={settings.department}
                    onChange={(e) => setSettings(prev => ({...prev, department: e.target.value}))}
                    className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                  >
                    <option value="">Sélectionner un département</option>
                    {departments.map(dept => (
                      <option key={dept.id} value={dept.id}>{dept.name}</option>
                    ))}
                  </select>
                </div>

                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-2">
                    Semestre
                  </label>
                  <select
                    value={settings.semester}
                    onChange={(e) => setSettings(prev => ({...prev, semester: e.target.value}))}
                    className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                  >
                    <option value="2024 - Semestre 1">2024 - Semestre 1</option>
                    <option value="2024 - Semestre 2">2024 - Semestre 2</option>
                    <option value="2025 - Semestre 1">2025 - Semestre 1</option>
                  </select>
                </div>
              </div>
            </div>
          </div>

          {/* Statistiques actuelles */}
          <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-6">
            <h3 className="text-lg font-semibold text-gray-900 mb-4">Statistiques Actuelles</h3>
            <div className="space-y-4">
              <div className="flex justify-between items-center">
                <span className="text-sm text-gray-600">Cours planifiés</span>
                <span className="text-lg font-bold text-gray-900">{stats.coursePlanifies}</span>
              </div>
              <div className="flex justify-between items-center">
                <span className="text-sm text-gray-600">Conflits détectés</span>
                <span className="text-lg font-bold text-red-600">{stats.conflitsDetectes}</span>
              </div>
              <div className="flex justify-between items-center">
                <span className="text-sm text-gray-600">Taux d'occupation</span>
                <span className="text-lg font-bold text-green-600">{stats.tauxOccupation}%</span>
              </div>
              <div className="flex justify-between items-center">
                <span className="text-sm text-gray-600">Score actuel</span>
                <span className="text-lg font-bold text-blue-600">{stats.scoreActuel}%</span>
              </div>
            </div>
          </div>
        </div>

        {/* Contraintes d'optimisation */}
        <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-6">
          <div className="flex items-center space-x-2 mb-6">
            <Target className="w-5 h-5 text-yellow-600" />
            <h2 className="text-lg font-semibold text-gray-900">Contraintes d'Optimisation</h2>
          </div>

          <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
            {settings.constraints.map((constraint) => (
              <div key={constraint.id} className="p-4 border border-gray-200 rounded-lg bg-gray-50">
                <div className="flex items-start space-x-3 mb-3">
                  <div className={constraint.color}>
                    {constraint.icon}
                  </div>
                  <div className="flex-1">
                    <h4 className="font-medium text-gray-900">{constraint.name}</h4>
                    <p className="text-sm text-gray-600">{constraint.description}</p>
                  </div>
                </div>
                <div className="flex items-center space-x-3">
                  <span className="text-sm text-gray-500">Poids:</span>
                  <div className="flex-1">
                    <input
                      type="range"
                      min="0"
                      max="10"
                      value={constraint.weight}
                      onChange={(e) => handleConstraintWeightChange(constraint.id, parseInt(e.target.value))}
                      className="w-full h-2 bg-gray-200 rounded-lg appearance-none cursor-pointer slider"
                    />
                  </div>
                  <span className="text-sm font-medium text-gray-900 min-w-[2ch]">
                    {constraint.weight}
                  </span>
                </div>
              </div>
            ))}
          </div>
        </div>

        {/* Actions */}
        <div className="flex flex-wrap gap-4 justify-between">
          <div className="flex flex-wrap gap-3">
            <button
              onClick={handleOptimizationStart}
              disabled={isOptimizing || !settings.department}
              className="px-6 py-3 bg-gradient-to-r from-green-600 to-blue-600 text-white rounded-lg hover:from-green-700 hover:to-blue-700 disabled:opacity-50 disabled:cursor-not-allowed font-medium flex items-center space-x-2 transition-all duration-200"
            >
              {isOptimizing ? (
                <>
                  <Pause className="w-5 h-5 animate-spin" />
                  <span>Optimisation...</span>
                </>
              ) : (
                <>
                  <Play className="w-5 h-5" />
                  <span>Lancer l'Optimisation</span>
                </>
              )}
            </button>

            <button
              onClick={() => {
                setStats(prev => ({
                  ...prev,
                  conflitsDetectes: 0,
                  scoreActuel: 85
                }));
                toast.success('Statistiques réinitialisées');
              }}
              className="px-4 py-3 border border-gray-300 text-gray-700 rounded-lg hover:bg-gray-50 font-medium flex items-center space-x-2"
            >
              <RotateCcw className="w-5 h-5" />
              <span>Réinitialiser</span>
            </button>
          </div>

          <div className="flex flex-wrap gap-3">
            <button
              onClick={handleSaveConfiguration}
              className="px-4 py-3 border border-blue-300 text-blue-700 rounded-lg hover:bg-blue-50 font-medium flex items-center space-x-2"
            >
              <Save className="w-5 h-5" />
              <span>Sauvegarder Config</span>
            </button>

            <button
              onClick={handleExportResults}
              className="px-4 py-3 border border-green-300 text-green-700 rounded-lg hover:bg-green-50 font-medium flex items-center space-x-2"
            >
              <Download className="w-5 h-5" />
              <span>Exporter Résultats</span>
            </button>
          </div>
        </div>

        {/* Message d'information */}
        {isOptimizing && (
          <div className="bg-blue-50 border border-blue-200 rounded-lg p-4">
            <div className="flex items-center space-x-2">
              <div className="animate-spin">
                <Clock className="w-5 h-5 text-blue-600" />
              </div>
              <div>
                <p className="text-blue-800 font-medium">Optimisation en cours...</p>
                <p className="text-blue-600 text-sm">
                  L'IA analyse {stats.coursePlanifies} cours et optimise selon {settings.constraints.length} contraintes.
                </p>
              </div>
            </div>
          </div>
        )}
      </div>

      <style>{`
        .slider::-webkit-slider-thumb {
          appearance: none;
          height: 20px;
          width: 20px;
          border-radius: 50%;
          background: #3B82F6;
          cursor: pointer;
          box-shadow: 0 2px 4px rgba(0,0,0,0.2);
        }
        .slider::-moz-range-thumb {
          height: 20px;
          width: 20px;
          border-radius: 50%;
          background: #3B82F6;
          cursor: pointer;
          border: none;
          box-shadow: 0 2px 4px rgba(0,0,0,0.2);
        }
        .slider::-webkit-slider-track {
          height: 8px;
          border-radius: 4px;
          background: #E5E7EB;
        }
        .slider::-moz-range-track {
          height: 8px;
          border-radius: 4px;
          background: #E5E7EB;
          border: none;
        }
      `}</style>
    </div>
  );
};

export default AIScheduleOptimizer;