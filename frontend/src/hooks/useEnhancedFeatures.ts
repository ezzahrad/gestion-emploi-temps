import { useState, useEffect, useCallback } from 'react';
import { toast } from 'react-hot-toast';
import enhancedAPI from '../services/enhancedAPI';
import { 
  Grade, 
  Absence, 
  PDFExportJob, 
  NotificationEnhanced,
  StudentStats,
  SubjectGradeSummary 
} from '../types/enhanced';

// Hook pour la gestion des notes
export const useGrades = (studentId?: number, isCurrentUser = false) => {
  const [grades, setGrades] = useState<Grade[]>([]);
  const [summaries, setSummaries] = useState<SubjectGradeSummary[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  const loadGrades = useCallback(async () => {
    try {
      setLoading(true);
      setError(null);
      
      let gradesResponse, summariesResponse;
      
      if (isCurrentUser) {
        [gradesResponse, summariesResponse] = await Promise.all([
          enhancedAPI.grades.getMyGrades(),
          enhancedAPI.grades.getMySummaries()
        ]);
      } else {
        [gradesResponse, summariesResponse] = await Promise.all([
          enhancedAPI.grades.getGrades({ student: studentId }),
          enhancedAPI.grades.getSubjectSummaries({ student: studentId })
        ]);
      }
      
      setGrades(gradesResponse.data);
      setSummaries(summariesResponse.data);
    } catch (err) {
      setError('Erreur lors du chargement des notes');
      console.error('Erreur chargement notes:', err);
    } finally {
      setLoading(false);
    }
  }, [studentId, isCurrentUser]);

  useEffect(() => {
    loadGrades();
  }, [loadGrades]);

  const exportTranscript = async (options: any = {}) => {
    try {
      const exportData = {
        export_type: 'transcript',
        student_id: studentId,
        include_details: true,
        format: 'A4',
        ...options
      };

      const response = await enhancedAPI.pdfExport.createExport(exportData);
      toast.success('Export du relevé de notes lancé !');
      
      return response.data.job_id;
    } catch (error) {
      console.error('Erreur export transcript:', error);
      toast.error('Erreur lors de l\'export PDF');
      throw error;
    }
  };

  return {
    grades,
    summaries,
    loading,
    error,
    refetch: loadGrades,
    exportTranscript
  };
};

// Hook pour la gestion des absences
export const useAbsences = (studentId?: number, isCurrentUser = false) => {
  const [absences, setAbsences] = useState<Absence[]>([]);
  const [statistics, setStatistics] = useState<any>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  const loadAbsences = useCallback(async () => {
    try {
      setLoading(true);
      setError(null);
      
      let absencesResponse, statsResponse;
      
      if (isCurrentUser) {
        [absencesResponse, statsResponse] = await Promise.all([
          enhancedAPI.absences.getMyAbsences(),
          enhancedAPI.absences.getMyStatistics()
        ]);
      } else {
        [absencesResponse, statsResponse] = await Promise.all([
          enhancedAPI.absences.getAbsences({ student: studentId }),
          enhancedAPI.absences.getAbsenceStatistics({ student: studentId })
        ]);
      }
      
      setAbsences(absencesResponse.data);
      setStatistics(statsResponse.data);
    } catch (err) {
      setError('Erreur lors du chargement des absences');
      console.error('Erreur chargement absences:', err);
    } finally {
      setLoading(false);
    }
  }, [studentId, isCurrentUser]);

  useEffect(() => {
    loadAbsences();
  }, [loadAbsences]);

  const createAbsence = async (absenceData: any) => {
    try {
      await enhancedAPI.absences.createAbsence(absenceData);
      toast.success('Absence déclarée avec succès');
      loadAbsences(); // Recharger les données
    } catch (error) {
      console.error('Erreur création absence:', error);
      toast.error('Erreur lors de la déclaration');
      throw error;
    }
  };

  const uploadJustification = async (absenceId: number, file: File) => {
    try {
      await enhancedAPI.absences.uploadJustification(absenceId, file);
      toast.success('Document justificatif téléchargé');
      loadAbsences(); // Recharger les données
    } catch (error) {
      console.error('Erreur upload justification:', error);
      toast.error('Erreur lors du téléchargement');
      throw error;
    }
  };

  const exportAbsenceReport = async (options: any = {}) => {
    try {
      const exportData = {
        export_type: 'absence_report',
        student_id: studentId,
        start_date: new Date(Date.now() - 90 * 24 * 60 * 60 * 1000).toISOString().split('T')[0],
        end_date: new Date().toISOString().split('T')[0],
        include_statistics: true,
        ...options
      };

      const response = await enhancedAPI.pdfExport.createExport(exportData);
      toast.success('Export du rapport d\'absences lancé !');
      
      return response.data.job_id;
    } catch (error) {
      console.error('Erreur export rapport:', error);
      toast.error('Erreur lors de l\'export PDF');
      throw error;
    }
  };

  return {
    absences,
    statistics,
    loading,
    error,
    refetch: loadAbsences,
    createAbsence,
    uploadJustification,
    exportAbsenceReport
  };
};

// Hook pour la gestion des exports PDF
export const usePDFExports = () => {
  const [jobs, setJobs] = useState<PDFExportJob[]>([]);
  const [availableTypes, setAvailableTypes] = useState<any[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  const loadExports = useCallback(async () => {
    try {
      setLoading(true);
      setError(null);
      
      const [jobsResponse, typesResponse] = await Promise.all([
        enhancedAPI.pdfExport.getMyJobs(),
        enhancedAPI.pdfExport.getAvailableTypes()
      ]);
      
      setJobs(jobsResponse.data);
      setAvailableTypes(typesResponse.data);
    } catch (err) {
      setError('Erreur lors du chargement des exports');
      console.error('Erreur chargement exports:', err);
    } finally {
      setLoading(false);
    }
  }, []);

  useEffect(() => {
    loadExports();
  }, [loadExports]);

  const createExport = async (exportData: any) => {
    try {
      const response = await enhancedAPI.pdfExport.createExport(exportData);
      toast.success('Export lancé avec succès !');
      
      // Commencer à surveiller le statut
      const jobId = response.data.job_id;
      pollJobStatus(jobId);
      
      loadExports(); // Recharger la liste
      return jobId;
    } catch (error) {
      console.error('Erreur création export:', error);
      toast.error('Erreur lors de la création de l\'export');
      throw error;
    }
  };

  const pollJobStatus = async (jobId: string) => {
    try {
      await enhancedAPI.helpers.pdf.pollJobStatus(
        jobId,
        (status) => {
          // Mettre à jour le job dans la liste
          setJobs(prevJobs => 
            prevJobs.map(job => 
              job.job_id === jobId ? { ...job, ...status } : job
            )
          );
          
          if (status.status === 'completed') {
            toast.success('Export terminé !');
          } else if (status.status === 'failed') {
            toast.error('Export échoué');
          }
        }
      );
    } catch (error) {
      console.error('Erreur polling status:', error);
    }
  };

  const downloadPDF = async (job: PDFExportJob) => {
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

  const cancelJob = async (jobId: string) => {
    try {
      await enhancedAPI.pdfExport.cancelJob(jobId);
      toast.success('Export annulé');
      loadExports();
    } catch (error) {
      console.error('Erreur annulation:', error);
      toast.error('Erreur lors de l\'annulation');
    }
  };

  return {
    jobs,
    availableTypes,
    loading,
    error,
    refetch: loadExports,
    createExport,
    downloadPDF,
    cancelJob,
    pollJobStatus
  };
};

// Hook pour la gestion des notifications
export const useNotifications = (maxItems = 50) => {
  const [notifications, setNotifications] = useState<NotificationEnhanced[]>([]);
  const [unreadCount, setUnreadCount] = useState(0);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  const loadNotifications = useCallback(async (filters: any = {}) => {
    try {
      setLoading(true);
      setError(null);
      
      const params = {
        limit: maxItems,
        ...filters
      };
      
      const [notificationsResponse, countResponse] = await Promise.all([
        enhancedAPI.notifications.getNotifications(params),
        enhancedAPI.notifications.getUnreadCount()
      ]);
      
      setNotifications(notificationsResponse.data);
      setUnreadCount(countResponse.data.count);
    } catch (err) {
      setError('Erreur lors du chargement des notifications');
      console.error('Erreur chargement notifications:', err);
    } finally {
      setLoading(false);
    }
  }, [maxItems]);

  useEffect(() => {
    loadNotifications();
  }, [loadNotifications]);

  const markAsRead = async (id: number) => {
    try {
      await enhancedAPI.notifications.markAsRead(id);
      setNotifications(prev => 
        prev.map(notif => 
          notif.id === id ? { ...notif, is_read: true } : notif
        )
      );
      setUnreadCount(prev => Math.max(0, prev - 1));
    } catch (error) {
      console.error('Erreur marquage lu:', error);
      toast.error('Erreur lors du marquage');
    }
  };

  const markAllAsRead = async () => {
    try {
      await enhancedAPI.notifications.markAllAsRead();
      setNotifications(prev => 
        prev.map(notif => ({ ...notif, is_read: true }))
      );
      setUnreadCount(0);
      toast.success('Toutes les notifications marquées comme lues');
    } catch (error) {
      console.error('Erreur marquage toutes lues:', error);
      toast.error('Erreur lors du marquage');
    }
  };

  const deleteNotification = async (id: number) => {
    try {
      await enhancedAPI.notifications.deleteNotification(id);
      setNotifications(prev => prev.filter(notif => notif.id !== id));
      toast.success('Notification supprimée');
    } catch (error) {
      console.error('Erreur suppression:', error);
      toast.error('Erreur lors de la suppression');
    }
  };

  return {
    notifications,
    unreadCount,
    loading,
    error,
    refetch: loadNotifications,
    markAsRead,
    markAllAsRead,
    deleteNotification
  };
};

// Hook pour les statistiques étudiants
export const useStudentStats = (studentId?: number) => {
  const [stats, setStats] = useState<StudentStats | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  const loadStats = useCallback(async () => {
    try {
      setLoading(true);
      setError(null);
      
      // Pour l'instant, simuler les données
      // En production, cela viendrait d'une API dédiée
      const mockStats: StudentStats = {
        total_absences: Math.floor(Math.random() * 10),
        justified_absences: Math.floor(Math.random() * 5),
        unjustified_absences: Math.floor(Math.random() * 3),
        absence_rate: Math.random() * 15,
        pending_makeups: Math.floor(Math.random() * 3),
        completed_makeups: Math.floor(Math.random() * 2),
        current_average: 10 + Math.random() * 10,
        subjects_count: 6 + Math.floor(Math.random() * 4),
        credits_acquired: 15 + Math.floor(Math.random() * 15),
        credits_total: 30,
        attendance_rate: 85 + Math.random() * 15,
        grade_trend: ['improving', 'stable', 'declining'][Math.floor(Math.random() * 3)] as any
      };
      
      setStats(mockStats);
    } catch (err) {
      setError('Erreur lors du chargement des statistiques');
      console.error('Erreur chargement stats:', err);
    } finally {
      setLoading(false);
    }
  }, [studentId]);

  useEffect(() => {
    loadStats();
  }, [loadStats]);

  return {
    stats,
    loading,
    error,
    refetch: loadStats
  };
};

// Hook composé pour les données complètes d'un étudiant
export const useStudentData = (studentId?: number, isCurrentUser = false) => {
  const grades = useGrades(studentId, isCurrentUser);
  const absences = useAbsences(studentId, isCurrentUser);
  const stats = useStudentStats(studentId);
  const notifications = useNotifications(10); // Limitées pour l'aperçu

  const loading = grades.loading || absences.loading || stats.loading;
  const error = grades.error || absences.error || stats.error;

  const refetchAll = () => {
    grades.refetch();
    absences.refetch();
    stats.refetch();
    notifications.refetch();
  };

  return {
    grades: grades.grades,
    summaries: grades.summaries,
    absences: absences.absences,
    absenceStatistics: absences.statistics,
    stats: stats.stats,
    notifications: notifications.notifications,
    unreadCount: notifications.unreadCount,
    loading,
    error,
    refetchAll,
    actions: {
      exportTranscript: grades.exportTranscript,
      exportAbsenceReport: absences.exportAbsenceReport,
      createAbsence: absences.createAbsence,
      uploadJustification: absences.uploadJustification,
      markNotificationRead: notifications.markAsRead,
      markAllNotificationsRead: notifications.markAllAsRead
    }
  };
};
