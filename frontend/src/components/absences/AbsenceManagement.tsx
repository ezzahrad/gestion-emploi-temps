import React, { useState, useEffect } from 'react';
import { Card, Button, Modal, Table, Loading, Form } from '../ui';
import { 
  Calendar, AlertTriangle, CheckCircle, Clock, Upload, 
  FileText, TrendingDown, Users, Calendar as CalendarIcon 
} from 'lucide-react';
import { toast } from 'react-hot-toast';
import enhancedAPI from '../../services/enhancedAPI';
import { 
  Absence, MakeupSession, StudentAbsenceStatistics, 
  AttendanceRecord 
} from '../../types';

interface AbsenceManagementProps {
  studentId?: number;
  isCurrentUser?: boolean;
}

export const AbsenceManagement: React.FC<AbsenceManagementProps> = ({ 
  studentId, 
  isCurrentUser = false 
}) => {
  const [absences, setAbsences] = useState<Absence[]>([]);
  const [makeupSessions, setMakeupSessions] = useState<MakeupSession[]>([]);
  const [statistics, setStatistics] = useState<StudentAbsenceStatistics | null>(null);
  const [loading, setLoading] = useState(true);
  const [showCreateAbsence, setShowCreateAbsence] = useState(false);
  const [selectedAbsence, setSelectedAbsence] = useState<Absence | null>(null);

  useEffect(() => {
    loadAbsenceData();
  }, [studentId]);

  const loadAbsenceData = async () => {
    try {
      setLoading(true);
      
      if (isCurrentUser) {
        const [absencesRes, sessionsRes, statsRes] = await Promise.all([
          enhancedAPI.absences.getMyAbsences(),
          enhancedAPI.absences.getMySessions(),
          enhancedAPI.absences.getMyStatistics()
        ]);
        
        setAbsences(absencesRes.data);
        setMakeupSessions(sessionsRes.data);
        setStatistics(statsRes.data);
      } else {
        const [absencesRes, sessionsRes, statsRes] = await Promise.all([
          enhancedAPI.absences.getAbsences({ student: studentId }),
          enhancedAPI.absences.getMakeupSessions({ absence__student: studentId }),
          enhancedAPI.absences.getAbsenceStatistics({ student: studentId })
        ]);
        
        setAbsences(absencesRes.data);
        setMakeupSessions(sessionsRes.data);
        setStatistics(statsRes.data[0] || null);
      }
    } catch (error) {
      console.error('Erreur lors du chargement des absences:', error);
      toast.error('Erreur lors du chargement des données');
    } finally {
      setLoading(false);
    }
  };

  const exportAbsenceReport = async () => {
    try {
      const exportData = {
        export_type: 'absence_report',
        student_id: studentId,
        start_date: new Date(Date.now() - 90 * 24 * 60 * 60 * 1000).toISOString().split('T')[0], // 3 mois
        end_date: new Date().toISOString().split('T')[0],
        include_statistics: true
      };

      const response = await enhancedAPI.pdfExport.createExport(exportData);
      
      toast.success('Export du rapport d\'absences lancé !');
      
      // Surveiller le statut
      enhancedAPI.helpers.pdf.pollJobStatus(
        response.data.job_id,
        (status) => {
          if (status.status === 'completed') {
            toast.success('Rapport d\'absences prêt !');
            enhancedAPI.helpers.pdf.downloadAndSavePDF(
              status.job_id, 
              `rapport_absences_${new Date().getTime()}.pdf`
            );
          }
        }
      );
    } catch (error) {
      console.error('Erreur export PDF:', error);
      toast.error('Erreur lors de l\'export PDF');
    }
  };

  if (loading) {
    return <Loading message="Chargement des données..." />;
  }

  return (
    <div className="space-y-6">
      {/* Statistiques d'absence */}
      {statistics && (
        <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
          <Card className="p-4">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm text-gray-600">Total absences</p>
                <p className="text-2xl font-bold text-red-600">
                  {statistics.total_absences}
                </p>
              </div>
              <Calendar className="w-8 h-8 text-red-500" />
            </div>
          </Card>

          <Card className="p-4">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm text-gray-600">Taux d'absence</p>
                <p className={`text-2xl font-bold ${
                  statistics.absence_rate > 20 ? 'text-red-600' : 
                  statistics.absence_rate > 10 ? 'text-orange-600' : 'text-green-600'
                }`}>
                  {statistics.absence_rate.toFixed(1)}%
                </p>
              </div>
              <TrendingDown className="w-8 h-8 text-orange-500" />
            </div>
          </Card>

          <Card className="p-4">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm text-gray-600">Absences justifiées</p>
                <p className="text-2xl font-bold text-blue-600">
                  {statistics.justified_absences}
                </p>
              </div>
              <CheckCircle className="w-8 h-8 text-blue-500" />
            </div>
          </Card>

          <Card className="p-4">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm text-gray-600">Rattrapages en attente</p>
                <p className="text-2xl font-bold text-purple-600">
                  {statistics.pending_makeups}
                </p>
              </div>
              <Clock className="w-8 h-8 text-purple-500" />
            </div>
          </Card>
        </div>
      )}

      {/* Alerte niveau de risque */}
      {statistics?.is_at_risk && (
        <div className={`p-4 rounded-lg border-l-4 ${
          statistics.risk_level === 'critical' ? 'bg-red-50 border-red-500' :
          statistics.risk_level === 'high' ? 'bg-orange-50 border-orange-500' :
          'bg-yellow-50 border-yellow-500'
        }`}>
          <div className="flex items-center">
            <AlertTriangle className={`w-5 h-5 mr-2 ${
              statistics.risk_level === 'critical' ? 'text-red-600' :
              statistics.risk_level === 'high' ? 'text-orange-600' :
              'text-yellow-600'
            }`} />
            <div>
              <h3 className="font-medium">
                Niveau de risque : {statistics.risk_level}
              </h3>
              <p className="text-sm text-gray-600 mt-1">
                Votre taux d'absence nécessite votre attention. 
                Pensez à planifier vos rattrapages.
              </p>
            </div>
          </div>
        </div>
      )}

      {/* Actions */}
      <div className="flex justify-between items-center">
        <h2 className="text-xl font-semibold">Gestion des Absences</h2>
        <div className="space-x-2">
          {isCurrentUser && (
            <Button
              onClick={() => setShowCreateAbsence(true)}
              className="bg-blue-600 hover:bg-blue-700"
            >
              <Calendar className="w-4 h-4 mr-2" />
              Déclarer absence
            </Button>
          )}
          <Button
            onClick={exportAbsenceReport}
            className="bg-green-600 hover:bg-green-700"
          >
            <FileText className="w-4 h-4 mr-2" />
            Rapport PDF
          </Button>
        </div>
      </div>

      {/* Liste des absences */}
      <Card>
        <div className="p-4 border-b">
          <h3 className="text-lg font-medium">Historique des absences</h3>
        </div>
        <Table
          headers={[
            'Date',
            'Matière',
            'Type',
            'Statut',
            'Rattrapage',
            'Actions'
          ]}
          data={absences.map(absence => ({
            id: absence.id,
            date: new Date(absence.absence_date).toLocaleDateString('fr-FR'),
            matiere: absence.schedule_details.subject_name,
            type: (
              <span className={`px-2 py-1 rounded text-sm ${
                getAbsenceTypeColor(absence.absence_type)
              }`}>
                {getAbsenceTypeLabel(absence.absence_type)}
              </span>
            ),
            statut: (
              <span className={`px-2 py-1 rounded text-sm ${
                getAbsenceStatusColor(absence.status)
              }`}>
                {getAbsenceStatusLabel(absence.status)}
              </span>
            ),
            rattrapage: absence.is_makeup_required ? (
              <span className={`px-2 py-1 rounded text-sm ${
                absence.makeup_completed ? 'bg-green-100 text-green-800' : 'bg-orange-100 text-orange-800'
              }`}>
                {absence.makeup_completed ? 'Terminé' : 'Requis'}
              </span>
            ) : (
              <span className="text-gray-400">Non requis</span>
            ),
            actions: (
              <Button
                size="sm"
                variant="outline"
                onClick={() => setSelectedAbsence(absence)}
              >
                Détails
              </Button>
            )
          }))}
        />
      </Card>

      {/* Sessions de rattrapage */}
      {makeupSessions.length > 0 && (
        <Card>
          <div className="p-4 border-b">
            <h3 className="text-lg font-medium">Sessions de rattrapage</h3>
          </div>
          <Table
            headers={[
              'Date originale',
              'Matière',
              'Date rattrapage',
              'Salle',
              'Enseignant',
              'Statut'
            ]}
            data={makeupSessions.map(session => ({
              id: session.id,
              date_originale: new Date(session.original_absence_date).toLocaleDateString('fr-FR'),
              matiere: session.subject_name,
              date_rattrapage: `${new Date(session.makeup_date).toLocaleDateString('fr-FR')} ${session.makeup_start_time}`,
              salle: session.room_name,
              enseignant: session.teacher_name,
              statut: (
                <span className={`px-2 py-1 rounded text-sm ${
                  getMakeupStatusColor(session.status)
                }`}>
                  {getMakeupStatusLabel(session.status)}
                </span>
              )
            }))}
          />
        </Card>
      )}

      {/* Modal création d'absence */}
      {showCreateAbsence && (
        <CreateAbsenceModal
          isOpen={showCreateAbsence}
          onClose={() => setShowCreateAbsence(false)}
          onCreated={loadAbsenceData}
        />
      )}

      {/* Modal détails absence */}
      {selectedAbsence && (
        <AbsenceDetailsModal
          absence={selectedAbsence}
          isOpen={!!selectedAbsence}
          onClose={() => setSelectedAbsence(null)}
          onUpdated={loadAbsenceData}
        />
      )}
    </div>
  );
};

