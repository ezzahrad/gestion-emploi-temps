// AdminDashboard.tsx - Tableau de bord administrateur optimisé pour desktop
import React, { useState, useEffect } from 'react';
import { useAuth, useAuthenticatedFetch } from '../contexts/AuthContext';
import { 
  Users, BookOpen, MapPin, Calendar, TrendingUp, AlertTriangle,
  Settings, Upload, Download, BarChart3, Clock, Target,
  Plus, Edit, Eye, RefreshCw, Filter, Search, Grid,
  CheckCircle, XCircle, Activity, Zap, Database
} from 'lucide-react';
import { toast } from 'react-hot-toast';
import { Link } from 'react-router-dom';

interface AdminStats {
  total_departments: number;
  total_programs: number;
  total_teachers: number;
  total_students: number;
  total_rooms: number;
  total_subjects: number;
  total_schedules: number;
  active_schedules_this_week: number;
  room_utilization_rate: number;
  teacher_workload_average: number;
  pending_registrations: number;
  system_alerts: number;
  recent_activities: ActivityItem[];
  quick_stats: QuickStat[];
}

interface ActivityItem {
  id: number;
  action: string;
  user: string;
  timestamp: string;
  details: string;
  type: 'create' | 'update' | 'delete' | 'import' | 'export';
}

interface QuickStat {
  label: string;
  value: number;
  change: number;
  trend: 'up' | 'down' | 'stable';
  color: string;
}

interface QuickAction {
  title: string;
  description: string;
  icon: React.ReactNode;
  link: string;
  color: string;
  priority: 'high' | 'medium' | 'low';
  badge?: string;
}

