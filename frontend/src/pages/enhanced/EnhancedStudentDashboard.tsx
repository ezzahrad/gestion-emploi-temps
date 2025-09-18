import React, { useState, useEffect } from 'react';
import { useAuth } from '../../contexts/AuthContext';
import { Card, Button, Loading } from '../../components/ui';
import { StudentGradesView } from '../../components/grades';
import { AbsenceManagement } from '../../components/absences';
import { PDFExportCenter } from '../../components/pdf';
import { NotificationCenter } from '../../components/notifications';
import { 
  BookOpen, Calendar, FileText, Bell, TrendingUp, 
  Award, AlertTriangle, Download, Eye 
} from 'lucide-react';
import enhancedAPI from '../../services/enhancedAPI';
import { StudentStats } from '../../types/enhanced';

export const EnhancedStudentDashboard: React.FC = () => {
  const { user } = useAuth();
  const [activeTab, setActiveTab] = useState('overview');
  const [stats, setStats] = useState<StudentStats | null>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    loadStudentStats();
  }, []);

  const loadStudentStats = async () => {
    try {
      setLoading(true);
      // Simuler le chargement des statistiques étudiant
      // En réalité, cela viendrait d'une API dédiée
      const mockStats: StudentStats = {
        total_absences: 3,
        justified_absences: 2,
        unjustified_absences: 1,
        absence_rate: 5.2,
        pending_makeups: 1,
        completed_makeups: 0,
        current_average: 14.5,
        subjects_count: 6,
        credits_acquired: 18,
        credits_total: 30,
        attendance_rate: 94.8,
        grade_trend: 'improving'
      };
      setStats(mockStats);
    } catch (error) {
      console.error('Erreur chargement stats:', error);
    } finally {
      setLoading(false);
    }
  };

  const tabs = [
    { id: 'overview', label: 'Vue d\'ensemble', icon: TrendingUp },
    { id: 'grades', label: 'Mes Notes', icon: BookOpen },
    { id: 'absences', label: 'Mes Absences', icon: Calendar },
    { id: 'exports', label: 'Mes Exports', icon: FileText },
    { id: 'notifications', label: 'Notifications', icon: Bell }
  ];

  if (loading) {
    return <Loading message="Chargement de votre dashboard..." />;
  }

  return (
    <div className="min-h-screen bg-gray-50">
      {/* Header */}
      <div className="bg-white shadow-sm border-b">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="py-6">
            <h1 className="text-2xl font-bold text-gray-900">
              Tableau de Bord Étudiant - {user?.full_name}
            </h1>
            <p className="text-gray-600 mt-1">
              Programme: {user?.program?.name || 'Non défini'}
            </p>
          </div>
        </div>
      </div>

      {/* Navigation tabs */}
      <div className="bg-white border-b">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <nav className="flex space-x-8" aria-label="Tabs">
            {tabs.map((tab) => {
              const Icon = tab.icon;
              return (
                <button
                  key={tab.id}
                  onClick={() => setActiveTab(tab.id)}
                  className={`${
                    activeTab === tab.id
                      ? 'border-blue-500 text-blue-600'
                      : 'border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300'
                  } whitespace-nowrap py-4 px-1 border-b-2 font-medium text-sm flex items-center space-x-2`}
                >
                  <Icon className="w-4 h-4" />
                  <span>{tab.label}</span>
                </button>
              );
            })}
          </nav>
        </div>
      </div>

      {/* Content */}
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        {activeTab === 'overview' && (
          <StudentOverview stats={stats} user={user} />
        )}
        
        {activeTab === 'grades' && (
          <StudentGradesView studentId={user?.id} isCurrentUser={true} />
        )}
        
        {activeTab === 'absences' && (
          <AbsenceManagement studentId={user?.id} isCurrentUser={true} />
        )}
        
        {activeTab === 'exports' && (
          <PDFExportCenter userRole={user?.role} />
        )}
        
        {activeTab === 'notifications' && (
          <NotificationCenter />
        )}
      </div>
    </div>
  );
};

