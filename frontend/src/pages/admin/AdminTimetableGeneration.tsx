// AdminTimetableGeneration.tsx - Génération automatique d'emploi du temps avec OR-Tools
import React, { useState, useEffect } from 'react';
import { useAuth, useAuthenticatedFetch } from '../../contexts/AuthContext';
import { 
  Settings, Calendar, Users, BookOpen, MapPin, Clock,
  AlertCircle, CheckCircle, RefreshCw, Play, Eye, X,
  TrendingUp, BarChart3, Zap, Target, Activity
} from 'lucide-react';
import { toast } from 'react-hot-toast';
import { useNavigate } from 'react-router-dom';
import { format, addDays } from 'date-fns';
import { fr } from 'date-fns/locale';

// Types
interface Program {
  id: number;
  name: string;
  code: string;
  level: string;
  department_name: string;
  total_students: number;
  total_subjects: number;
}

interface GenerationParams {
  start_date: string;
  end_date: string;
  program_ids: number[];
  include_weekends: boolean;
  max_sessions_per_day: number;
  preferred_time_slots: string[];
}

interface GenerationLog {
  id: number;
  generated_by_name: string;
  generation_date: string;
  status: 'pending' | 'success' | 'failed' | 'optimizing';
  status_display: string;
  start_date: string;
  end_date: string;
  programs_list: string[];
  total_sessions_planned: number;
  conflicts_resolved: number;
  optimization_score: number;
  efficiency_score: number;
  processing_time: number;
  execution_log: string;
}