const AdminDashboard: React.FC = () => {
  const { user } = useAuth();
  const authenticatedFetch = useAuthenticatedFetch();
  
  const [stats, setStats] = useState<AdminStats | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [selectedTimeRange, setSelectedTimeRange] = useState('week');
  const [refreshing, setRefreshing] = useState(false);

  const loadDashboardData = async () => {
    try {
      setLoading(true);
      setError(null);

      const response = await authenticatedFetch(`/api/core/dashboard/admin/?period=${selectedTimeRange}`);
      
      if (response.ok) {
        const data = await response.json();
        setStats(data);
      } else {
        throw new Error('Erreur lors du chargement des données administrateur');
      }
    } catch (error) {
      console.error('Erreur dashboard admin:', error);
      setError('Impossible de charger le tableau de bord administrateur');
      toast.error('Erreur de chargement des données');
    } finally {
      setLoading(false);
    }
  };

  const refreshData = async () => {
    setRefreshing(true);
    await loadDashboardData();
    setRefreshing(false);
    toast.success('Données actualisées');
  };

  useEffect(() => {
    loadDashboardData();
  }, [selectedTimeRange]);

  const getQuickActions = (): QuickAction[] => [
    {
      title: 'Générer Emploi du Temps',
      description: 'Créer automatiquement les plannings',
      icon: <Target className="h-6 w-6" />,
      link: '/admin/generate-timetable',
      color: 'from-red-500 to-red-600',
      priority: 'high',
      badge: 'Nouveau'
    },
    {
      title: 'Importer Données Excel',
      description: 'Charger des données depuis Excel',
      icon: <Upload className="h-6 w-6" />,
      link: '/admin/import-excel',
      color: 'from-green-500 to-emerald-600',
      priority: 'high'
    },
    {
      title: 'Gestion Utilisateurs',
      description: 'Gérer enseignants et étudiants',
      icon: <Users className="h-6 w-6" />,
      link: '/admin/users',
      color: 'from-blue-500 to-blue-600',
      priority: 'medium',
      badge: stats?.pending_registrations ? `${stats.pending_registrations}` : undefined
    },
    {
      title: 'Configuration Système',
      description: 'Paramètres et configuration',
      icon: <Settings className="h-6 w-6" />,
      link: '/admin/settings',
      color: 'from-gray-500 to-gray-600',
      priority: 'medium'
    },
    {
      title: 'Rapports & Analytics',
      description: 'Statistiques détaillées',
      icon: <BarChart3 className="h-6 w-6" />,
      link: '/admin/reports',
      color: 'from-purple-500 to-purple-600',
      priority: 'medium'
    },
    {
      title: 'Gestion des Salles',
      description: 'Configurer les espaces',
      icon: <MapPin className="h-6 w-6" />,
      link: '/admin/rooms',
      color: 'from-orange-500 to-orange-600',
      priority: 'low'
    },
    {
      title: 'Base de Données',
      description: 'Maintenance et backup',
      icon: <Database className="h-6 w-6" />,
      link: '/admin/database',
      color: 'from-indigo-500 to-indigo-600',
      priority: 'low'
    },
    {
      title: 'Optimisation IA',
      description: 'Améliorer les plannings',
      icon: <Zap className="h-6 w-6" />,
      link: '/admin/ai-optimization',
      color: 'from-yellow-500 to-yellow-600',
      priority: 'medium',
      badge: 'Beta'
    }
  ];

  const renderStatCard = (title: string, value: number | string, icon: React.ReactNode, color: string, trend?: { value: number; direction: 'up' | 'down' | 'stable' }) => (
    <div className="bg-white rounded-xl shadow-sm border border-gray-200 p-6 hover:shadow-md transition-all duration-200">
      <div className="flex items-center justify-between">
        <div className="flex items-center">
          <div className={`flex-shrink-0 bg-gradient-to-br ${color} p-3 rounded-lg shadow-sm`}>
            <div className="text-white">
              {icon}
            </div>
          </div>
          <div className="ml-4">
            <p className="text-sm font-medium text-gray-500">{title}</p>
            <p className="text-2xl font-bold text-gray-900">{value}</p>
          </div>
        </div>
        {trend && trend.value !== 0 && (
          <div className={`flex items-center px-2 py-1 rounded-full text-xs font-medium ${
            trend.direction === 'up' ? 'text-green-600 bg-green-100' :
            trend.direction === 'down' ? 'text-red-600 bg-red-100' :
            'text-gray-600 bg-gray-100'
          }`}>
            {trend.direction === 'up' ? '↗' : trend.direction === 'down' ? '↘' : '→'}
            <span className="ml-1">{Math.abs(trend.value)}%</span>
          </div>
        )}
      </div>
    </div>
  );

  const renderQuickActions = () => {
    const sortedActions = getQuickActions().sort((a, b) => {
      const priorityOrder = { high: 0, medium: 1, low: 2 };
      return priorityOrder[a.priority] - priorityOrder[b.priority];
    });

    return (
      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4 gap-4">
        {sortedActions.map((action, index) => (
          <Link
            key={index}
            to={action.link}
            className={`relative bg-gradient-to-r ${action.color} text-white p-6 rounded-xl shadow-sm hover:shadow-lg transition-all duration-300 transform hover:-translate-y-1 hover:scale-105 group`}
          >
            {action.badge && (
              <span className="absolute -top-2 -right-2 bg-yellow-400 text-yellow-900 text-xs font-bold px-2 py-1 rounded-full">
                {action.badge}
              </span>
            )}
            <div className="flex items-start justify-between">
              <div className="flex-1">
                <div className="flex items-center mb-2">
                  {action.icon}
                  <div className={`ml-2 w-2 h-2 rounded-full ${
                    action.priority === 'high' ? 'bg-red-300' :
                    action.priority === 'medium' ? 'bg-yellow-300' :
                    'bg-green-300'
                  }`} />
                </div>
                <h3 className="font-semibold text-lg leading-tight">{action.title}</h3>
                <p className="text-sm opacity-90 mt-1">{action.description}</p>
              </div>
            </div>
            <div className="mt-4 opacity-0 group-hover:opacity-100 transition-opacity">
              <div className="text-xs font-medium">Cliquer pour accéder →</div>
            </div>
          </Link>
        ))}
      </div>
    );
  };

  const renderActivityFeed = () => {
    if (!stats?.recent_activities?.length) {
      return (
        <div className="text-center py-8 text-gray-500">
          <Activity className="h-12 w-12 mx-auto mb-4 opacity-50" />
          <p>Aucune activité récente</p>
        </div>
      );
    }

    const getActivityIcon = (type: string) => {
      switch (type) {
        case 'create': return <Plus className="h-4 w-4 text-green-600" />;
        case 'update': return <Edit className="h-4 w-4 text-blue-600" />;
        case 'delete': return <XCircle className="h-4 w-4 text-red-600" />;
        case 'import': return <Upload className="h-4 w-4 text-purple-600" />;
        case 'export': return <Download className="h-4 w-4 text-orange-600" />;
        default: return <Activity className="h-4 w-4 text-gray-600" />;
      }
    };

    return (
      <div className="space-y-4">
        {stats.recent_activities.slice(0, 8).map((activity) => (
          <div key={activity.id} className="flex items-start space-x-3 p-3 hover:bg-gray-50 rounded-lg transition-colors">
            <div className="flex-shrink-0 mt-1">
              {getActivityIcon(activity.type)}
            </div>
            <div className="flex-1 min-w-0">
              <div className="flex items-center justify-between">
                <p className="text-sm font-medium text-gray-900">
                  {activity.action}
                </p>
                <span className="text-xs text-gray-500">
                  {new Date(activity.timestamp).toLocaleDateString('fr-FR', {
                    day: 'numeric',
                    month: 'short',
                    hour: '2-digit',
                    minute: '2-digit'
                  })}
                </span>
              </div>
              <p className="text-sm text-gray-600">{activity.details}</p>
              <p className="text-xs text-gray-500 mt-1">Par {activity.user}</p>
            </div>
          </div>
        ))}
      </div>
    );
  };

  const renderSystemAlerts = () => {
    const mockAlerts = [
      {
        id: 1,
        type: 'warning',
        title: 'Salle A101 - Capacité dépassée',
        message: 'La salle A101 a 35 étudiants inscrits pour une capacité de 30.',
        timestamp: '2024-01-15T10:30:00Z'
      },
      {
        id: 2,
        type: 'info',
        title: 'Nouvelles inscriptions',
        message: '5 nouveaux étudiants en attente de validation.',
        timestamp: '2024-01-15T09:15:00Z'
      },
      {
        id: 3,
        type: 'error',
        title: 'Conflit d\'emploi du temps',
        message: 'Prof. Martin a 2 cours simultanés le mercredi 14h.',
        timestamp: '2024-01-15T08:45:00Z'
      }
    ];

    return (
      <div className="space-y-3">
        {mockAlerts.map((alert) => (
          <div key={alert.id} className={`p-4 rounded-lg border-l-4 ${
            alert.type === 'error' ? 'border-red-500 bg-red-50' :
            alert.type === 'warning' ? 'border-yellow-500 bg-yellow-50' :
            'border-blue-500 bg-blue-50'
          }`}>
            <div className="flex items-start justify-between">
              <div className="flex-1">
                <div className="flex items-center">
                  {alert.type === 'error' ? <XCircle className="h-4 w-4 text-red-600 mr-2" /> :
                   alert.type === 'warning' ? <AlertTriangle className="h-4 w-4 text-yellow-600 mr-2" /> :
                   <CheckCircle className="h-4 w-4 text-blue-600 mr-2" />}
                  <h4 className="text-sm font-medium text-gray-900">{alert.title}</h4>
                </div>
                <p className="text-sm text-gray-600 mt-1">{alert.message}</p>
              </div>
              <span className="text-xs text-gray-500">
                {new Date(alert.timestamp).toLocaleTimeString('fr-FR', {
                  hour: '2-digit',
                  minute: '2-digit'
                })}
              </span>
            </div>
          </div>
        ))}
      </div>
    );
  };

  if (loading) {
    return (
      <div className="min-h-screen bg-gray-50 flex items-center justify-center">
        <div className="text-center">
          <div className="animate-spin rounded-full h-16 w-16 border-b-2 border-primary-600 mx-auto"></div>
          <p className="mt-4 text-gray-600 text-lg">Chargement du tableau de bord administrateur...</p>
        </div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="min-h-screen bg-gray-50 flex items-center justify-center">
        <div className="text-center max-w-md">
          <AlertTriangle className="h-16 w-16 text-red-500 mx-auto mb-4" />
          <h2 className="text-xl font-semibold text-gray-900 mb-2">Erreur de chargement</h2>
          <p className="text-gray-600 mb-6">{error}</p>
          <button
            onClick={loadDashboardData}
            className="btn-primary"
          >
            <RefreshCw className="h-4 w-4 mr-2" />
            Réessayer
          </button>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gray-50">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        
        {/* En-tête */}
        <div className="mb-8">
          <div className="flex flex-col lg:flex-row lg:items-center lg:justify-between">
            <div className="mb-4 lg:mb-0">
              <h1 className="text-4xl font-bold text-gray-900">
                Tableau de Bord Administrateur
              </h1>
              <p className="text-lg text-gray-600 mt-2">
                Bienvenue, {user?.first_name} {user?.last_name}
              </p>
              <div className="flex items-center mt-3 space-x-4">
                <span className="inline-flex items-center px-3 py-1 rounded-full text-sm font-medium bg-red-100 text-red-800">
                  Administrateur
                </span>
                <span className="text-sm text-gray-500">
                  Dernière connexion: {new Date().toLocaleString('fr-FR')}
                </span>
              </div>
            </div>
            
            <div className="flex items-center space-x-4">
              {/* Sélecteur de période */}
              <select
                value={selectedTimeRange}
                onChange={(e) => setSelectedTimeRange(e.target.value)}
                className="border border-gray-300 rounded-lg px-3 py-2 text-sm focus:ring-2 focus:ring-primary-500 focus:border-primary-500"
              >
                <option value="day">Aujourd'hui</option>
                <option value="week">Cette semaine</option>
                <option value="month">Ce mois</option>
                <option value="year">Cette année</option>
              </select>
              
              {/* Bouton actualiser */}
              <button
                onClick={refreshData}
                disabled={refreshing}
                className="btn-secondary"
                title="Actualiser les données"
              >
                <RefreshCw className={`h-4 w-4 mr-2 ${refreshing ? 'animate-spin' : ''}`} />
                Actualiser
              </button>
            </div>
          </div>
        </div>

        {/* Statistiques principales */}
        {stats && (
          <div className="mb-8 grid grid-cols-2 md:grid-cols-4 lg:grid-cols-6 xl:grid-cols-8 gap-4">
            {renderStatCard(
              "Départements", 
              stats.total_departments, 
              <Grid className="h-6 w-6" />, 
              "from-blue-500 to-blue-600",
              { value: 0, direction: 'stable' }
            )}
            {renderStatCard(
              "Programmes", 
              stats.total_programs, 
              <BookOpen className="h-6 w-6" />, 
              "from-purple-500 to-purple-600",
              { value: 2, direction: 'up' }
            )}
            {renderStatCard(
              "Enseignants", 
              stats.total_teachers, 
              <Users className="h-6 w-6" />, 
              "from-green-500 to-emerald-600",
              { value: 3, direction: 'up' }
            )}
            {renderStatCard(
              "Étudiants", 
              stats.total_students, 
              <Users className="h-6 w-6" />, 
              "from-indigo-500 to-indigo-600",
              { value: 8, direction: 'up' }
            )}
            {renderStatCard(
              "Salles", 
              stats.total_rooms, 
              <MapPin className="h-6 w-6" />, 
              "from-orange-500 to-orange-600",
              { value: 0, direction: 'stable' }
            )}
            {renderStatCard(
              "Cours actifs", 
              stats.active_schedules_this_week, 
              <Calendar className="h-6 w-6" />, 
              "from-teal-500 to-teal-600",
              { value: 5, direction: 'up' }
            )}
            {renderStatCard(
              "Taux occupation", 
              `${stats.room_utilization_rate?.toFixed(1) || 0}%`, 
              <TrendingUp className="h-6 w-6" />, 
              "from-cyan-500 to-cyan-600",
              { value: 3.2, direction: 'up' }
            )}
            {renderStatCard(
              "Charge moyenne", 
              `${stats.teacher_workload_average?.toFixed(1) || 0}h`, 
              <Clock className="h-6 w-6" />, 
              "from-rose-500 to-rose-600",
              { value: 1.8, direction: 'down' }
            )}
          </div>
        )}

        {/* Actions rapides */}
        <div className="mb-8">
          <div className="flex items-center justify-between mb-6">
            <h2 className="text-2xl font-semibold text-gray-900">Actions rapides</h2>
            <div className="flex items-center space-x-2">
              <span className="text-sm text-gray-500">Triées par priorité</span>
              <div className="flex space-x-1">
                <div className="w-2 h-2 bg-red-400 rounded-full" title="Haute priorité"></div>
                <div className="w-2 h-2 bg-yellow-400 rounded-full" title="Moyenne priorité"></div>
                <div className="w-2 h-2 bg-green-400 rounded-full" title="Basse priorité"></div>
              </div>
            </div>
          </div>
          
          <div className="bg-white rounded-xl shadow-sm border border-gray-200 p-6">
            {renderQuickActions()}
          </div>
        </div>

        <div className="grid grid-cols-1 xl:grid-cols-3 gap-8">
          
          {/* Activité récente */}
          <div className="xl:col-span-2">
            <div className="bg-white rounded-xl shadow-sm border border-gray-200">
              <div className="p-6 border-b border-gray-200">
                <div className="flex items-center justify-between">
                  <h2 className="text-xl font-semibold text-gray-900">Activité récente</h2>
                  <Link 
                    to="/admin/activity-log" 
                    className="text-sm text-primary-600 hover:text-primary-700 font-medium"
                  >
                    Voir tout →
                  </Link>
                </div>
              </div>
              <div className="p-6">
                {renderActivityFeed()}
              </div>
            </div>
          </div>

          {/* Alertes système */}
          <div>
            <div className="bg-white rounded-xl shadow-sm border border-gray-200">
              <div className="p-6 border-b border-gray-200">
                <div className="flex items-center justify-between">
                  <h2 className="text-xl font-semibold text-gray-900">
                    Alertes système
                    {stats?.system_alerts && stats.system_alerts > 0 && (
                      <span className="ml-2 inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium bg-red-100 text-red-800">
                        {stats.system_alerts}
                      </span>
                    )}
                  </h2>
                  <button className="text-sm text-gray-500 hover:text-gray-700">
                    <Settings className="h-4 w-4" />
                  </button>
                </div>
              </div>
              <div className="p-6">
                {renderSystemAlerts()}
              </div>
            </div>
          </div>

        </div>

      </div>
    </div>
  );
};

export default AdminDashboard;