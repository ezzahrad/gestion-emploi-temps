import { api } from './api';

// ===== SERVICES POUR LES NOTES ET ÉVALUATIONS =====

export const gradesAPI = {
  // Échelles de notation
  getGradeScales: () => api.get('/grades/grade-scales/'),
  createGradeScale: (data: any) => api.post('/grades/grade-scales/', data),
  updateGradeScale: (id: number, data: any) => api.put(`/grades/grade-scales/${id}/`, data),

  // Évaluations
  getEvaluations: (params?: any) => api.get('/grades/evaluations/', { params }),
  createEvaluation: (data: any) => api.post('/grades/evaluations/', data),
  updateEvaluation: (id: number, data: any) => api.put(`/grades/evaluations/${id}/`, data),
  publishEvaluation: (id: number) => api.post(`/grades/evaluations/${id}/publish/`),
  getEvaluationStatistics: (id: number) => api.get(`/grades/evaluations/${id}/statistics/`),

  // Notes
  getGrades: (params?: any) => api.get('/grades/grades/', { params }),
  createGrade: (data: any) => api.post('/grades/grades/', data),
  updateGrade: (id: number, data: any) => api.put(`/grades/grades/${id}/`, data),
  publishGrade: (id: number) => api.post(`/grades/grades/${id}/publish/`),
  bulkCreateGrades: (data: any) => api.post('/grades/grades/bulk_create/', data),
  getMyGrades: () => api.get('/grades/grades/my_grades/'),

  // Résumés par matière
  getSubjectSummaries: (params?: any) => api.get('/grades/subject-summaries/', { params }),
  recalculateSummary: (id: number) => api.post(`/grades/subject-summaries/${id}/recalculate/`),
  validateSummary: (id: number) => api.post(`/grades/subject-summaries/${id}/validate/`),
  getMySummaries: () => api.get('/grades/subject-summaries/my_summaries/'),

  // Relevés de notes
  getTranscripts: (params?: any) => api.get('/grades/transcripts/', { params }),
  calculateGPA: (id: number) => api.post(`/grades/transcripts/${id}/calculate_gpa/`),
  finalizeTranscript: (id: number) => api.post(`/grades/transcripts/${id}/finalize/`),
  getMyTranscripts: () => api.get('/grades/transcripts/my_transcripts/'),
  getCurrentTranscript: () => api.get('/grades/transcripts/current_transcript/'),
};

// ===== SERVICES POUR LES ABSENCES =====

export const absencesAPI = {
  // Politiques d'absence
  getPolicies: () => api.get('/absences/policies/'),
  
  // Absences
  getAbsences: (params?: any) => api.get('/absences/absences/', { params }),
  createAbsence: (data: any) => api.post('/absences/absences/', data),
  updateAbsence: (id: number, data: any) => api.put(`/absences/absences/${id}/`, data),
  approveAbsence: (id: number) => api.post(`/absences/absences/${id}/approve/`),
  rejectAbsence: (id: number, comments?: string) => api.post(`/absences/absences/${id}/reject/`, { comments }),
  uploadJustification: (id: number, file: File) => {
    const formData = new FormData();
    formData.append('justification_document', file);
    return api.post(`/absences/absences/${id}/upload_justification/`, formData, {
      headers: { 'Content-Type': 'multipart/form-data' }
    });
  },
  getMyAbsences: () => api.get('/absences/absences/my_absences/'),
  getAbsenceStatistics: () => api.get('/absences/absences/statistics/'),

  // Sessions de rattrapage
  getMakeupSessions: (params?: any) => api.get('/absences/makeup-sessions/', { params }),
  createMakeupSession: (data: any) => api.post('/absences/makeup-sessions/', data),
  confirmMakeupSession: (id: number) => api.post(`/absences/makeup-sessions/${id}/confirm/`),
  completeMakeupSession: (id: number, data: any) => api.post(`/absences/makeup-sessions/${id}/complete/`, data),
  addMakeupFeedback: (id: number, feedback: string) => api.post(`/absences/makeup-sessions/${id}/add_feedback/`, { feedback }),
  getMySessions: () => api.get('/absences/makeup-sessions/my_sessions/'),

  // Présences
  getAttendanceRecords: (params?: any) => api.get('/absences/attendance/', { params }),
  createAttendanceRecord: (data: any) => api.post('/absences/attendance/', data),
  bulkCreateAttendance: (data: any) => api.post('/absences/attendance/bulk_create/', data),
  validateRecord: (id: number) => api.post(`/absences/attendance/${id}/validate_record/`),
  getAttendanceBySchedule: (scheduleId: number) => api.get('/absences/attendance/by_schedule/', { 
    params: { schedule_id: scheduleId }
  }),

  // Statistiques d'absences
  getAbsenceStatistics: (params?: any) => api.get('/absences/statistics/', { params }),
  recalculateStatistics: (id: number, data?: any) => api.post(`/absences/statistics/${id}/recalculate/`, data),
  getMyStatistics: () => api.get('/absences/statistics/my_statistics/'),
  getAtRiskStudents: () => api.get('/absences/statistics/at_risk_students/'),
  generateAbsenceReport: (data: any) => api.post('/absences/statistics/generate_report/', data),
};

