// Dashboard.tsx - Tableau de bord optimisé pour desktop
import React, { useState, useEffect } from 'react';
import { useAuth, useAuthenticatedFetch, roleDisplayNames } from '../contexts/AuthContext';
import { 
  Calendar, Users, BookOpen, MapPin, Clock, TrendingUp,
  AlertCircle, Upload, Download, Settings,
  BarChart3, Activity, ArrowUp, ArrowDown, Minus} from 'lucide-react';
import { toast } from 'react-hot-toast';
import { Link } from 'react-router-dom';

// Types
interface DashboardStats {
  total_departments?: number;
  total_programs?: number;
  total_teachers?: number;
  total_students?: number;
  total_rooms?: number;
  total_subjects?: number;
  total_schedules?: number;
  active_schedules_this_week?: number;
  room_utilization_rate?: number;
  teacher_workload_average?: number;
  weekly_sessions?: number;
  weekly_hours?: number;
  total_subjects_taught?: number;
  workload_percentage?: number;
  program?: string;
  upcoming_sessions?: any[];
}

interface QuickAction {
  title: string;
  description: string;
  icon: React.ReactNode;
  link: string;
  color: string;
  permission?: string;
}

const Dashboard: React.FC = () => {
  const { user, hasPermission, hasRole } = useAuth();
  const authenticatedFetch = useAuthenticatedFetch();
  const [stats, setStats] = useState<DashboardStats>({});
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    // Rediriger vers le tableau de bord spécifique au rôle
    if (user) {
      if (user.role === 'admin') {
        window.location.href = '/admin/dashboard';
        return;
      } else if (user.role === 'teacher') {
        window.location.href = '/teacher/dashboard';
        return;
      } else if (user.role === 'student') {
        window.location.href = '/student/dashboard';
        return;
      }
    }
    
    loadDashboardData();
  }, [user]);

  const loadDashboardData = async () => {
    try {
      setLoading(true);
      setError(null);

      const response = await authenticatedFetch('/api/dashboard/');
      
      if (response.ok) {
        const data = await response.json();
        setStats(data);
      } else {
        throw new Error('Erreur lors du chargement des données');
      }
    } catch (error) {
      console.error('Erreur dashboard:', error);
      setError('Impossible de charger les données du tableau de bord');
      toast.error('Erreur de chargement des données');
    } finally {
      setLoading(false);
    }
  };

  const getQuickActions = (): QuickAction[] => {
    const baseActions: QuickAction[] = [];

    baseActions.push({
      title: 'Mon Emploi du Temps',
      description: 'Voir mes cours et horaires',
      icon: <Calendar className="h-6 w-6" />,
      link: '/schedule/personal',
      color: 'bg-gradient-to-r from-blue-500 to-blue-600 hover:from-blue-600 hover:to-blue-700'
    });

    baseActions.push({
      title: 'Exporter PDF',
      description: 'Télécharger mon planning',
      icon: <Download className="h-6 w-6" />,
      link: '/export/schedule?format=pdf',
      color: 'bg-gradient-to-r from-green-500 to-emerald-600 hover:from-green-600 hover:to-emerald-700'
    });

    if (hasRole('admin')) {
      baseActions.push(
        {
          title: 'Importer Excel',
          description: 'Charger des données depuis Excel',
          icon: <Upload className="h-6 w-6" />,
          link: '/admin/import-excel',
          color: 'bg-gradient-to-r from-purple-500 to-purple-600 hover:from-purple-600 hover:to-purple-700',
          permission: 'import_excel'
        },
        {
          title: 'Générer Emploi du Temps',
          description: 'Créer automatiquement les planning',
          icon: <Settings className="h-6 w-6" />,
          link: '/admin/generate-timetable',
          color: 'bg-gradient-to-r from-red-500 to-red-600 hover:from-red-600 hover:to-red-700',
          permission: 'generate_timetable'
        },
        {
          title: 'Statistiques Avancées',
          description: 'Rapports et analyses',
          icon: <BarChart3 className="h-6 w-6" />,
          link: '/admin/statistics',
          color: 'bg-gradient-to-r from-indigo-500 to-indigo-600 hover:from-indigo-600 hover:to-indigo-700',
          permission: 'view_statistics'
        },
        {
          title: 'Gestion Utilisateurs',
          description: 'Gérer les comptes',
          icon: <Users className="h-6 w-6" />,
          link: '/admin/users',
          color: 'bg-gradient-to-r from-orange-500 to-orange-600 hover:from-orange-600 hover:to-orange-700',
          permission: 'manage_users'
        }
      );
    }

    if (hasRole(['admin', 'department_head', 'program_head'])) {
      baseActions.push({
        title: 'Gérer les Cours',
        description: 'Modifier les emplois du temps',
        icon: <BookOpen className="h-6 w-6" />,
        link: '/admin/schedules',
        color: 'bg-gradient-to-r from-teal-500 to-teal-600 hover:from-teal-600 hover:to-teal-700',
        permission: 'manage_schedules'
      });
    }

    if (hasRole('teacher')) {
      baseActions.push(
        {
          title: 'Mes Étudiants',
          description: 'Voir la liste de mes étudiants',
          icon: <Users className="h-6 w-6" />,
          link: '/teacher/students',
          color: 'bg-gradient-to-r from-purple-500 to-purple-600 hover:from-purple-600 hover:to-purple-700'
        },
        {
          title: 'Disponibilités',
          description: 'Gérer mes créneaux',
          icon: <Clock className="h-6 w-6" />,
          link: '/teacher/availability',
          color: 'bg-gradient-to-r from-orange-500 to-orange-600 hover:from-orange-600 hover:to-orange-700'
        }
      );
    }

    return baseActions.filter(action => 
      !action.permission || hasPermission(action.permission)
    );
  };

  const renderAdminStats = () => (
    <div className="grid grid-cols-2 md:grid-cols-3 lg:grid-cols-4 xl:grid-cols-6 2xl:grid-cols-8 gap-6 mb-8">
      <StatCard
        title="Départements"
        value={stats.total_departments || 0}
        icon={<MapPin className="h-6 w-6" />}
        color="from-blue-500 to-blue-600"
        trend={{ value: 0, direction: 'neutral' }}
      />
      <StatCard
        title="Enseignants"
        value={stats.total_teachers || 0}
        icon={<Users className="h-6 w-6" />}
        color="from-green-500 to-emerald-600"
        trend={{ value: 2, direction: 'up' }}
      />
      <StatCard
        title="Étudiants"
        value={stats.total_students || 0}
        icon={<Users className="h-6 w-6" />}
        color="from-purple-500 to-purple-600"
        trend={{ value: 5, direction: 'up' }}
      />
      <StatCard
        title="Salles"
        value={stats.total_rooms || 0}
        icon={<MapPin className="h-6 w-6" />}
        color="from-orange-500 to-orange-600"
        trend={{ value: 0, direction: 'neutral' }}
      />
      <StatCard
        title="Cours cette semaine"
        value={stats.active_schedules_this_week || 0}
        icon={<Calendar className="h-6 w-6" />}
        color="from-indigo-500 to-indigo-600"
        trend={{ value: 3, direction: 'up' }}
      />
      <StatCard
        title="Taux utilisation"
        value={`${stats.room_utilization_rate?.toFixed(1) || 0}%`}
        icon={<TrendingUp className="h-6 w-6" />}
        color="from-teal-500 to-teal-600"
        trend={{ value: 2.5, direction: 'up' }}
      />
      <StatCard
        title="Charge moyenne"
        value={`${stats.teacher_workload_average?.toFixed(1) || 0}h`}
        icon={<Activity className="h-6 w-6" />}
        color="from-red-500 to-red-600"
        trend={{ value: 1.2, direction: 'down' }}
      />
      <StatCard
        title="Total emplois"
        value={stats.total_schedules || 0}
        icon={<BookOpen className="h-6 w-6" />}
        color="from-yellow-500 to-yellow-600"
        trend={{ value: 8, direction: 'up' }}
      />
    </div>
  );

  const renderTeacherStats = () => (
    <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6 mb-8">
      <StatCard
        title="Cours cette semaine"
        value={stats.weekly_sessions || 0}
        icon={<Calendar className="h-6 w-6" />}
        color="from-blue-500 to-blue-600"
        trend={{ value: 2, direction: 'up' }}
      />
      <StatCard
        title="Heures cette semaine"
        value={`${stats.weekly_hours || 0}h`}
        icon={<Clock className="h-6 w-6" />}
        color="from-green-500 to-emerald-600"
        trend={{ value: 3, direction: 'up' }}
      />
      <StatCard
        title="Matières enseignées"
        value={stats.total_subjects_taught || 0}
        icon={<BookOpen className="h-6 w-6" />}
        color="from-purple-500 to-purple-600"
        trend={{ value: 0, direction: 'neutral' }}
      />
      <StatCard
        title="Charge de travail"
        value={`${stats.workload_percentage?.toFixed(1) || 0}%`}
        icon={<Activity className="h-6 w-6" />}
        color={
          (stats.workload_percentage || 0) > 80 
            ? "from-red-500 to-red-600" 
            : (stats.workload_percentage || 0) > 60 
              ? "from-orange-500 to-orange-600" 
              : "from-green-500 to-emerald-600"
        }
        trend={{ value: 5.2, direction: 'up' }}
      />
    </div>
  );

  const renderStudentStats = () => (
    <div className="grid grid-cols-1 md:grid-cols-3 gap-6 mb-8">
      <div className="bg-white rounded-xl shadow-sm border border-gray-200 p-6 hover:shadow-md transition-shadow">
        <div className="flex items-center">
          <div className="flex-shrink-0">
            <div className="h-12 w-12 bg-gradient-to-br from-blue-500 to-blue-600 rounded-lg flex items-center justify-center">
              <BookOpen className="h-6 w-6 text-white" />
            </div>
          </div>
          <div className="ml-4">
            <p className="text-sm font-medium text-gray-500">Mon Programme</p>
            <p className="text-xl font-bold text-gray-900">{stats.program || 'N/A'}</p>
          </div>
        </div>
      </div>
      <StatCard
        title="Cours cette semaine"
        value={stats.weekly_sessions || 0}
        icon={<Calendar className="h-6 w-6" />}
        color="from-green-500 to-emerald-600"
        trend={{ value: 0, direction: 'neutral' }}
      />
      <StatCard
        title="Heures cette semaine"
        value={`${stats.weekly_hours || 0}h`}
        icon={<Clock className="h-6 w-6" />}
        color="from-purple-500 to-purple-600"
        trend={{ value: 2, direction: 'up' }}
      />
    </div>
  );

  const renderUpcomingSessions = () => {
    if (!stats.upcoming_sessions || stats.upcoming_sessions.length === 0) {
      return (
        <div className="text-center py-12 text-gray-500">
          <Calendar className="h-16 w-16 mx-auto mb-4 opacity-50" />
          <p className="text-lg font-medium">Aucun cours à venir</p>
          <p className="text-sm mt-1">Votre planning est libre pour le moment</p>
        </div>
      );
    }

    return (
      <div className="space-y-3">
        {stats.upcoming_sessions.slice(0, 6).map((session, index) => (
          <div key={index} className="flex items-center p-4 bg-gray-50 hover:bg-gray-100 rounded-xl border border-gray-100 transition-colors">
            <div className="flex-shrink-0">
              <div className="h-10 w-10 bg-blue-100 rounded-lg flex items-center justify-center">
                <Calendar className="h-5 w-5 text-blue-600" />
              </div>
            </div>
            <div className="ml-4 flex-1 min-w-0">
              <p className="text-sm font-semibold text-gray-900 truncate">
                {session.subject_name || session.title}
              </p>
              <p className="text-sm text-gray-600">
                {session.time_slot_info?.day_display} - {session.time_slot_info?.start_time} à {session.time_slot_info?.end_time}
              </p>
              <p className="text-xs text-gray-500">
                {session.room_name} {session.teacher_name && `• ${session.teacher_name}`}
              </p>
            </div>
            <div className="flex-shrink-0">
              <span className="inline-flex items-center px-3 py-1 rounded-full text-xs font-medium bg-blue-100 text-blue-800">
                {session.start_date}
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
          <p className="mt-4 text-gray-600 text-lg">Chargement du tableau de bord...</p>
        </div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="min-h-screen bg-gray-50 flex items-center justify-center">
        <div className="text-center max-w-md">
          <AlertCircle className="h-16 w-16 text-red-500 mx-auto mb-4" />
          <h2 className="text-xl font-semibold text-gray-900 mb-2">Erreur de chargement</h2>
          <p className="text-gray-600 mb-6">{error}</p>
          <button
            onClick={loadDashboardData}
            className="px-6 py-3 bg-primary-600 text-white rounded-lg hover:bg-primary-700 transition-colors font-medium"
          >
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
                Tableau de bord
              </h1>
              <p className="text-lg text-gray-600 mt-2">
                Bienvenue, {user?.first_name} {user?.last_name}
              </p>
              <span className={`inline-flex items-center px-3 py-1 rounded-full text-sm font-medium mt-3 ${
                user?.role === 'admin' ? 'bg-red-100 text-red-800' :
                user?.role === 'teacher' ? 'bg-purple-100 text-purple-800' :
                user?.role === 'student' ? 'bg-blue-100 text-blue-800' :
                'bg-gray-100 text-gray-800'
              }`}>
                {roleDisplayNames[user?.role || '']}
              </span>
            </div>
            <div className="text-right">
              <p className="text-sm text-gray-500">Dernière mise à jour</p>
              <p className="text-lg font-semibold text-gray-900">
                {new Date().toLocaleString('fr-FR', {
                  weekday: 'long',
                  year: 'numeric',
                  month: 'long',
                  day: 'numeric',
                  hour: '2-digit',
                  minute: '2-digit'
                })}
              </p>
            </div>
          </div>
        </div>

        {/* Statistiques selon le rôle */}
        {hasRole('admin') && renderAdminStats()}
        {hasRole('teacher') && renderTeacherStats()}
        {hasRole('student') && renderStudentStats()}

        <div className="grid grid-cols-1 xl:grid-cols-3 gap-8">
          
          {/* Actions rapides */}
          <div className="xl:col-span-2">
            <div className="bg-white rounded-xl shadow-sm border border-gray-200 p-6">
              <h2 className="text-xl font-semibold text-gray-900 mb-6">Actions rapides</h2>
              <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-4">
                {getQuickActions().map((action, index) => (
                  <Link
                    key={index}
                    to={action.link}
                    className={`${action.color} text-white p-6 rounded-xl shadow-sm hover:shadow-lg transition-all duration-300 transform hover:-translate-y-1 hover:scale-105`}
                  >
                    <div className="flex items-center">
                      <div className="flex-shrink-0">
                        {action.icon}
                      </div>
                      <div className="ml-4">
                        <p className="font-semibold">{action.title}</p>
                        <p className="text-sm opacity-90">{action.description}</p>
                      </div>
                    </div>
                  </Link>
                ))}
              </div>
            </div>
          </div>

          {/* Prochains cours */}
          <div className="bg-white rounded-xl shadow-sm border border-gray-200 p-6">
            <div className="flex items-center justify-between mb-6">
              <h2 className="text-xl font-semibold text-gray-900">Prochains cours</h2>
              <Link 
                to="/schedule/personal" 
                className="text-sm text-primary-600 hover:text-primary-700 font-medium transition-colors"
              >
                Voir tout →
              </Link>
            </div>
            {renderUpcomingSessions()}
          </div>

        </div>

      </div>
    </div>
  );
};

// Composant StatCard amélioré
interface StatCardProps {
  title: string;
  value: string | number;
  icon: React.ReactNode;
  color: string;
  trend: { value: number; direction: 'up' | 'down' | 'neutral' };
}

const StatCard: React.FC<StatCardProps> = ({ title, value, icon, color, trend }) => {
  const getTrendIcon = () => {
    if (trend.direction === 'up') return <ArrowUp className="h-3 w-3" />;
    if (trend.direction === 'down') return <ArrowDown className="h-3 w-3" />;
    return <Minus className="h-3 w-3" />;
  };

  const getTrendColor = () => {
    if (trend.direction === 'up') return 'text-green-600 bg-green-100';
    if (trend.direction === 'down') return 'text-red-600 bg-red-100';
    return 'text-gray-600 bg-gray-100';
  };

  return (
    <div className="bg-white rounded-xl shadow-sm border border-gray-200 p-6 hover:shadow-md transition-shadow">
      <div className="flex items-center justify-between">
        <div className="flex items-center">
          <div className={`flex-shrink-0 bg-gradient-to-br ${color} p-3 rounded-lg shadow-sm`}>
            <div className="text-white">
              {icon}
            </div>
          </div>
          <div className="ml-4">
            <p className="text-sm font-medium text-gray-500">{title}</p>
            <div className="flex items-center mt-1">
              <p className="text-2xl font-bold text-gray-900">{value}</p>
            </div>
          </div>
        </div>
        {trend.value !== 0 && (
          <div className={`flex items-center px-2 py-1 rounded-full text-xs font-medium ${getTrendColor()}`}>
            {getTrendIcon()}
            <span className="ml-1">{Math.abs(trend.value)}%</span>
          </div>
        )}
      </div>
    </div>
  );
};

export default Dashboard;