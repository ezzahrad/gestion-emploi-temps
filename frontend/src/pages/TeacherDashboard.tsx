// TeacherDashboard.tsx - Tableau de bord enseignant optimisé pour desktop
import React, { useState, useEffect } from 'react';
import { useAuth, useAuthenticatedFetch } from '../contexts/AuthContext';
import {
  Calendar, Clock, Users, BookOpen, MapPin, TrendingUp,
  AlertCircle, Upload, Download, BarChart3, Plus,
  Edit, Eye, RefreshCw, Filter, Search, Grid, List,
  CheckCircle, XCircle, Activity, Bell, MessageSquare,
  FileText, Target, Settings, Coffee, Star
} from 'lucide-react';
import { toast } from 'react-hot-toast';
import { Link } from 'react-router-dom';
import { format, startOfWeek, isToday, isTomorrow } from 'date-fns';
import { fr } from 'date-fns/locale';

// --- Interfaces
interface TeacherStats {
  weekly_sessions: number;
  weekly_hours: number;
  total_subjects_taught: number;
  workload_percentage: number;
  upcoming_sessions: UpcomingSession[];
  recent_activities: ActivityItem[];
  student_count: number;
  average_class_size: number;
  next_break_duration: number;
  performance_metrics: PerformanceMetric[];
}

interface UpcomingSession {
  id: number;
  subject_name: string;
  subject_code: string;
  room_name: string;
  start_time: string;
  end_time: string;
  date: string;
  student_count: number;
  room_capacity: number;
  duration_minutes: number;
  is_cancelled: boolean;
  is_makeup: boolean;
  notes?: string;
  program_names: string[];
}

interface ActivityItem {
  id: number;
  type: 'grade' | 'absence' | 'session' | 'material';
  title: string;
  description: string;
  timestamp: string;
  student_count?: number;
}

interface PerformanceMetric {
  label: string;
  value: number;
  max_value: number;
  unit: string;
  trend: 'up' | 'down' | 'stable';
  color: string;
}

interface QuickAction {
  title: string;
  description: string;
  icon: React.ReactNode;
  link: string;
  color: string;
  badge?: string;
}

