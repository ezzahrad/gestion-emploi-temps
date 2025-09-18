import axios from "axios";

// Align base URL and storage keys with AuthContext
const API_BASE_URL = (import.meta as any).env?.VITE_API_URL
  ? `${(import.meta as any).env.VITE_API_URL}/api`
  : "http://127.0.0.1:8000/api";
const TOKEN_STORAGE_KEY = "appget_token";
const USER_STORAGE_KEY = "appget_user";

// Create axios instance
export const api = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    "Content-Type": "application/json",
  },
});

// Compute the correct login URL on the frontend app
const getFrontendLoginUrl = (): string => {
  const explicitAppUrl = (import.meta as any).env?.VITE_APP_URL as
    | string
    | undefined;
  if (explicitAppUrl) return `${explicitAppUrl.replace(/\/$/, "")}/login`;
  // If currently on backend host:8000, force dev frontend port 3001
  const isBackendHost =
    window.location.port === "8000" || window.location.hostname === "127.0.0.1";
  if (isBackendHost) return "http://localhost:3001/login";
  // Otherwise use same origin
  return "/login";
};

// Add token to requests
api.interceptors.request.use(
  (config) => {
    const token = localStorage.getItem(TOKEN_STORAGE_KEY);
    if (token) {
      config.headers.Authorization = `Bearer ${token}`;
    }
    return config;
  },
  (error) => {
    return Promise.reject(error);
  }
);

// Handle auth errors
api.interceptors.response.use(
  (response) => response,
  (error) => {
    if (error.response?.status === 401) {
      localStorage.removeItem(TOKEN_STORAGE_KEY);
      localStorage.removeItem(USER_STORAGE_KEY);
      window.location.href = getFrontendLoginUrl();
    }
    return Promise.reject(error);
  }
);

// Authentication API
export const authAPI = {
  login: (credentials: { email: string; password: string }) =>
    api.post("/auth/login/", credentials),

  register: (userData: any) => api.post("/auth/register/", userData),

  getProfile: () => api.get("/auth/profile/"),

  updateProfile: (userData: any) => api.put("/auth/profile/update/", userData),
};

// Core API
export const coreAPI = {
  // Dashboard
  getDashboardStats: () => api.get("/core/dashboard/stats/"),

  // Departments
  getDepartments: (params?: any) => api.get("/core/departments/", { params }),

  createDepartment: (data: any) => api.post("/core/departments/", data),

  updateDepartment: (id: number, data: any) =>
    api.put(`/core/departments/${id}/`, data),

  deleteDepartment: (id: number) => api.delete(`/core/departments/${id}/`),

  // Programs
  getPrograms: (params?: any) => api.get("/core/programs/", { params }),

  createProgram: (data: any) => api.post("/core/programs/", data),

  updateProgram: (id: number, data: any) =>
    api.put(`/core/programs/${id}/`, data),

  deleteProgram: (id: number) => api.delete(`/core/programs/${id}/`),

  // Rooms
  getRooms: (params?: any) => api.get("/core/rooms/", { params }),

  createRoom: (data: any) => api.post("/core/rooms/", data),

  updateRoom: (id: number, data: any) => api.put(`/core/rooms/${id}/`, data),

  deleteRoom: (id: number) => api.delete(`/core/rooms/${id}/`),

  // Subjects
  getSubjects: (params?: any) => api.get("/core/subjects/", { params }),

  createSubject: (data: any) => api.post("/core/subjects/", data),

  updateSubject: (id: number, data: any) =>
    api.put(`/core/subjects/${id}/`, data),

  deleteSubject: (id: number) => api.delete(`/core/subjects/${id}/`),

  // Teachers
  getTeachers: (params?: any) => api.get("/core/teachers/", { params }),

  createTeacher: (data: any) => api.post("/core/teachers/", data),

  updateTeacher: (id: number, data: any) =>
    api.put(`/core/teachers/${id}/`, data),

  deleteTeacher: (id: number) => api.delete(`/core/teachers/${id}/`),

  // Students
  getStudents: (params?: any) => api.get("/core/students/", { params }),

  createStudent: (data: any) => api.post("/core/students/", data),

  updateStudent: (id: number, data: any) =>
    api.put(`/core/students/${id}/`, data),

  deleteStudent: (id: number) => api.delete(`/core/students/${id}/`),
};