const AdminTimetableGeneration: React.FC = () => {
  const { user, hasPermission } = useAuth();
  const authenticatedFetch = useAuthenticatedFetch();
  const navigate = useNavigate();

  // États
  const [programs, setPrograms] = useState<Program[]>([]);
  const [generationLogs, setGenerationLogs] = useState<GenerationLog[]>([]);
  const [loading, setLoading] = useState(false);
  const [generating, setGenerating] = useState(false);
  const [selectedLog, setSelectedLog] = useState<GenerationLog | null>(null);

  // Paramètres de génération
  const [params, setParams] = useState<GenerationParams>({
    start_date: format(new Date(), 'yyyy-MM-dd'),
    end_date: format(addDays(new Date(), 90), 'yyyy-MM-dd'), // 3 mois
    program_ids: [],
    include_weekends: false,
    max_sessions_per_day: 6,
    preferred_time_slots: []
  });

  // États de l'interface
  const [showAdvancedOptions, setShowAdvancedOptions] = useState(false);

  useEffect(() => {
    if (hasPermission('generate_timetable')) {
      loadPrograms();
      loadGenerationLogs();
    } else {
      navigate('/dashboard');
      toast.error('Accès non autorisé');
    }
  }, []);

  const loadPrograms = async () => {
    try {
      const response = await authenticatedFetch('/api/core/programs/');
      if (response.ok) {
        const data = await response.json();
        setPrograms(data.results || []);
      }
    } catch (error) {
      console.error('Erreur lors du chargement des programmes:', error);
    }
  };

  const loadGenerationLogs = async () => {
    try {
      setLoading(true);
      // Fonctionnalité temporairement désactivée
      console.log('Generation logs - fonctionnalité en développement');
      setGenerationLogs([]);
      /*
      const response = await authenticatedFetch('/api/timetable-generations/');
      if (response.ok) {
        const data = await response.json();
        setGenerationLogs(data.results || []);
      }
      */
    } catch (error) {
      console.error('Erreur lors du chargement des logs:', error);
    } finally {
      setLoading(false);
    }
  };

  const handleGenerate = async () => {
    if (!params.start_date || !params.end_date) {
      toast.error('Veuillez sélectionner les dates de début et fin');
      return;
    }

    if (new Date(params.end_date) <= new Date(params.start_date)) {
      toast.error('La date de fin doit être postérieure à la date de début');
      return;
    }

    if (params.program_ids.length === 0) {
      toast.error('Veuillez sélectionner au moins un programme');
      return;
    }

    setGenerating(true);

    try {
      toast.loading('Génération de l\'emploi du temps en cours...', { id: 'generate' });

      const response = await authenticatedFetch('/api/generate/timetable/', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(params),
      });

      const result = await response.json();

      if (response.ok && result.success) {
        toast.success('Emploi du temps généré avec succès !', { id: 'generate' });
        
        // Recharger les logs
        await loadGenerationLogs();
        
        // Afficher les statistiques
        toast.success(
          `${result.stats.total_sessions_planned} séances planifiées, ` +
          `${result.stats.conflicts_resolved} conflits résolus`
        );
      } else {
        throw new Error(result.error || 'Erreur lors de la génération');
      }
    } catch (error: any) {
      console.error('Erreur génération:', error);
      toast.error(error.message || 'Erreur lors de la génération', { id: 'generate' });
    } finally {
      setGenerating(false);
    }
  };

  const handleProgramSelection = (programId: number, checked: boolean) => {
    setParams(prev => ({
      ...prev,
      program_ids: checked
        ? [...prev.program_ids, programId]
        : prev.program_ids.filter(id => id !== programId)
    }));
  };

  const selectAllPrograms = () => {
    setParams(prev => ({
      ...prev,
      program_ids: programs.map(p => p.id)
    }));
  };

  const deselectAllPrograms = () => {
    setParams(prev => ({
      ...prev,
      program_ids: []
    }));
  };

  const getStatusColor = (status: string) => {
    switch (status) {
      case 'success': return 'text-green-600 bg-green-100';
      case 'failed': return 'text-red-600 bg-red-100';
      case 'optimizing': return 'text-blue-600 bg-blue-100';
      case 'pending': return 'text-yellow-600 bg-yellow-100';
      default: return 'text-gray-600 bg-gray-100';
    }
  };

  const getStatusIcon = (status: string) => {
    switch (status) {
      case 'success': return <CheckCircle className="h-5 w-5" />;
      case 'failed': return <AlertCircle className="h-5 w-5" />;
      case 'optimizing': return <RefreshCw className="h-5 w-5 animate-spin" />;
      case 'pending': return <Clock className="h-5 w-5" />;
      default: return <Settings className="h-5 w-5" />;
    }
  };

  const getScoreColor = (score: number) => {
    if (score >= 80) return 'text-green-600';
    if (score >= 60) return 'text-yellow-600';
    return 'text-red-600';
  };

  const LogDetailsModal = ({ log, onClose }: { log: GenerationLog | null, onClose: () => void }) => {
    if (!log) return null;

    return (
      <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center p-4 z-50">
        <div className="bg-white rounded-lg shadow-xl max-w-4xl w-full max-h-[90vh] overflow-hidden">
          <div className="flex items-center justify-between p-6 border-b">
            <h3 className="text-lg font-semibold">Détails de la génération</h3>
            <button
              onClick={onClose}
              className="text-gray-400 hover:text-gray-600"
            >
              <X className="h-6 w-6" />
            </button>
          </div>
          
          <div className="p-6 overflow-y-auto">
            <div className="grid grid-cols-1 md:grid-cols-2 gap-6 mb-6">
              <div>
                <h4 className="font-medium text-gray-900 mb-3">Informations générales</h4>
                <div className="space-y-2 text-sm">
                  <div><strong>Généré par:</strong> {log.generated_by_name}</div>
                  <div><strong>Date:</strong> {new Date(log.generation_date).toLocaleString('fr-FR')}</div>
                  <div><strong>Période:</strong> {format(new Date(log.start_date), 'dd/MM/yyyy')} - {format(new Date(log.end_date), 'dd/MM/yyyy')}</div>
                  <div><strong>Programmes:</strong> {log.programs_list.join(', ')}</div>
                  <div><strong>Temps de traitement:</strong> {log.processing_time?.toFixed(2)}s</div>
                </div>
              </div>
              
              <div>
                <h4 className="font-medium text-gray-900 mb-3">Résultats</h4>
                <div className="space-y-2 text-sm">
                  <div><strong>Séances planifiées:</strong> {log.total_sessions_planned}</div>
                  <div><strong>Conflits résolus:</strong> {log.conflicts_resolved}</div>
                  <div>
                    <strong>Score d'optimisation:</strong>{' '}
                    <span className={getScoreColor(log.optimization_score)}>
                      {log.optimization_score?.toFixed(1)}%
                    </span>
                  </div>
                  <div>
                    <strong>Score d'efficacité:</strong>{' '}
                    <span className={getScoreColor(log.efficiency_score)}>
                      {log.efficiency_score?.toFixed(1)}%
                    </span>
                  </div>
                </div>
              </div>
            </div>

            {log.execution_log && (
              <div>
                <h4 className="font-medium text-gray-900 mb-3">Log d'exécution</h4>
                <pre className="bg-gray-50 p-4 rounded-lg text-xs overflow-x-auto max-h-64">
                  {log.execution_log}
                </pre>
              </div>
            )}
          </div>
        </div>
      </div>
    );
  };

  return (
    <div className="min-h-screen bg-gray-50">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        
        {/* En-tête */}
        <div className="mb-8">
          <h1 className="text-3xl font-bold text-gray-900">Génération Automatique d'Emploi du Temps</h1>
          <p className="text-gray-600 mt-2">
            Utilisez l'intelligence artificielle pour créer des emplois du temps optimisés
          </p>
        </div>

        <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
          
          {/* Configuration */}
          <div className="lg:col-span-2 space-y-6">
            
            {/* Paramètres principaux */}
            <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-6">
              <h2 className="text-lg font-semibold text-gray-900 mb-6">Configuration</h2>
              
              <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                
                {/* Dates */}
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-2">
                    Date de début
                  </label>
                  <input
                    type="date"
                    value={params.start_date}
                    onChange={(e) => setParams(prev => ({ ...prev, start_date: e.target.value }))}
                    className="w-full border border-gray-300 rounded-lg px-3 py-2 focus:outline-none focus:ring-2 focus:ring-primary-500 focus:border-primary-500"
                  />
                </div>

                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-2">
                    Date de fin
                  </label>
                  <input
                    type="date"
                    value={params.end_date}
                    onChange={(e) => setParams(prev => ({ ...prev, end_date: e.target.value }))}
                    className="w-full border border-gray-300 rounded-lg px-3 py-2 focus:outline-none focus:ring-2 focus:ring-primary-500 focus:border-primary-500"
                  />
                </div>
              </div>

              {/* Options avancées */}
              <div className="mt-6">
                <button
                  onClick={() => setShowAdvancedOptions(!showAdvancedOptions)}
                  className="text-sm text-primary-600 hover:text-primary-700 font-medium"
                >
                  {showAdvancedOptions ? 'Masquer' : 'Afficher'} les options avancées
                </button>

                {showAdvancedOptions && (
                  <div className="mt-4 space-y-4 p-4 bg-gray-50 rounded-lg">
                    
                    <div className="flex items-center">
                      <input
                        type="checkbox"
                        id="include_weekends"
                        checked={params.include_weekends}
                        onChange={(e) => setParams(prev => ({ ...prev, include_weekends: e.target.checked }))}
                        className="h-4 w-4 text-primary-600 focus:ring-primary-500 border-gray-300 rounded"
                      />
                      <label htmlFor="include_weekends" className="ml-2 text-sm text-gray-700">
                        Inclure les week-ends
                      </label>
                    </div>

                    <div>
                      <label className="block text-sm font-medium text-gray-700 mb-2">
                        Sessions max par jour
                      </label>
                      <input
                        type="number"
                        min="1"
                        max="12"
                        value={params.max_sessions_per_day}
                        onChange={(e) => setParams(prev => ({ ...prev, max_sessions_per_day: parseInt(e.target.value) }))}
                        className="w-full border border-gray-300 rounded-lg px-3 py-2 focus:outline-none focus:ring-2 focus:ring-primary-500 focus:border-primary-500"
                      />
                    </div>
                  </div>
                )}
              </div>
            </div>

            {/* Sélection des programmes */}
            <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-6">
              <div className="flex items-center justify-between mb-4">
                <h2 className="text-lg font-semibold text-gray-900">
                  Programmes à inclure ({params.program_ids.length} sélectionnés)
                </h2>
                <div className="space-x-2">
                  <button
                    onClick={selectAllPrograms}
                    className="text-sm text-primary-600 hover:text-primary-700"
                  >
                    Tout sélectionner
                  </button>
                  <button
                    onClick={deselectAllPrograms}
                    className="text-sm text-gray-600 hover:text-gray-700"
                  >
                    Tout désélectionner
                  </button>
                </div>
              </div>

              <div className="grid grid-cols-1 md:grid-cols-2 gap-4 max-h-64 overflow-y-auto">
                {programs.map((program) => (
                  <div key={program.id} className="flex items-start">
                    <input
                      type="checkbox"
                      id={`program-${program.id}`}
                      checked={params.program_ids.includes(program.id)}
                      onChange={(e) => handleProgramSelection(program.id, e.target.checked)}
                      className="h-4 w-4 text-primary-600 focus:ring-primary-500 border-gray-300 rounded mt-1"
                    />
                    <label htmlFor={`program-${program.id}`} className="ml-3 text-sm">
                      <div className="font-medium text-gray-900">{program.name}</div>
                      <div className="text-gray-600">
                        {program.level} • {program.department_name}
                      </div>
                      <div className="text-xs text-gray-500">
                        {program.total_students} étudiants • {program.total_subjects} matières
                      </div>
                    </label>
                  </div>
                ))}
              </div>
            </div>

            {/* Bouton de génération */}
            <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-6">
              <div className="text-center">
                <button
                  onClick={handleGenerate}
                  disabled={generating || params.program_ids.length === 0}
                  className={`px-8 py-4 rounded-lg font-medium text-white transition-all duration-200 ${
                    generating || params.program_ids.length === 0
                      ? 'bg-gray-400 cursor-not-allowed'
                      : 'bg-gradient-to-r from-primary-600 to-primary-700 hover:from-primary-700 hover:to-primary-800 hover:shadow-lg transform hover:-translate-y-0.5'
                  }`}
                >
                  {generating ? (
                    <>
                      <RefreshCw className="h-5 w-5 mr-3 animate-spin" />
                      Génération en cours...
                    </>
                  ) : (
                    <>
                      <Zap className="h-5 w-5 mr-3" />
                      Générer l'emploi du temps
                    </>
                  )}
                </button>
                
                {params.program_ids.length === 0 && (
                  <p className="text-sm text-gray-500 mt-2">
                    Veuillez sélectionner au moins un programme
                  </p>
                )}
              </div>
            </div>
          </div>

          {/* Informations et statistiques */}
          <div className="space-y-6">
            
            {/* Avantages OR-Tools */}
            <div className="bg-gradient-to-br from-blue-50 to-indigo-50 rounded-lg p-6 border border-blue-200">
              <div className="text-center mb-4">
                <Target className="h-12 w-12 text-blue-600 mx-auto mb-2" />
                <h3 className="font-medium text-blue-900">Optimisation Intelligente</h3>
              </div>
              <ul className="text-sm text-blue-800 space-y-2">
                <li className="flex items-center">
                  <CheckCircle className="h-4 w-4 mr-2 text-blue-600" />
                  Résolution automatique des conflits
                </li>
                <li className="flex items-center">
                  <CheckCircle className="h-4 w-4 mr-2 text-blue-600" />
                  Optimisation des créneaux horaires
                </li>
                <li className="flex items-center">
                  <CheckCircle className="h-4 w-4 mr-2 text-blue-600" />
                  Respect des contraintes pédagogiques
                </li>
                <li className="flex items-center">
                  <CheckCircle className="h-4 w-4 mr-2 text-blue-600" />
                  Équilibrage de la charge
                </li>
              </ul>
            </div>

            {/* Statistiques rapides */}
            <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-6">
              <h3 className="font-medium text-gray-900 mb-4">Statistiques</h3>
              <div className="space-y-3">
                <div className="flex justify-between">
                  <span className="text-sm text-gray-600">Total générations</span>
                  <span className="text-sm font-medium">{generationLogs.length}</span>
                </div>
                <div className="flex justify-between">
                  <span className="text-sm text-gray-600">Réussies</span>
                  <span className="text-sm font-medium text-green-600">
                    {generationLogs.filter(log => log.status === 'success').length}
                  </span>
                </div>
                <div className="flex justify-between">
                  <span className="text-sm text-gray-600">En cours</span>
                  <span className="text-sm font-medium text-blue-600">
                    {generationLogs.filter(log => log.status === 'pending' || log.status === 'optimizing').length}
                  </span>
                </div>
                <div className="flex justify-between">
                  <span className="text-sm text-gray-600">Score moyen</span>
                  <span className="text-sm font-medium text-primary-600">
                    {generationLogs.length > 0
                      ? (generationLogs.reduce((acc, log) => acc + (log.optimization_score || 0), 0) / generationLogs.length).toFixed(1)
                      : 0
                    }%
                  </span>
                </div>
              </div>
            </div>

            {/* Conseils */}
            <div className="bg-yellow-50 rounded-lg p-6 border border-yellow-200">
              <div className="flex items-start">
                <AlertCircle className="h-6 w-6 text-yellow-600 mt-0.5 mr-3 flex-shrink-0" />
                <div>
                  <h3 className="font-medium text-yellow-900 mb-2">Conseils d'optimisation</h3>
                  <ul className="text-sm text-yellow-800 space-y-1">
                    <li>• Assurez-vous que les données sont complètes</li>
                    <li>• Plus la période est courte, meilleure est l'optimisation</li>
                    <li>• Vérifiez les disponibilités des enseignants</li>
                    <li>• Validez les capacités des salles</li>
                  </ul>
                </div>
              </div>
            </div>
          </div>
        </div>

        {/* Historique des générations */}
        <div className="mt-12">
          <div className="flex items-center justify-between mb-6">
            <h2 className="text-xl font-semibold text-gray-900">Historique des générations</h2>
            <button
              onClick={loadGenerationLogs}
              disabled={loading}
              className="flex items-center px-3 py-2 text-sm text-gray-600 hover:text-gray-800 hover:bg-gray-100 rounded-lg transition-colors duration-200 disabled:opacity-50"
            >
              <RefreshCw className={`h-4 w-4 mr-2 ${loading ? 'animate-spin' : ''}`} />
              Actualiser
            </button>
          </div>

          <div className="bg-white rounded-lg shadow-sm border border-gray-200 overflow-hidden">
            {generationLogs.length === 0 ? (
              <div className="p-8 text-center text-gray-500">
                <Settings className="h-12 w-12 mx-auto mb-4 opacity-50" />
                <p>Aucune génération effectuée</p>
              </div>
            ) : (
              <div className="overflow-x-auto">
                <table className="min-w-full divide-y divide-gray-200">
                  <thead className="bg-gray-50">
                    <tr>
                      <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                        Date
                      </th>
                      <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                        Période
                      </th>
                      <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                        Programmes
                      </th>
                      <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                        Statut
                      </th>
                      <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                        Résultats
                      </th>
                      <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                        Performance
                      </th>
                      <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                        Actions
                      </th>
                    </tr>
                  </thead>
                  <tbody className="bg-white divide-y divide-gray-200">
                    {generationLogs.map((log) => (
                      <tr key={log.id} className="hover:bg-gray-50">
                        <td className="px-6 py-4 whitespace-nowrap">
                          <div className="text-sm text-gray-900">
                            {format(new Date(log.generation_date), 'dd/MM/yyyy HH:mm')}
                          </div>
                          <div className="text-xs text-gray-500">
                            Par {log.generated_by_name}
                          </div>
                        </td>
                        <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                          {format(new Date(log.start_date), 'dd/MM/yy')} -{' '}
                          {format(new Date(log.end_date), 'dd/MM/yy')}
                        </td>
                        <td className="px-6 py-4 whitespace-nowrap">
                          <div className="text-sm text-gray-900">
                            {log.programs_list.length} programme{log.programs_list.length > 1 ? 's' : ''}
                          </div>
                          <div className="text-xs text-gray-500 truncate max-w-32">
                            {log.programs_list.join(', ')}
                          </div>
                        </td>
                        <td className="px-6 py-4 whitespace-nowrap">
                          <span className={`inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium ${getStatusColor(log.status)}`}>
                            {getStatusIcon(log.status)}
                            <span className="ml-1">{log.status_display}</span>
                          </span>
                        </td>
                        <td className="px-6 py-4 whitespace-nowrap text-sm">
                          <div className="text-gray-900">
                            <strong>{log.total_sessions_planned}</strong> séances
                          </div>
                          <div className="text-gray-500">
                            {log.conflicts_resolved} conflits résolus
                          </div>
                        </td>
                        <td className="px-6 py-4 whitespace-nowrap text-sm">
                          <div className={`font-medium ${getScoreColor(log.optimization_score)}`}>
                            Opt: {log.optimization_score?.toFixed(1)}%
                          </div>
                          <div className={`text-xs ${getScoreColor(log.efficiency_score)}`}>
                            Eff: {log.efficiency_score?.toFixed(1)}%
                          </div>
                        </td>
                        <td className="px-6 py-4 whitespace-nowrap text-sm">
                          <button
                            onClick={() => setSelectedLog(log)}
                            className="text-primary-600 hover:text-primary-900"
                          >
                            <Eye className="h-4 w-4" />
                          </button>
                        </td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
            )}
          </div>
        </div>

        {/* Modal détails */}
        <LogDetailsModal 
          log={selectedLog}
          onClose={() => setSelectedLog(null)}
        />

      </div>
    </div>
  );
};

export default AdminTimetableGeneration;