const CreateAbsenceModal: React.FC<{
  isOpen: boolean;
  onClose: () => void;
  onCreated: () => void;
}> = ({ isOpen, onClose, onCreated }) => {
  const [loading, setLoading] = useState(false);
  const [schedules, setSchedules] = useState([]);

  const handleSubmit = async (data: any) => {
    try {
      setLoading(true);
      await enhancedAPI.absences.createAbsence(data);
      toast.success('Absence déclarée avec succès');
      onCreated();
      onClose();
    } catch (error) {
      console.error('Erreur création absence:', error);
      toast.error('Erreur lors de la déclaration');
    } finally {
      setLoading(false);
    }
  };

  return (
    <Modal isOpen={isOpen} onClose={onClose} title="Déclarer une absence">
      <Form
        onSubmit={handleSubmit}
        loading={loading}
        fields={[
          {
            name: 'schedule',
            label: 'Cours',
            type: 'select',
            required: true,
            options: schedules
          },
          {
            name: 'absence_type',
            label: 'Type d\'absence',
            type: 'select',
            required: true,
            options: [
              { value: 'medical', label: 'Médicale' },
              { value: 'family', label: 'Familiale' },
              { value: 'personal', label: 'Personnelle' },
              { value: 'transportation', label: 'Transport' },
              { value: 'other', label: 'Autre' }
            ]
          },
          {
            name: 'reason',
            label: 'Raison détaillée',
            type: 'textarea',
            required: true
          }
        ]}
        submitText="Déclarer l'absence"
      />
    </Modal>
  );
};