// Schedule API
export const scheduleAPI = {
  getSchedules: (params?: any) => api.get("/schedule/schedules/", { params }),

  getScheduleByWeek: (params: any) =>
    api.get("/schedule/schedules/by-week/", { params }),

  createSchedule: (data: any) => api.post("/schedule/schedules/", data),

  updateSchedule: (id: number, data: any) =>
    api.put(`/schedule/schedules/${id}/`, data),

  deleteSchedule: (id: number) => api.delete(`/schedule/schedules/${id}/`),

  checkConflicts: (data: any) =>
    api.post("/schedule/schedules/check-conflicts/", data),

  getAvailableRooms: (params: any) =>
    api.get("/schedule/schedules/available-rooms/", { params }),

  // Absences
  getAbsences: (params?: any) => api.get("/schedule/absences/", { params }),

  createAbsence: (data: any) => api.post("/schedule/absences/", data),

  // Makeup sessions
  getMakeupSessions: (params?: any) =>
    api.get("/schedule/makeup-sessions/", { params }),

  createMakeupSession: (data: any) =>
    api.post("/schedule/makeup-sessions/", data),

  approveMakeup: (id: number, action: "approve" | "reject") =>
    api.post(`/schedule/makeup-sessions/${id}/approve/`, { action }),

  // AI Optimization
  getOptimizationStats: () => api.get("/schedule/optimization/stats/"),

  optimizeSchedules: (data: any) =>
    api.post("/schedule/optimization/optimize/", data),

  saveOptimizationConfig: (data: any) =>
    api.post("/schedule/optimization/config/", data),

  exportOptimizationResults: () =>
    api.get("/schedule/optimization/export/", { responseType: "blob" }),

  // Import/Export
  importSchedules: (formData: FormData) =>
    api.post("/schedule/import/", formData, {
      headers: { "Content-Type": "multipart/form-data" },
    }),

  downloadImportTemplate: () =>
    api.get("/schedule/import/template/", { responseType: "blob" }),

  exportSchedules: (params: any) =>
    api.get("/schedule/export/", { params, responseType: "blob" }),
};

// Notifications API
export const notificationsAPI = {
  getNotifications: () => api.get("/notifications/"),

  markAsRead: (id: number) => api.post(`/notifications/${id}/read/`),

  markAllAsRead: () => api.post("/notifications/mark-all-read/"),

  getUnreadCount: () => api.get("/notifications/unread-count/"),
};

// Grades API
export const gradesAPI = {
  // Grade Scales
  getGradeScales: () => api.get("/grades/grade-scales/"),
  
  // Evaluations
  getEvaluations: (params?: any) => api.get("/grades/evaluations/", { params }),
  createEvaluation: (data: any) => api.post("/grades/evaluations/", data),
  updateEvaluation: (id: number, data: any) => api.put(`/grades/evaluations/${id}/`, data),
  deleteEvaluation: (id: number) => api.delete(`/grades/evaluations/${id}/`),
  publishEvaluation: (id: number) => api.post(`/grades/evaluations/${id}/publish/`),
  getEvaluationStats: (id: number) => api.get(`/grades/evaluations/${id}/statistics/`),
  
  // Grades
  getGrades: (params?: any) => api.get("/grades/grades/", { params }),
  createGrade: (data: any) => api.post("/grades/grades/", data),
  updateGrade: (id: number, data: any) => api.put(`/grades/grades/${id}/`, data),
  deleteGrade: (id: number) => api.delete(`/grades/grades/${id}/`),
  bulkCreateGrades: (data: any) => api.post("/grades/grades/bulk_create/", data),
  publishGrade: (id: number) => api.post(`/grades/grades/${id}/publish/`),
  getMyGrades: () => api.get("/grades/grades/my_grades/"),
  
  // Subject Summaries
  getSubjectSummaries: (params?: any) => api.get("/grades/subject-summaries/", { params }),
  recalculateSummary: (id: number) => api.post(`/grades/subject-summaries/${id}/recalculate/`),
  validateSummary: (id: number) => api.post(`/grades/subject-summaries/${id}/validate/`),
  getMySummaries: () => api.get("/grades/subject-summaries/my_summaries/"),
  
  // Transcripts
  getTranscripts: (params?: any) => api.get("/grades/transcripts/", { params }),
  createTranscript: (data: any) => api.post("/grades/transcripts/", data),
  updateTranscript: (id: number, data: any) => api.put(`/grades/transcripts/${id}/`, data),
  calculateGPA: (id: number) => api.post(`/grades/transcripts/${id}/calculate_gpa/`),
  finalizeTranscript: (id: number) => api.post(`/grades/transcripts/${id}/finalize/`),
  getMyTranscripts: () => api.get("/grades/transcripts/my_transcripts/"),
  getCurrentTranscript: () => api.get("/grades/transcripts/current_transcript/"),
};