// --- Composant principal
const TeacherDashboard: React.FC = () => {
  const { user } = useAuth();
  const authenticatedFetch = useAuthenticatedFetch();

  const [stats, setStats] = useState<TeacherStats | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [currentWeek] = useState(startOfWeek(new Date(), { locale: fr }));
  const [viewMode, setViewMode] = useState<'grid' | 'list'>('grid');
  const [refreshing, setRefreshing] = useState(false);

  // --- Charger les données
  const loadDashboardData = async () => {
    try {
      setLoading(true);
      setError(null);

      const response = await authenticatedFetch('/api/core/dashboard/teacher/');
      if (response.ok) {
        const data = await response.json();
        setStats(data);
      } else {
        throw new Error('Erreur lors du chargement des données enseignant');
      }
    } catch (err) {
      console.error('Erreur dashboard enseignant:', err);
      setError('Impossible de charger le tableau de bord enseignant');
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
  }, []);

  // --- Helpers pour la charge de travail
  const getWorkloadColor = (percentage: number) => {
    if (percentage >= 90) return 'from-red-500 to-red-600';
    if (percentage >= 75) return 'from-orange-500 to-orange-600';
    if (percentage >= 50) return 'from-yellow-500 to-yellow-600';
    return 'from-green-500 to-emerald-600';
  };

  const getWorkloadStatus = (percentage: number) => {
    if (percentage >= 90) return { text: 'Surchargé', color: 'text-red-600' };
    if (percentage >= 75) return { text: 'Chargé', color: 'text-orange-600' };
    if (percentage >= 50) return { text: 'Normal', color: 'text-yellow-600' };
    return { text: 'Léger', color: 'text-green-600' };
  };

  // --- Rendu cartes statistiques
  const renderStatCard = (
    title: string,
    value: string | number,
    icon: React.ReactNode,
    color: string,
    subtitle?: string
  ) => (
    <div className="bg-white rounded-xl shadow-sm border border-gray-200 p-6 hover:shadow-md transition-all duration-200">
      <div className="flex items-center">
        <div className={`flex-shrink-0 bg-gradient-to-br ${color} p-3 rounded-lg shadow-sm`}>
          <div className="text-white">{icon}</div>
        </div>
        <div className="ml-4">
          <p className="text-sm font-medium text-gray-500">{title}</p>
          <p className="text-2xl font-bold text-gray-900">{value}</p>
          {subtitle && <p className="text-xs text-gray-500 mt-1">{subtitle}</p>}
        </div>
      </div>
    </div>
  );

  // --- Rendu si chargement
  if (loading) {
    return (
      <div className="min-h-screen bg-gray-50 flex items-center justify-center">
        <div className="text-center">
          <div className="animate-spin rounded-full h-16 w-16 border-b-2 border-primary-600 mx-auto"></div>
          <p className="mt-4 text-gray-600 text-lg">Chargement de votre tableau de bord...</p>
        </div>
      </div>
    );
  }

  // --- Rendu si erreur
  if (error) {
    return (
      <div className="min-h-screen bg-gray-50 flex items-center justify-center">
        <div className="text-center max-w-md">
          <AlertCircle className="h-16 w-16 text-red-500 mx-auto mb-4" />
          <h2 className="text-xl font-semibold text-gray-900 mb-2">Erreur de chargement</h2>
          <p className="text-gray-600 mb-6">{error}</p>
          <button onClick={loadDashboardData} className="btn-primary flex items-center gap-2">
            <RefreshCw className="h-4 w-4" />
            Réessayer
          </button>
        </div>
      </div>
    );
  }

  // --- Rendu principal
  return (
    <div className="min-h-screen bg-gray-50">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        {/* En-tête */}
        <div className="mb-8">
          <h1 className="text-4xl font-bold text-gray-900">Mon Tableau de Bord</h1>
          <p className="text-lg text-gray-600 mt-2">
            Bonjour {user?.first_name}, voici un aperçu de votre activité
          </p>
          <div className="mt-3 text-sm text-gray-500">
            Semaine du {format(currentWeek, 'd MMMM yyyy', { locale: fr })}
          </div>
        </div>

        {/* Statistiques principales */}
        {stats && (
          <div className="mb-8 grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
            {renderStatCard('Cours cette semaine', stats.weekly_sessions, <Calendar className="h-6 w-6" />, 'from-blue-500 to-blue-600', `${stats.weekly_hours}h au total`)}
            {renderStatCard('Matières enseignées', stats.total_subjects_taught, <BookOpen className="h-6 w-6" />, 'from-purple-500 to-purple-600')}
            {renderStatCard('Étudiants total', stats.student_count || 0, <Users className="h-6 w-6" />, 'from-green-500 to-emerald-600', `${stats.average_class_size || 0} moy./classe`)}
            <div className="bg-white rounded-xl shadow-sm border border-gray-200 p-6 hover:shadow-md transition-all duration-200">
              <div className="flex items-center">
                <div className={`flex-shrink-0 bg-gradient-to-br ${getWorkloadColor(stats.workload_percentage || 0)} p-3 rounded-lg shadow-sm`}>
                  <TrendingUp className="h-6 w-6 text-white" />
                </div>
                <div className="ml-4">
                  <p className="text-sm font-medium text-gray-500">Charge de travail</p>
                  <p className="text-2xl font-bold text-gray-900">{stats.workload_percentage?.toFixed(1) || 0}%</p>
                  <p className={`text-xs font-medium ${getWorkloadStatus(stats.workload_percentage || 0).color}`}>
                    {getWorkloadStatus(stats.workload_percentage || 0).text}
                  </p>
                </div>
              </div>
            </div>
          </div>
        )}
      </div>
    </div>
  );
};

export default TeacherDashboard;