const AbsenceDetailsModal: React.FC<{
  absence: Absence;
  isOpen: boolean;
  onClose: () => void;
  onUpdated: () => void;
}> = ({ absence, isOpen, onClose, onUpdated }) => {
  const [uploading, setUploading] = useState(false);

  const handleUploadJustification = async (file: File) => {
    try {
      setUploading(true);
      await enhancedAPI.absences.uploadJustification(absence.id, file);
      toast.success('Document justificatif téléchargé');
      onUpdated();
    } catch (error) {
      console.error('Erreur upload:', error);
      toast.error('Erreur lors du téléchargement');
    } finally {
      setUploading(false);
    }
  };

  return (
    <Modal isOpen={isOpen} onClose={onClose} title="Détails de l'absence">
      <div className="space-y-4">
        {/* Informations de base */}
        <div className="grid grid-cols-2 gap-4">
          <div>
            <label className="text-sm font-medium text-gray-600">Date</label>
            <p>{new Date(absence.absence_date).toLocaleDateString('fr-FR')}</p>
          </div>
          <div>
            <label className="text-sm font-medium text-gray-600">Matière</label>
            <p>{absence.schedule_details.subject_name}</p>
          </div>
          <div>
            <label className="text-sm font-medium text-gray-600">Enseignant</label>
            <p>{absence.schedule_details.teacher_name}</p>
          </div>
          <div>
            <label className="text-sm font-medium text-gray-600">Salle</label>
            <p>{absence.schedule_details.room_name}</p>
          </div>
        </div>

        {/* Raison */}
        <div>
          <label className="text-sm font-medium text-gray-600">Raison</label>
          <p className="mt-1">{absence.reason}</p>
        </div>

        {/* Justification */}
        <div>
          <label className="text-sm font-medium text-gray-600">Document justificatif</label>
          {absence.justification_document_url ? (
            <div className="mt-1">
              <a 
                href={absence.justification_document_url}
                target="_blank"
                rel="noopener noreferrer"
                className="text-blue-600 hover:text-blue-800"
              >
                📄 Voir le document
              </a>
            </div>
          ) : (
            <div className="mt-1">
              <input
                type="file"
                accept=".pdf,.jpg,.jpeg,.png,.doc,.docx"
                onChange={(e) => {
                  const file = e.target.files?.[0];
                  if (file) handleUploadJustification(file);
                }}
                disabled={uploading}
                className="block w-full text-sm text-gray-500 file:mr-4 file:py-2 file:px-4 file:rounded-full file:border-0 file:text-sm file:font-semibold file:bg-blue-50 file:text-blue-700 hover:file:bg-blue-100"
              />
              {uploading && <p className="text-sm text-gray-500 mt-1">Téléchargement...</p>}
            </div>
          )}
        </div>

        {/* Alerte justification */}
        {absence.is_justification_overdue && (
          <div className="bg-red-50 p-3 rounded-lg border border-red-200">
            <p className="text-sm text-red-700">
              ⚠️ Délai de justification dépassé
            </p>
          </div>
        )}

        {/* Rattrapage */}
        {absence.can_request_makeup && (
          <div className="bg-blue-50 p-3 rounded-lg border border-blue-200">
            <p className="text-sm text-blue-700">
              💡 Vous pouvez demander un rattrapage pour cette absence
            </p>
          </div>
        )}
      </div>
    </Modal>
  );
};