// Absences API
export const absencesAPI = {
  // Absence Policies
  getAbsencePolicies: () => api.get("/absences/policies/"),
  
  // Absences
  getAbsences: (params?: any) => api.get("/absences/absences/", { params }),
  createAbsence: (data: any) => api.post("/absences/absences/", data),
  updateAbsence: (id: number, data: any) => api.put(`/absences/absences/${id}/`, data),
  deleteAbsence: (id: number) => api.delete(`/absences/absences/${id}/`),
  approveAbsence: (id: number) => api.post(`/absences/absences/${id}/approve/`),
  rejectAbsence: (id: number, comments?: string) => api.post(`/absences/absences/${id}/reject/`, { comments }),
  uploadJustification: (id: number, file: File) => {
    const formData = new FormData();
    formData.append('justification_document', file);
    return api.post(`/absences/absences/${id}/upload_justification/`, formData, {
      headers: { 'Content-Type': 'multipart/form-data' }
    });
  },
  getMyAbsences: () => api.get("/absences/absences/my_absences/"),
  getAbsenceStatistics: () => api.get("/absences/absences/statistics/"),
  
  // Makeup Sessions
  getMakeupSessions: (params?: any) => api.get("/absences/makeup-sessions/", { params }),
  createMakeupSession: (data: any) => api.post("/absences/makeup-sessions/", data),
  updateMakeupSession: (id: number, data: any) => api.put(`/absences/makeup-sessions/${id}/`, data),
  confirmMakeupSession: (id: number) => api.post(`/absences/makeup-sessions/${id}/confirm/`),
  completeMakeupSession: (id: number, data: any) => api.post(`/absences/makeup-sessions/${id}/complete/`, data),
  addMakeupFeedback: (id: number, feedback: string) => api.post(`/absences/makeup-sessions/${id}/add_feedback/`, { feedback }),
  getMySessions: () => api.get("/absences/makeup-sessions/my_sessions/"),
  
  // Attendance Records
  getAttendanceRecords: (params?: any) => api.get("/absences/attendance/", { params }),
  createAttendanceRecord: (data: any) => api.post("/absences/attendance/", data),
  bulkCreateAttendance: (data: any) => api.post("/absences/attendance/bulk_create/", data),
  validateAttendanceRecord: (id: number) => api.post(`/absences/attendance/${id}/validate_record/`),
  getAttendanceBySchedule: (scheduleId: number) => api.get("/absences/attendance/by_schedule/", { params: { schedule_id: scheduleId } }),
  
  // Student Statistics
  getAbsenceStatistics: (params?: any) => api.get("/absences/statistics/", { params }),
  recalculateStatistics: (id: number, startDate?: string, endDate?: string) => api.post(`/absences/statistics/${id}/recalculate/`, { start_date: startDate, end_date: endDate }),
  getMyStatistics: () => api.get("/absences/statistics/my_statistics/"),
  getAtRiskStudents: () => api.get("/absences/statistics/at_risk_students/"),
  generateAbsenceReport: (data: any) => api.post("/absences/statistics/generate_report/", data),
};

// PDF Export API
export const pdfExportAPI = {
  // Templates
  getTemplates: (params?: any) => api.get("/pdf-export/templates/", { params }),
  createTemplate: (data: any) => api.post("/pdf-export/templates/", data),
  updateTemplate: (id: number, data: any) => api.put(`/pdf-export/templates/${id}/`, data),
  deleteTemplate: (id: number) => api.delete(`/pdf-export/templates/${id}/`),
  
  // Export Jobs
  getExportJobs: (params?: any) => api.get("/pdf-export/jobs/", { params }),
  createExportJob: (data: any) => api.post("/pdf-export/jobs/", data),
  cancelExportJob: (id: number) => api.post(`/pdf-export/jobs/${id}/cancel/`),
  downloadPDF: (jobId: string) => api.get(`/pdf-export/jobs/${jobId}/download/`, { responseType: 'blob' }),
  bulkExport: (data: any) => api.post("/pdf-export/jobs/bulk_export/", data),
  getMyExports: () => api.get("/pdf-export/jobs/my_exports/"),
  getExportStatistics: () => api.get("/pdf-export/jobs/statistics/"),
  
  // Settings
  getExportSettings: () => api.get("/pdf-export/settings/"),
  updateExportSettings: (id: number, data: any) => api.put(`/pdf-export/settings/${id}/`, data),
  
  // Statistics
  getExportStatistics: (params?: any) => api.get("/pdf-export/statistics/", { params }),
  getExportSummary: () => api.get("/pdf-export/statistics/summary/"),
  
  // Download Logs
  getDownloadLogs: (params?: any) => api.get("/pdf-export/download-logs/", { params }),
};
