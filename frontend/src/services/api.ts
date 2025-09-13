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
};

// Notifications API
export const notificationsAPI = {
  getNotifications: () => api.get("/notifications/"),

  markAsRead: (id: number) => api.post(`/notifications/${id}/read/`),

  markAllAsRead: () => api.post("/notifications/mark-all-read/"),

  getUnreadCount: () => api.get("/notifications/unread-count/"),
};