// ===== SERVICES POUR L'EXPORT PDF =====

export const pdfExportAPI = {
  // Templates
  getTemplates: (params?: any) => api.get('/pdf-export/templates/', { params }),
  createTemplate: (data: any) => api.post('/pdf-export/templates/', data),
  updateTemplate: (id: number, data: any) => api.put(`/pdf-export/templates/${id}/`, data),
  setTemplateAsDefault: (id: number) => api.post(`/pdf-export/templates/${id}/set_as_default/`),
  getTemplatesByType: (type: string) => api.get('/pdf-export/templates/by_type/', { params: { type } }),

  // Jobs d'export
  getJobs: (params?: any) => api.get('/pdf-export/jobs/', { params }),
  getJobStatus: (jobId: string) => api.get('/pdf-export/jobs/status/', { params: { job_id: jobId } }),
  downloadPDF: (jobId: string) => api.get(`/pdf-export/jobs/${jobId}/download/`, { responseType: 'blob' }),
  cancelJob: (jobId: string) => api.post(`/pdf-export/jobs/${jobId}/cancel/`),
  getMyJobs: () => api.get('/pdf-export/jobs/my_jobs/'),

  // Création d'exports
  createExport: (data: any) => api.post('/pdf-export/export/create/', data),
  createBulkExport: (data: any) => api.post('/pdf-export/export/bulk/', data),
  getAvailableTypes: () => api.get('/pdf-export/export/types/'),

  // Paramètres et statistiques
  getSettings: () => api.get('/pdf-export/settings/'),
  updateSettings: (data: any) => api.put('/pdf-export/settings/1/', data),
  getStatistics: (params?: any) => api.get('/pdf-export/statistics/', { params }),
  getStatisticsSummary: () => api.get('/pdf-export/statistics/summary/'),
  getStatisticsTrends: (days?: number) => api.get('/pdf-export/statistics/trends/', { 
    params: { days }
  }),
};

// ===== SERVICES POUR LES NOTIFICATIONS AVANCÉES =====

export const notificationsEnhancedAPI = {
  // Notifications de base (étendues)
  getNotifications: (params?: any) => api.get('/notifications/', { params }),
  markAsRead: (id: number) => api.post(`/notifications/${id}/read/`),
  markAllAsRead: () => api.post('/notifications/mark-all-read/'),
  getUnreadCount: () => api.get('/notifications/unread-count/'),
  deleteNotification: (id: number) => api.delete(`/notifications/${id}/`),
  
  // Nouvelles fonctionnalités
  respondToNotification: (id: number, response: any) => api.post(`/notifications/${id}/respond/`, response),
  getNotificationsByThread: (threadId: string) => api.get('/notifications/by_thread/', { 
    params: { thread_id: threadId }
  }),
  getNotificationsByCategory: (category: string) => api.get('/notifications/by_category/', { 
    params: { category }
  }),

  // Paramètres utilisateur
  getMySettings: () => api.get('/notifications/settings/'),
  updateMySettings: (data: any) => api.put('/notifications/settings/', data),
  testNotification: (channel: string) => api.post('/notifications/test/', { channel }),

  // Templates (admin)
  getTemplates: () => api.get('/notifications/templates/'),
  createTemplate: (data: any) => api.post('/notifications/templates/', data),
  updateTemplate: (id: number, data: any) => api.put(`/notifications/templates/${id}/`, data),

  // Groupes
  getGroups: () => api.get('/notifications/groups/'),
  createGroup: (data: any) => api.post('/notifications/groups/', data),
  getGroupRecipients: (id: number) => api.get(`/notifications/groups/${id}/recipients/`),

  // Envois en masse
  getBatches: () => api.get('/notifications/batches/'),
  createBatch: (data: any) => api.post('/notifications/batches/', data),
  sendBatch: (id: number) => api.post(`/notifications/batches/${id}/send/`),
  getBatchStatistics: (id: number) => api.get(`/notifications/batches/${id}/statistics/`),

  // Analytics
  getDeliveryLogs: (params?: any) => api.get('/notifications/delivery-logs/', { params }),
  getNotificationAnalytics: (params?: any) => api.get('/notifications/analytics/', { params }),
};