const StudentOverview: React.FC<{ 
  stats: StudentStats | null; 
  user: any;
}> = ({ stats, user }) => {
  const quickActions = [
    {
      title: 'Voir mes notes',
      description: 'Consulter mon relevé de notes',
      icon: BookOpen,
      color: 'bg-blue-500',
      action: () => window.location.href = '#grades'
    },
    {
      title: 'Déclarer une absence',
      description: 'Signaler une absence récente',
      icon: Calendar,
      color: 'bg-orange-500',
      action: () => window.location.href = '#absences'
    },
    {
      title: 'Export PDF',
      description: 'Télécharger mes documents',
      icon: Download,
      color: 'bg-green-500',
      action: () => window.location.href = '#exports'
    },
    {
      title: 'Mon emploi du temps',
      description: 'Consulter mon planning',
      icon: Eye,
      color: 'bg-purple-500',
      action: () => window.location.href = '/schedule'
    }
  ];

  if (!stats) {
    return <Loading message="Chargement des statistiques..." />;
  }

  return (
    <div className="space-y-6">
      {/* Statistiques principales */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
        <Card className="p-6">
          <div className="flex items-center">
            <div className="flex-shrink-0">
              <Award className="h-8 w-8 text-blue-500" />
            </div>
            <div className="ml-4">
              <p className="text-sm font-medium text-gray-500">Moyenne générale</p>
              <p className="text-2xl font-semibold text-gray-900">
                {stats.current_average.toFixed(1)}/20
              </p>
            </div>
          </div>
        </Card>

        <Card className="p-6">
          <div className="flex items-center">
            <div className="flex-shrink-0">
              <TrendingUp className={`h-8 w-8 ${
                stats.attendance_rate >= 95 ? 'text-green-500' :
                stats.attendance_rate >= 85 ? 'text-yellow-500' : 'text-red-500'
              }`} />
            </div>
            <div className="ml-4">
              <p className="text-sm font-medium text-gray-500">Taux de présence</p>
              <p className="text-2xl font-semibold text-gray-900">
                {stats.attendance_rate.toFixed(1)}%
              </p>
            </div>
          </div>
        </Card>

        <Card className="p-6">
          <div className="flex items-center">
            <div className="flex-shrink-0">
              <BookOpen className="h-8 w-8 text-purple-500" />
            </div>
            <div className="ml-4">
              <p className="text-sm font-medium text-gray-500">Crédits acquis</p>
              <p className="text-2xl font-semibold text-gray-900">
                {stats.credits_acquired}/{stats.credits_total}
              </p>
            </div>
          </div>
        </Card>

        <Card className="p-6">
          <div className="flex items-center">
            <div className="flex-shrink-0">
              <Calendar className={`h-8 w-8 ${
                stats.total_absences <= 2 ? 'text-green-500' :
                stats.total_absences <= 5 ? 'text-yellow-500' : 'text-red-500'
              }`} />
            </div>
            <div className="ml-4">
              <p className="text-sm font-medium text-gray-500">Total absences</p>
              <p className="text-2xl font-semibold text-gray-900">
                {stats.total_absences}
              </p>
            </div>
          </div>
        </Card>
      </div>

      {/* Alertes et recommandations */}
      {(stats.pending_makeups > 0 || stats.unjustified_absences > 0) && (
        <Card className="p-6 border-l-4 border-l-orange-500 bg-orange-50">
          <div className="flex">
            <div className="flex-shrink-0">
              <AlertTriangle className="h-5 w-5 text-orange-400" />
            </div>
            <div className="ml-3">
              <h3 className="text-sm font-medium text-orange-800">
                Action requise
              </h3>
              <div className="mt-2 text-sm text-orange-700">
                <ul className="list-disc list-inside space-y-1">
                  {stats.pending_makeups > 0 && (
                    <li>
                      Vous avez {stats.pending_makeups} rattrapage(s) en attente
                    </li>
                  )}
                  {stats.unjustified_absences > 0 && (
                    <li>
                      {stats.unjustified_absences} absence(s) non justifiée(s)
                    </li>
                  )}
                </ul>
              </div>
            </div>
          </div>
        </Card>
      )}

      {/* Actions rapides */}
      <Card className="p-6">
        <h3 className="text-lg font-medium text-gray-900 mb-4">Actions rapides</h3>
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
          {quickActions.map((action, index) => {
            const Icon = action.icon;
            return (
              <button
                key={index}
                onClick={action.action}
                className="text-left p-4 rounded-lg border border-gray-200 hover:border-gray-300 hover:shadow-md transition-all duration-200"
              >
                <div className="flex items-center">
                  <div className={`flex-shrink-0 p-2 rounded-lg ${action.color}`}>
                    <Icon className="h-5 w-5 text-white" />
                  </div>
                  <div className="ml-3 min-w-0 flex-1">
                    <p className="text-sm font-medium text-gray-900 truncate">
                      {action.title}
                    </p>
                    <p className="text-sm text-gray-500 truncate">
                      {action.description}
                    </p>
                  </div>
                </div>
              </button>
            );
          })}
        </div>
      </Card>

      {/* Tendance des notes */}
      <Card className="p-6">
        <h3 className="text-lg font-medium text-gray-900 mb-4">Tendance académique</h3>
        <div className="flex items-center">
          <TrendingUp className={`h-5 w-5 mr-2 ${
            stats.grade_trend === 'improving' ? 'text-green-500' :
            stats.grade_trend === 'stable' ? 'text-yellow-500' : 'text-red-500'
          }`} />
          <span className="text-sm text-gray-600">
            {stats.grade_trend === 'improving' ? 'En amélioration' :
             stats.grade_trend === 'stable' ? 'Stable' : 'En baisse'}
          </span>
        </div>
        <div className="mt-4">
          <div className="bg-gray-200 rounded-full h-2">
            <div 
              className={`h-2 rounded-full ${
                stats.current_average >= 16 ? 'bg-green-500' :
                stats.current_average >= 12 ? 'bg-yellow-500' : 'bg-red-500'
              }`}
              style={{ width: `${(stats.current_average / 20) * 100}%` }}
            />
          </div>
          <p className="text-xs text-gray-500 mt-1">
            Progression vers l'excellence (16/20)
          </p>
        </div>
      </Card>

      {/* Notifications récentes (aperçu) */}
      <Card className="p-6">
        <div className="flex justify-between items-center mb-4">
          <h3 className="text-lg font-medium text-gray-900">
            Notifications récentes
          </h3>
          <Button
            size="sm"
            variant="outline"
            onClick={() => window.location.href = '#notifications'}
          >
            Voir toutes
          </Button>
        </div>
        <NotificationCenter isDropdown={true} maxItems={3} />
      </Card>
    </div>
  );
};

export default EnhancedStudentDashboard;
