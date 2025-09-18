import React, { useState, useEffect } from 'react';
import { Card, Button, Modal, Form, Loading, Table } from '../ui';
import { 
  FileText, Download, Settings, Clock, CheckCircle, 
  AlertCircle, Trash2, Eye, RefreshCw 
} from 'lucide-react';
import { toast } from 'react-hot-toast';
import enhancedAPI from '../../services/enhancedAPI';
import { PDFExportJob, PDFTemplate } from '../../types';

interface PDFExportCenterProps {
  userRole?: string;
}

export const PDFExportCenter: React.FC<PDFExportCenterProps> = ({ userRole }) => {
  const [jobs, setJobs] = useState<PDFExportJob[]>([]);
  const [availableTypes, setAvailableTypes] = useState<any[]>([]);
  const [templates, setTemplates] = useState<PDFTemplate[]>([]);
  const [loading, setLoading] = useState(true);
  const [showCreateExport, setShowCreateExport] = useState(false);
  const [selectedJob, setSelectedJob] = useState<PDFExportJob | null>(null);

  useEffect(() => {
    loadExportData();
  }, []);

  const loadExportData = async () => {
    try {
      setLoading(true);
      const [jobsRes, typesRes, templatesRes] = await Promise.all([
        enhancedAPI.pdfExport.getMyJobs(),
        enhancedAPI.pdfExport.getAvailableTypes(),
        enhancedAPI.pdfExport.getTemplates()
      ]);
      
      setJobs(jobsRes.data);
      setAvailableTypes(typesRes.data);
      setTemplates(templatesRes.data);
    } catch (error) {
      console.error('Erreur lors du chargement:', error);
      toast.error('Erreur lors du chargement des données');
    } finally {
      setLoading(false);
    }
  };

  const handleDownload = async (job: PDFExportJob) => {
    try {
      const success = await enhancedAPI.helpers.pdf.downloadAndSavePDF(
        job.job_id,
        `${job.export_type}_${new Date(job.created_at).getTime()}.pdf`
      );
      
      if (success) {
        toast.success('Téléchargement démarré !');
      } else {
        toast.error('Erreur lors du téléchargement');
      }
    } catch (error) {
      console.error('Erreur téléchargement:', error);
      toast.error('Erreur lors du téléchargement');
    }
  };

  const handleCancelJob = async (jobId: string) => {
    try {
      await enhancedAPI.pdfExport.cancelJob(jobId);
      toast.success('Export annulé');
      loadExportData();
    } catch (error) {
      console.error('Erreur annulation:', error);
      toast.error('Erreur lors de l\'annulation');
    }
  };

  const refreshJobStatus = async (jobId: string) => {
    try {
      const response = await enhancedAPI.pdfExport.getJobStatus(jobId);
      const updatedJob = response.data;
      
      setJobs(prevJobs => 
        prevJobs.map(job => 
          job.job_id === jobId ? { ...job, ...updatedJob } : job
        )
      );
      
      if (updatedJob.status === 'completed') {
        toast.success('Export terminé !');
      } else if (updatedJob.status === 'failed') {
        toast.error('Export échoué');
      }
    } catch (error) {
      console.error('Erreur refresh:', error);
    }
  };

  if (loading) {
    return <Loading message="Chargement du centre d'export..." />;
  }

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex justify-between items-center">
        <div>
          <h1 className="text-2xl font-bold text-gray-900">Centre d'Export PDF</h1>
          <p className="text-gray-600">Générez et téléchargez vos documents PDF</p>
        </div>
        <Button
          onClick={() => setShowCreateExport(true)}
          className="bg-blue-600 hover:bg-blue-700"
        >
          <FileText className="w-4 h-4 mr-2" />
          Nouvel export
        </Button>
      </div>

      {/* Raccourcis rapides */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
        {availableTypes.slice(0, 4).map((type) => (
          <Card key={type.value} className="p-4 hover:shadow-md transition-shadow cursor-pointer">
            <div className="flex items-center justify-between">
              <div>
                <h3 className="font-medium text-gray-900">{type.label}</h3>
                <p className="text-sm text-gray-500 mt-1">Export rapide</p>
              </div>
              <FileText className="w-8 h-8 text-blue-500" />
            </div>
          </Card>
        ))}
      </div>

      {/* Jobs en cours */}
      <Card>
        <div className="p-4 border-b flex justify-between items-center">
          <h2 className="text-lg font-medium">Mes exports</h2>
          <Button
            size="sm"
            variant="outline"
            onClick={loadExportData}
          >
            <RefreshCw className="w-4 h-4 mr-1" />
            Actualiser
          </Button>
        </div>
        
        {jobs.length === 0 ? (
          <div className="p-8 text-center text-gray-500">
            <FileText className="w-12 h-12 mx-auto mb-4 text-gray-300" />
            <p>Aucun export pour le moment</p>
            <p className="text-sm mt-1">Créez votre premier export PDF !</p>
          </div>
        ) : (
          <Table
            headers={[
              'Type',
              'Date de création',
              'Statut',
              'Progression',
              'Taille',
              'Actions'
            ]}
            data={jobs.map(job => ({
              id: job.job_id,
              type: getExportTypeLabel(job.export_type),
              date: new Date(job.created_at).toLocaleDateString('fr-FR', {
                day: '2-digit',
                month: '2-digit',
                year: 'numeric',
                hour: '2-digit',
                minute: '2-digit'
              }),
              statut: <JobStatusBadge job={job} />,
              progression: <ProgressBar job={job} />,
              taille: job.file_size_display || '-',
              actions: <JobActions 
                job={job} 
                onDownload={() => handleDownload(job)}
                onCancel={() => handleCancelJob(job.job_id)}
                onRefresh={() => refreshJobStatus(job.job_id)}
                onDetails={() => setSelectedJob(job)}
              />
            }))}
          />
        )}
      </Card>

      {/* Modal création d'export */}
      {showCreateExport && (
        <CreateExportModal
          isOpen={showCreateExport}
          onClose={() => setShowCreateExport(false)}
          availableTypes={availableTypes}
          templates={templates}
          onCreated={loadExportData}
        />
      )}

      {/* Modal détails job */}
      {selectedJob && (
        <JobDetailsModal
          job={selectedJob}
          isOpen={!!selectedJob}
          onClose={() => setSelectedJob(null)}
        />
      )}
    </div>
  );
};

