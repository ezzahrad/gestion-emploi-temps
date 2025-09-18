import React, { useState, useEffect } from 'react';
import { useAuth } from '../../contexts/AuthContext';
import { Card, Button, Loading, Table, Modal, Form } from '../../components/ui';
import { PDFExportCenter } from '../../components/pdf';
import { NotificationCenter } from '../../components/notifications';
import { 
  Users, BookOpen, Calendar, FileText, Bell, Plus,
  Edit, Eye, Check, X, TrendingUp, Award, AlertTriangle 
} from 'lucide-react';
import { toast } from 'react-hot-toast';
import enhancedAPI from '../../services/enhancedAPI';
import { 
  Grade, Evaluation, Absence, AttendanceRecord,
  SubjectGradeSummary 
} from '../../types/enhanced';

export const EnhancedTeacherDashboard: React.FC = () => {
  const { user } = useAuth();
  const [activeTab, setActiveTab] = useState('overview');
  const [mySubjects, setMySubjects] = useState([]);
  const [myStudents, setMyStudents] = useState([]);
  const [pendingGrades, setPendingGrades] = useState<Grade[]>([]);
  const [pendingAbsences, setPendingAbsences] = useState<Absence[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    loadTeacherData();
  }, []);

  const loadTeacherData = async () => {
    try {
      setLoading(true);
      // En réalité, ces données viendraient d'APIs dédiées
      // Pour l'instant, on simule
      
      // Charger mes matières
      // const subjectsRes = await coreAPI.getSubjects({ teacher: user?.id });
      // setMySubjects(subjectsRes.data);
      
      // Charger mes étudiants
      // const studentsRes = await coreAPI.getStudents({ teacher: user?.id });
      // setMyStudents(studentsRes.data);
      
      // Charger les notes en attente de publication
      const gradesRes = await enhancedAPI.grades.getGrades({ 
        graded_by: user?.id,
        is_published: false 
      });
      setPendingGrades(gradesRes.data);
      
      // Charger les absences en attente d'approbation
      const absencesRes = await enhancedAPI.absences.getAbsences({ 
        status: 'pending',
        schedule__teacher: user?.id 
      });
      setPendingAbsences(absencesRes.data);
      
    } catch (error) {
      console.error('Erreur chargement données enseignant:', error);
      toast.error('Erreur lors du chargement');
    } finally {
      setLoading(false);
    }
  };

  const tabs = [
    { id: 'overview', label: 'Vue d\'ensemble', icon: TrendingUp },
    { id: 'evaluations', label: 'Évaluations', icon: BookOpen },
    { id: 'absences', label: 'Absences', icon: Calendar },
    { id: 'students', label: 'Mes Étudiants', icon: Users },
    { id: 'exports', label: 'Exports', icon: FileText },
    { id: 'notifications', label: 'Notifications', icon: Bell }
  ];

  if (loading) {
    return <Loading message="Chargement de votre espace enseignant..." />;
  }

  return (
    <div className="min-h-screen bg-gray-50">
      {/* Header */}
      <div className="bg-white shadow-sm border-b">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="py-6">
            <h1 className="text-2xl font-bold text-gray-900">
              Espace Enseignant - {user?.full_name}
            </h1>
            <p className="text-gray-600 mt-1">
              Département: {user?.department?.name || 'Non défini'}
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
          <TeacherOverview 
            pendingGrades={pendingGrades}
            pendingAbsences={pendingAbsences}
            onRefresh={loadTeacherData}
          />
        )}
        
        {activeTab === 'evaluations' && (
          <EvaluationManagement userId={user?.id} />
        )}
        
        {activeTab === 'absences' && (
          <TeacherAbsenceManagement teacherId={user?.id} />
        )}
        
        {activeTab === 'students' && (
          <StudentsManagement teacherId={user?.id} />
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

const TeacherOverview: React.FC<{
  pendingGrades: Grade[];
  pendingAbsences: Absence[];
  onRefresh: () => void;
}> = ({ pendingGrades, pendingAbsences, onRefresh }) => {
  const publishGrade = async (gradeId: number) => {
    try {
      await enhancedAPI.grades.publishGrade(gradeId);
      toast.success('Note publiée');
      onRefresh();
    } catch (error) {
      console.error('Erreur publication note:', error);
      toast.error('Erreur lors de la publication');
    }
  };

  const approveAbsence = async (absenceId: number) => {
    try {
      await enhancedAPI.absences.approveAbsence(absenceId);
      toast.success('Absence approuvée');
      onRefresh();
    } catch (error) {
      console.error('Erreur approbation absence:', error);
      toast.error('Erreur lors de l\'approbation');
    }
  };

  const rejectAbsence = async (absenceId: number) => {
    try {
      await enhancedAPI.absences.rejectAbsence(absenceId);
      toast.success('Absence rejetée');
      onRefresh();
    } catch (error) {
      console.error('Erreur rejet absence:', error);
      toast.error('Erreur lors du rejet');
    }
  };

  return (
    <div className="space-y-6">
      {/* Statistiques rapides */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
        <Card className="p-6">
          <div className="flex items-center">
            <div className="flex-shrink-0">
              <BookOpen className="h-8 w-8 text-blue-500" />
            </div>
            <div className="ml-4">
              <p className="text-sm font-medium text-gray-500">Notes en attente</p>
              <p className="text-2xl font-semibold text-gray-900">
                {pendingGrades.length}
              </p>
            </div>
          </div>
        </Card>

        <Card className="p-6">
          <div className="flex items-center">
            <div className="flex-shrink-0">
              <Calendar className="h-8 w-8 text-orange-500" />
            </div>
            <div className="ml-4">
              <p className="text-sm font-medium text-gray-500">Absences à traiter</p>
              <p className="text-2xl font-semibold text-gray-900">
                {pendingAbsences.length}
              </p>
            </div>
          </div>
        </Card>

        <Card className="p-6">
          <div className="flex items-center">
            <div className="flex-shrink-0">
              <Users className="h-8 w-8 text-green-500" />
            </div>
            <div className="ml-4">
              <p className="text-sm font-medium text-gray-500">Mes étudiants</p>
              <p className="text-2xl font-semibold text-gray-900">
                0 {/* À calculer depuis les APIs */}
              </p>
            </div>
          </div>
        </Card>
      </div>

      {/* Notes en attente de publication */}
      {pendingGrades.length > 0 && (
        <Card>
          <div className="p-4 border-b flex justify-between items-center">
            <h3 className="text-lg font-medium">Notes en attente de publication</h3>
            <span className="text-sm text-gray-500">
              {pendingGrades.length} note(s)
            </span>
          </div>
          <Table
            headers={[
              'Étudiant',
              'Évaluation',
              'Note',
              'Pourcentage',
              'Date',
              'Actions'
            ]}
            data={pendingGrades.slice(0, 5).map(grade => ({
              id: grade.id,
              etudiant: grade.student_name,
              evaluation: grade.evaluation_name,
              note: `${grade.grade_value}/${grade.max_grade}`,
              pourcentage: `${grade.percentage.toFixed(1)}%`,
              date: new Date(grade.created_at).toLocaleDateString('fr-FR'),
              actions: (
                <div className="flex space-x-2">
                  <Button
                    size="sm"
                    onClick={() => publishGrade(grade.id)}
                    className="bg-green-600 hover:bg-green-700"
                  >
                    <Check className="w-4 h-4" />
                  </Button>
                  <Button
                    size="sm"
                    variant="outline"
                  >
                    <Edit className="w-4 h-4" />
                  </Button>
                </div>
              )
            }))}
          />
        </Card>
      )}

      {/* Absences à traiter */}
      {pendingAbsences.length > 0 && (
        <Card>
          <div className="p-4 border-b flex justify-between items-center">
            <h3 className="text-lg font-medium">Absences à traiter</h3>
            <span className="text-sm text-gray-500">
              {pendingAbsences.length} absence(s)
            </span>
          </div>
          <Table
            headers={[
              'Étudiant',
              'Date',
              'Matière',
              'Type',
              'Raison',
              'Actions'
            ]}
            data={pendingAbsences.slice(0, 5).map(absence => ({
              id: absence.id,
              etudiant: absence.schedule_details.subject_name, // À corriger
              date: new Date(absence.absence_date).toLocaleDateString('fr-FR'),
              matiere: absence.schedule_details.subject_name,
              type: absence.absence_type,
              raison: absence.reason.substring(0, 50) + '...',
              actions: (
                <div className="flex space-x-2">
                  <Button
                    size="sm"
                    onClick={() => approveAbsence(absence.id)}
                    className="bg-green-600 hover:bg-green-700"
                  >
                    <Check className="w-4 h-4" />
                  </Button>
                  <Button
                    size="sm"
                    onClick={() => rejectAbsence(absence.id)}
                    className="bg-red-600 hover:bg-red-700"
                  >
                    <X className="w-4 h-4" />
                  </Button>
                  <Button
                    size="sm"
                    variant="outline"
                  >
                    <Eye className="w-4 h-4" />
                  </Button>
                </div>
              )
            }))}
          />
        </Card>
      )}

      {/* Actions rapides */}
      <Card className="p-6">
        <h3 className="text-lg font-medium text-gray-900 mb-4">Actions rapides</h3>
        <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
          <Button className="p-4 h-auto flex-col bg-blue-600 hover:bg-blue-700">
            <Plus className="w-6 h-6 mb-2" />
            <span>Nouvelle évaluation</span>
          </Button>
          <Button className="p-4 h-auto flex-col bg-green-600 hover:bg-green-700">
            <FileText className="w-6 h-6 mb-2" />
            <span>Prendre les présences</span>
          </Button>
          <Button className="p-4 h-auto flex-col bg-purple-600 hover:bg-purple-700">
            <Award className="w-6 h-6 mb-2" />
            <span>Voir les notes</span>
          </Button>
        </div>
      </Card>
    </div>
  );
};

const EvaluationManagement: React.FC<{ userId: number | undefined }> = ({ userId }) => {
  const [evaluations, setEvaluations] = useState<Evaluation[]>([]);
  const [loading, setLoading] = useState(true);
  const [showCreateEvaluation, setShowCreateEvaluation] = useState(false);

  useEffect(() => {
    loadEvaluations();
  }, []);

  const loadEvaluations = async () => {
    try {
      const response = await enhancedAPI.grades.getEvaluations({ created_by: userId });
      setEvaluations(response.data);
    } catch (error) {
      console.error('Erreur chargement évaluations:', error);
    } finally {
      setLoading(false);
    }
  };

  if (loading) {
    return <Loading message="Chargement des évaluations..." />;
  }

  return (
    <div className="space-y-6">
      <div className="flex justify-between items-center">
        <h2 className="text-xl font-semibold">Mes Évaluations</h2>
        <Button
          onClick={() => setShowCreateEvaluation(true)}
          className="bg-blue-600 hover:bg-blue-700"
        >
          <Plus className="w-4 h-4 mr-2" />
          Nouvelle évaluation
        </Button>
      </div>

      <Card>
        <Table
          headers={[
            'Nom',
            'Matière',
            'Type',
            'Date',
            'Note max',
            'Coefficient',
            'Statut',
            'Actions'
          ]}
          data={evaluations.map(evaluation => ({
            id: evaluation.id,
            nom: evaluation.name,
            matiere: evaluation.subject_name,
            type: evaluation.evaluation_type,
            date: new Date(evaluation.evaluation_date).toLocaleDateString('fr-FR'),
            note_max: evaluation.max_grade,
            coefficient: evaluation.coefficient,
            statut: evaluation.is_published ? (
              <span className="px-2 py-1 bg-green-100 text-green-800 rounded text-sm">
                Publiée
              </span>
            ) : (
              <span className="px-2 py-1 bg-yellow-100 text-yellow-800 rounded text-sm">
                Brouillon
              </span>
            ),
            actions: (
              <div className="flex space-x-2">
                <Button size="sm" variant="outline">
                  <Eye className="w-4 h-4" />
                </Button>
                <Button size="sm" variant="outline">
                  <Edit className="w-4 h-4" />
                </Button>
              </div>
            )
          }))}
        />
      </Card>

      {/* Modal création évaluation */}
      {showCreateEvaluation && (
        <Modal
          isOpen={showCreateEvaluation}
          onClose={() => setShowCreateEvaluation(false)}
          title="Créer une évaluation"
        >
          <p>Formulaire de création d'évaluation à implémenter</p>
        </Modal>
      )}
    </div>
  );
};

const TeacherAbsenceManagement: React.FC<{ teacherId: number | undefined }> = ({ teacherId }) => {
  return (
    <div className="space-y-6">
      <h2 className="text-xl font-semibold">Gestion des Absences</h2>
      <p className="text-gray-600">
        Interface de gestion des absences pour les enseignants à implémenter
      </p>
    </div>
  );
};

const StudentsManagement: React.FC<{ teacherId: number | undefined }> = ({ teacherId }) => {
  return (
    <div className="space-y-6">
      <h2 className="text-xl font-semibold">Mes Étudiants</h2>
      <p className="text-gray-600">
        Liste et gestion des étudiants à implémenter
      </p>
    </div>
  );
};

export default EnhancedTeacherDashboard;