// Fonctions utilitaires pour les couleurs et labels
const getAbsenceTypeColor = (type: string) => {
  const colors = {
    'unjustified': 'bg-red-100 text-red-800',
    'medical': 'bg-blue-100 text-blue-800',
    'family': 'bg-purple-100 text-purple-800',
    'personal': 'bg-yellow-100 text-yellow-800',
    'transportation': 'bg-orange-100 text-orange-800',
    'other': 'bg-gray-100 text-gray-800'
  };
  return colors[type as keyof typeof colors] || 'bg-gray-100 text-gray-800';
};

const getAbsenceTypeLabel = (type: string) => {
  const labels = {
    'unjustified': 'Non justifiée',
    'medical': 'Médicale',
    'family': 'Familiale',
    'personal': 'Personnelle',
    'transportation': 'Transport',
    'other': 'Autre'
  };
  return labels[type as keyof typeof labels] || type;
};

const getAbsenceStatusColor = (status: string) => {
  const colors = {
    'pending': 'bg-orange-100 text-orange-800',
    'approved': 'bg-green-100 text-green-800',
    'rejected': 'bg-red-100 text-red-800',
    'auto_approved': 'bg-blue-100 text-blue-800'
  };
  return colors[status as keyof typeof colors] || 'bg-gray-100 text-gray-800';
};

const getAbsenceStatusLabel = (status: string) => {
  const labels = {
    'pending': 'En attente',
    'approved': 'Approuvée',
    'rejected': 'Rejetée',
    'auto_approved': 'Auto-approuvée'
  };
  return labels[status as keyof typeof labels] || status;
};

const getMakeupStatusColor = (status: string) => {
  const colors = {
    'scheduled': 'bg-blue-100 text-blue-800',
    'confirmed': 'bg-green-100 text-green-800',
    'completed': 'bg-green-100 text-green-800',
    'cancelled': 'bg-red-100 text-red-800',
    'rescheduled': 'bg-orange-100 text-orange-800'
  };
  return colors[status as keyof typeof colors] || 'bg-gray-100 text-gray-800';
};

const getMakeupStatusLabel = (status: string) => {
  const labels = {
    'scheduled': 'Programmée',
    'confirmed': 'Confirmée',
    'completed': 'Terminée',
    'cancelled': 'Annulée',
    'rescheduled': 'Reprogrammée'
  };
  return labels[status as keyof typeof labels] || status;
};

export default AbsenceManagement;