const JobStatusBadge: React.FC<{ job: PDFExportJob }> = ({ job }) => {
  const getStatusConfig = (status: string) => {
    switch (status) {
      case 'pending':
        return { color: 'bg-yellow-100 text-yellow-800', icon: Clock, label: 'En attente' };
      case 'processing':
        return { color: 'bg-blue-100 text-blue-800', icon: RefreshCw, label: 'En cours' };
      case 'completed':
        return { color: 'bg-green-100 text-green-800', icon: CheckCircle, label: 'Terminé' };
      case 'failed':
        return { color: 'bg-red-100 text-red-800', icon: AlertCircle, label: 'Échec' };
      case 'cancelled':
        return { color: 'bg-gray-100 text-gray-800', icon: AlertCircle, label: 'Annulé' };
      default:
        return { color: 'bg-gray-100 text-gray-800', icon: Clock, label: status };
    }
  };

  const config = getStatusConfig(job.status);
  const Icon = config.icon;

  return (
    <span className={`inline-flex items-center px-2 py-1 rounded-full text-xs font-medium ${config.color}`}>
      <Icon className="w-3 h-3 mr-1" />
      {config.label}
    </span>
  );
};

const ProgressBar: React.FC<{ job: PDFExportJob }> = ({ job }) => {
  if (job.status === 'completed') {
    return <span className="text-green-600 font-medium">100%</span>;
  }

  if (job.status === 'failed' || job.status === 'cancelled') {
    return <span className="text-gray-400">-</span>;
  }

  return (
    <div className="w-full bg-gray-200 rounded-full h-2">
      <div 
        className="bg-blue-600 h-2 rounded-full transition-all duration-300"
        style={{ width: `${job.progress}%` }}
      />
      <span className="text-xs text-gray-600 ml-2">{job.progress}%</span>
    </div>
  );
};

const JobActions: React.FC<{
  job: PDFExportJob;
  onDownload: () => void;
  onCancel: () => void;
  onRefresh: () => void;
  onDetails: () => void;
}> = ({ job, onDownload, onCancel, onRefresh, onDetails }) => {
  return (
    <div className="flex items-center space-x-1">
      {job.status === 'completed' && (
        <Button
          size="sm"
          variant="outline"
          onClick={onDownload}
          title="Télécharger"
        >
          <Download className="w-4 h-4" />
        </Button>
      )}
      
      {(job.status === 'pending' || job.status === 'processing') && (
        <>
          <Button
            size="sm"
            variant="outline"
            onClick={onRefresh}
            title="Actualiser"
          >
            <RefreshCw className="w-4 h-4" />
          </Button>
          <Button
            size="sm"
            variant="outline"
            onClick={onCancel}
            title="Annuler"
            className="text-red-600 hover:text-red-700"
          >
            <Trash2 className="w-4 h-4" />
          </Button>
        </>
      )}
      
      <Button
        size="sm"
        variant="outline"
        onClick={onDetails}
        title="Détails"
      >
        <Eye className="w-4 h-4" />
      </Button>
    </div>
  );
};