// ===== SERVICES UTILITAIRES =====

export const enhancedUtilsAPI = {
  // Recherche globale enrichie
  globalSearch: (query: string, filters?: any) => api.get('/core/search/', { 
    params: { q: query, ...filters }
  }),

  // Statistiques avancées du dashboard
  getAdvancedDashboardStats: (params?: any) => api.get('/core/dashboard/advanced-stats/', { params }),
  
  // Export de données
  exportData: (type: string, params?: any) => api.get(`/core/export/${type}/`, { 
    params, 
    responseType: 'blob' 
  }),

  // Synchronisation et cache
  syncData: () => api.post('/core/sync/'),
  clearCache: (key?: string) => api.post('/core/cache/clear/', { key }),

  // Logs et audit
  getAuditLogs: (params?: any) => api.get('/core/audit-logs/', { params }),
  
  // Configuration système
  getSystemConfig: () => api.get('/core/config/'),
  updateSystemConfig: (data: any) => api.put('/core/config/', data),
};

// ===== HELPER FUNCTIONS =====

export const pdfHelpers = {
  /**
   * Télécharger un PDF et le sauvegarder
   */
  downloadAndSavePDF: async (jobId: string, filename?: string) => {
    try {
      const response = await pdfExportAPI.downloadPDF(jobId);
      const blob = new Blob([response.data], { type: 'application/pdf' });
      const url = window.URL.createObjectURL(blob);
      
      const link = document.createElement('a');
      link.href = url;
      link.download = filename || `export_${new Date().getTime()}.pdf`;
      document.body.appendChild(link);
      link.click();
      
      document.body.removeChild(link);
      window.URL.revokeObjectURL(url);
      
      return true;
    } catch (error) {
      console.error('Erreur lors du téléchargement PDF:', error);
      return false;
    }
  },

  /**
   * Surveiller le statut d'un job PDF
   */
  pollJobStatus: async (jobId: string, onUpdate?: (status: any) => void, maxAttempts = 60) => {
    let attempts = 0;
    
    return new Promise((resolve, reject) => {
      const poll = async () => {
        try {
          const response = await pdfExportAPI.getJobStatus(jobId);
          const status = response.data;
          
          if (onUpdate) {
            onUpdate(status);
          }
          
          if (status.status === 'completed') {
            resolve(status);
          } else if (status.status === 'failed') {
            reject(new Error(status.error_message || 'Export failed'));
          } else if (attempts >= maxAttempts) {
            reject(new Error('Timeout: Export took too long'));
          } else {
            attempts++;
            setTimeout(poll, 2000); // Poll every 2 seconds
          }
        } catch (error) {
          reject(error);
        }
      };
      
      poll();
    });
  }
};

export const notificationHelpers = {
  /**
   * Formater le temps relatif pour les notifications
   */
  formatTimeAgo: (dateString: string) => {
    const date = new Date(dateString);
    const now = new Date();
    const diffInMinutes = Math.floor((now.getTime() - date.getTime()) / (1000 * 60));
    
    if (diffInMinutes < 1) return 'À l\'instant';
    if (diffInMinutes < 60) return `Il y a ${diffInMinutes} min`;
    
    const diffInHours = Math.floor(diffInMinutes / 60);
    if (diffInHours < 24) return `Il y a ${diffInHours}h`;
    
    const diffInDays = Math.floor(diffInHours / 24);
    if (diffInDays < 7) return `Il y a ${diffInDays}j`;
    
    return date.toLocaleDateString('fr-FR');
  },

  /**
   * Obtenir la couleur selon la priorité
   */
  getPriorityColor: (priority: string) => {
    const colors = {
      'low': 'text-gray-600',
      'medium': 'text-blue-600',
      'high': 'text-orange-600',
      'urgent': 'text-red-600',
      'critical': 'text-red-800'
    };
    return colors[priority as keyof typeof colors] || 'text-gray-600';
  },

  /**
   * Obtenir l'icône selon le type de notification
   */
  getNotificationIcon: (type: string) => {
    const icons = {
      'schedule_change': '📅',
      'absence': '🏥',
      'makeup': '🔄',
      'grade': '📊',
      'evaluation': '📝',
      'pdf_export': '📄',
      'system': '⚙️',
      'reminder': '⏰',
      'admin_alert': '🚨'
    };
    return icons[type as keyof typeof icons] || '📢';
  }
};

// Export par défaut des APIs principales
export default {
  grades: gradesAPI,
  absences: absencesAPI,
  pdfExport: pdfExportAPI,
  notifications: notificationsEnhancedAPI,
  utils: enhancedUtilsAPI,
  helpers: {
    pdf: pdfHelpers,
    notifications: notificationHelpers
  }
};