const CreateExportModal: React.FC<{
  isOpen: boolean;
  onClose: () => void;
  availableTypes: any[];
  templates: PDFTemplate[];
  onCreated: () => void;
}> = ({ isOpen, onClose, availableTypes, templates, onCreated }) => {
  const [loading, setLoading] = useState(false);
  const [selectedType, setSelectedType] = useState('');

  const handleSubmit = async (data: any) => {
    try {
      setLoading(true);
      const response = await enhancedAPI.pdfExport.createExport(data);
      
      toast.success('Export lancé avec succès !');
      
      // Commencer à surveiller le statut
      enhancedAPI.helpers.pdf.pollJobStatus(
        response.data.job_id,
        (status) => {
          if (status.status === 'completed') {
            toast.success('Export terminé !');
            onCreated();
          } else if (status.status === 'failed') {
            toast.error('Export échoué');
          }
        }
      ).catch(console.error);
      
      onCreated();
      onClose();
    } catch (error) {
      console.error('Erreur création export:', error);
      toast.error('Erreur lors de la création de l\'export');
    } finally {
      setLoading(false);
    }
  };

  const getFormFields = () => {
    const baseFields = [
      {
        name: 'export_type',
        label: 'Type d\'export',
        type: 'select' as const,
        required: true,
        options: availableTypes,
        onChange: (value: string) => setSelectedType(value)
      },
      {
        name: 'format',
        label: 'Format de page',
        type: 'select' as const,
        options: [
          { value: 'A4', label: 'A4' },
          { value: 'A3', label: 'A3' },
          { value: 'Letter', label: 'Letter' }
        ],
        defaultValue: 'A4'
      },
      {
        name: 'orientation',
        label: 'Orientation',
        type: 'select' as const,
        options: [
          { value: 'portrait', label: 'Portrait' },
          { value: 'landscape', label: 'Paysage' }
        ],
        defaultValue: 'portrait'
      }
    ];

    // Ajouter des champs selon le type
    if (selectedType === 'schedule' || selectedType === 'transcript' || selectedType === 'absence_report') {
      baseFields.push({
        name: 'include_details',
        label: 'Inclure les détails',
        type: 'checkbox' as const,
        defaultValue: true
      });
    }

    if (selectedType === 'schedule' || selectedType === 'absence_report') {
      baseFields.push(
        {
          name: 'start_date',
          label: 'Date de début',
          type: 'date' as const
        },
        {
          name: 'end_date',
          label: 'Date de fin',
          type: 'date' as const
        }
      );
    }

    return baseFields;
  };

  return (
    <Modal isOpen={isOpen} onClose={onClose} title="Créer un export PDF">
      <Form
        onSubmit={handleSubmit}
        loading={loading}
        fields={getFormFields()}
        submitText="Lancer l'export"
      />
    </Modal>
  );
};

const JobDetailsModal: React.FC<{
  job: PDFExportJob;
  isOpen: boolean;
  onClose: () => void;
}> = ({ job, isOpen, onClose }) => {
  return (
    <Modal isOpen={isOpen} onClose={onClose} title="Détails de l'export">
      <div className="space-y-4">
        <div className="grid grid-cols-2 gap-4">
          <div>
            <label className="text-sm font-medium text-gray-600">Type d'export</label>
            <p>{getExportTypeLabel(job.export_type)}</p>
          </div>
          <div>
            <label className="text-sm font-medium text-gray-600">Statut</label>
            <div className="mt-1">
              <JobStatusBadge job={job} />
            </div>
          </div>
          <div>
            <label className="text-sm font-medium text-gray-600">Progression</label>
            <ProgressBar job={job} />
          </div>
          <div>
            <label className="text-sm font-medium text-gray-600">Taille du fichier</label>
            <p>{job.file_size_display || 'N/A'}</p>
          </div>
          <div>
            <label className="text-sm font-medium text-gray-600">Nombre de pages</label>
            <p>{job.page_count || 'N/A'}</p>
          </div>
          <div>
            <label className="text-sm font-medium text-gray-600">Créé le</label>
            <p>{new Date(job.created_at).toLocaleString('fr-FR')}</p>
          </div>
        </div>

        {job.processing_time && (
          <div>
            <label className="text-sm font-medium text-gray-600">Temps de traitement</label>
            <p>{job.processing_time.toFixed(1)} secondes</p>
          </div>
        )}

        {job.error_message && (
          <div>
            <label className="text-sm font-medium text-gray-600">Message d'erreur</label>
            <div className="mt-1 p-3 bg-red-50 border border-red-200 rounded">
              <p className="text-sm text-red-700">{job.error_message}</p>
            </div>
          </div>
        )}

        {job.success_message && (
          <div>
            <label className="text-sm font-medium text-gray-600">Message de succès</label>
            <div className="mt-1 p-3 bg-green-50 border border-green-200 rounded">
              <p className="text-sm text-green-700">{job.success_message}</p>
            </div>
          </div>
        )}

        {job.download_url && (
          <div className="pt-4 border-t">
            <Button
              onClick={() => enhancedAPI.helpers.pdf.downloadAndSavePDF(job.job_id)}
              className="w-full bg-green-600 hover:bg-green-700"
            >
              <Download className="w-4 h-4 mr-2" />
              Télécharger le PDF
            </Button>
          </div>
        )}
      </div>
    </Modal>
  );
};

// Fonction utilitaire pour les labels des types d'export
const getExportTypeLabel = (type: string) => {
  const labels = {
    'schedule': 'Emploi du temps',
    'transcript': 'Relevé de notes',
    'absence_report': 'Rapport d\'absences',
    'attendance_report': 'Rapport de présences',
    'teacher_schedule': 'Planning enseignant',
    'room_schedule': 'Planning salle',
    'bulk_schedules': 'Emplois du temps en masse',
    'bulk_transcripts': 'Relevés en masse'
  };
  return labels[type as keyof typeof labels] || type;
};

export default PDFExportCenter;
