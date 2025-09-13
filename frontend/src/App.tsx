import React from 'react';
import { BrowserRouter as Router, Routes, Route, Navigate } from 'react-router-dom';
import { Toaster } from 'react-hot-toast';
import { QueryClient, QueryClientProvider } from 'react-query';

// Contextes
import { AuthProvider } from './contexts/AuthContext';

// Composants de base
import Layout from './components/Layout';
import Login from './components/Login';
import ProtectedRoute from './components/ProtectedRoute';

// Pages principales
import Dashboard from './pages/Dashboard';
import ScheduleViewer from './pages/ScheduleViewer';
import  TeacherDashboard  from './pages/TeacherDashboard';
import {StudentDashboard } from './pages/StudentDashboard';
import  AdminDashboard  from './pages/AdminDashboard';
import InteractiveCalendar from './pages/InteractiveCalendar';
import AIScheduleOptimizer from './pages/AIScheduleOptimizer';
import ImportExportSystem from './pages/ImportExportSystem';
import ReportsAndAnalytics from './pages/ReportsAndAnalytics';
import SubjectManagement from './pages/SubjectManagement';
import ConnectionTest from './pages/ConnectionTest';

// Pages Admin
import AdminImportExcel from './pages/admin/AdminImportExcel';
import AdminTimetableGeneration from './pages/admin/AdminTimetableGeneration';

// Configuration de toast
const toasterConfig = {
  duration: 4000,
  position: 'top-right' as const,
  toastOptions: {
    success: {
      style: {
        background: '#10B981',
        color: 'white',
      },
    },
    error: {
      style: {
        background: '#EF4444',
        color: 'white',
      },
    },
    loading: {
      style: {
        background: '#3B82F6',
        color: 'white',
      },
    },
  },
};

// Create a client
const queryClient = new QueryClient({
  defaultOptions: {
    queries: {
      refetchOnWindowFocus: false,
      retry: 1,
      staleTime: 30000,
    },
  },
});

const App: React.FC = () => {
  return (
    <QueryClientProvider client={queryClient}>
      <AuthProvider>
        <Router>
          <div className="App h-screen w-full force-desktop">
            <Toaster {...toasterConfig} />
          
          <Routes>
            {/* Route de connexion - publique */}
            <Route path="/login" element={
              <div className="force-desktop w-full h-full">
                <Login />
              </div>
            } />
            
            {/* Redirection de la racine vers dashboard */}
            <Route path="/" element={<Navigate to="/dashboard" replace />} />
            
            {/* Dashboard principal - protégé */}
            <Route path="/dashboard" element={
              <ProtectedRoute>
                <Layout>
                  <Dashboard />
                </Layout>
              </ProtectedRoute>
            } />
            
            {/* Emploi du temps - accessible à tous les utilisateurs connectés */}
            <Route path="/schedule" element={
              <ProtectedRoute>
                <Layout>
                  <ScheduleViewer />
                </Layout>
              </ProtectedRoute>
            } />

            {/* Nouvelles pages */}
            <Route path="/calendar" element={
              <ProtectedRoute>
                <Layout>
                  <InteractiveCalendar />
                </Layout>
              </ProtectedRoute>
            } />

            <Route path="/optimize" element={
              <ProtectedRoute requiredRole={["admin", "department_head", "program_head"]}>
                <Layout>
                  <AIScheduleOptimizer />
                </Layout>
              </ProtectedRoute>
            } />

            <Route path="/import-export" element={
              <ProtectedRoute requiredRole={["admin", "department_head"]}>
                <Layout>
                  <ImportExportSystem />
                </Layout>
              </ProtectedRoute>
            } />

            <Route path="/reports" element={
              <ProtectedRoute requiredRole={["admin", "department_head", "program_head"]}>
                <Layout>
                  <ReportsAndAnalytics />
                </Layout>
              </ProtectedRoute>
            } />
            
            <Route path="/schedule/personal" element={
              <ProtectedRoute>
                <Layout>
                  <ScheduleViewer />
                </Layout>
              </ProtectedRoute>
            } />
            
            <Route path="/schedule/weekly" element={
              <ProtectedRoute>
                <Layout>
                  <ScheduleViewer />
                </Layout>
              </ProtectedRoute>
            } />
            
            {/* Routes ADMINISTRATEUR */}
            <Route path="/admin/dashboard" element={
              <ProtectedRoute requiredRole="admin">
                <Layout>
                  <AdminDashboard />
                </Layout>
              </ProtectedRoute>
            } />
            
            <Route path="/admin/import-excel" element={
              <ProtectedRoute requiredRole="admin">
                <Layout>
                  <AdminImportExcel />
                </Layout>
              </ProtectedRoute>
            } />
            
            <Route path="/admin/generate-timetable" element={
              <ProtectedRoute requiredRole="admin">
                <Layout>
                  <AdminTimetableGeneration />
                </Layout>
              </ProtectedRoute>
            } />
            
            {/* Route pour la génération d'emploi du temps avec vérification de rôle explicite */}
            <Route path="/admin/generate-timetable/:id" element={
              <ProtectedRoute requiredRole="admin">
                <Layout>
                  <AdminTimetableGeneration />
                </Layout>
              </ProtectedRoute>
            } />
            
            <Route path="/admin/departments" element={
              <ProtectedRoute requiredRole={["admin", "department_head"]}>
                <Layout>
                  <div className="force-full-width padding-desktop">
                    <h1 className="text-2xl font-bold">Gestion des Départements</h1>
                    <p className="text-gray-600 mt-2">Module en cours de développement</p>
                  </div>
                </Layout>
              </ProtectedRoute>
            } />
            
            <Route path="/admin/programs" element={
              <ProtectedRoute requiredRole={["admin", "department_head", "program_head"]}>
                <Layout>
                  <div className="force-full-width padding-desktop">
                    <h1 className="text-2xl font-bold">Gestion des Programmes</h1>
                    <p className="text-gray-600 mt-2">Module en cours de développement</p>
                  </div>
                </Layout>
              </ProtectedRoute>
            } />
            
            <Route path="/admin/teachers" element={
              <ProtectedRoute requiredRole={["admin", "department_head"]}>
                <Layout>
                  <div className="force-full-width padding-desktop">
                    <h1 className="text-2xl font-bold">Gestion des Enseignants</h1>
                    <p className="text-gray-600 mt-2">Module en cours de développement</p>
                  </div>
                </Layout>
              </ProtectedRoute>
            } />
            
            <Route path="/admin/students" element={
              <ProtectedRoute requiredRole={["admin", "program_head"]}>
                <Layout>
                  <div className="force-full-width padding-desktop">
                    <h1 className="text-2xl font-bold">Gestion des Étudiants</h1>
                    <p className="text-gray-600 mt-2">Module en cours de développement</p>
                  </div>
                </Layout>
              </ProtectedRoute>
            } />
            
            <Route path="/admin/rooms" element={
              <ProtectedRoute requiredRole={["admin", "department_head"]}>
                <Layout>
                  <div className="force-full-width padding-desktop">
                    <h1 className="text-2xl font-bold">Gestion des Salles</h1>
                    <p className="text-gray-600 mt-2">Module en cours de développement</p>
                  </div>
                </Layout>
              </ProtectedRoute>
            } />
            
            <Route path="/admin/subjects" element={
              <ProtectedRoute requiredRole={["admin", "department_head"]}>
                <Layout>
                  <SubjectManagement />
                </Layout>
              </ProtectedRoute>
            } />
            
            <Route path="/admin/schedules" element={
              <ProtectedRoute requiredRole={["admin", "department_head", "program_head"]}>
                <Layout>
                  <ScheduleViewer />
                </Layout>
              </ProtectedRoute>
            } />

            {/* Routes ENSEIGNANT */}
            <Route path="/teacher/dashboard" element={
              <ProtectedRoute requiredRole="teacher">
                <Layout>
                  <TeacherDashboard />
                </Layout>
              </ProtectedRoute>
            } />
            
            <Route path="/teacher/schedules" element={
              <ProtectedRoute requiredRole="teacher">
                <Layout>
                  <ScheduleViewer />
                </Layout>
              </ProtectedRoute>
            } />
            
            <Route path="/teacher/students" element={
              <ProtectedRoute requiredRole="teacher">
                <Layout>
                  <div className="force-full-width padding-desktop">
                    <h1 className="text-2xl font-bold">Mes Étudiants</h1>
                    <p className="text-gray-600 mt-2">Module en cours de développement</p>
                  </div>
                </Layout>
              </ProtectedRoute>
            } />
            
            <Route path="/teacher/availability" element={
              <ProtectedRoute requiredRole="teacher">
                <Layout>
                  <div className="force-full-width padding-desktop">
                    <h1 className="text-2xl font-bold">Mes Disponibilités</h1>
                    <p className="text-gray-600 mt-2">Module en cours de développement</p>
                  </div>
                </Layout>
              </ProtectedRoute>
            } />

            {/* Routes ÉTUDIANT */}
            <Route path="/student/dashboard" element={
              <ProtectedRoute requiredRole="student">
                <Layout>
                  <StudentDashboard />
                </Layout>
              </ProtectedRoute>
            } />
            
            <Route path="/student/program" element={
              <ProtectedRoute requiredRole="student">
                <Layout>
                  <div className="force-full-width padding-desktop">
                    <h1 className="text-2xl font-bold">Mon Programme</h1>
                    <p className="text-gray-600 mt-2">Informations sur votre programme d'études</p>
                  </div>
                </Layout>
              </ProtectedRoute>
            } />

            {/* Routes communes */}
            <Route path="/profile" element={
              <ProtectedRoute>
                <Layout>
                  <div className="force-full-width padding-desktop">
                    <h1 className="text-2xl font-bold">Mon Profil</h1>
                    <p className="text-gray-600 mt-2">Gérer vos informations personnelles</p>
                  </div>
                </Layout>
              </ProtectedRoute>
            } />
            
            <Route path="/settings" element={
              <ProtectedRoute>
                <Layout>
                  <div className="force-full-width padding-desktop">
                    <h1 className="text-2xl font-bold">Paramètres</h1>
                    <p className="text-gray-600 mt-2">Configuration de l'application</p>
                  </div>
                </Layout>
              </ProtectedRoute>
            } />

            {/* Route de test de connexion */}
            <Route path="/connection-test" element={
              <ProtectedRoute>
                <Layout>
                  <ConnectionTest />
                </Layout>
              </ProtectedRoute>
            } />

            {/* Route de support public */}
            <Route path="/support" element={
              <div className="min-h-screen flex items-center justify-center bg-gray-50 force-desktop w-full">
                <div className="max-w-md w-full bg-white rounded-lg shadow-lg p-8 text-center">
                  <h1 className="text-2xl font-bold text-gray-900 mb-4">Support</h1>
                  <p className="text-gray-600 mb-6">
                    Pour obtenir de l'aide, veuillez contacter l'administrateur système.
                  </p>
                  <div className="space-y-2 text-sm text-gray-500">
                    <p><strong>Email:</strong> support@university.edu</p>
                    <p><strong>Téléphone:</strong> +212 528 xx xx xx</p>
                  </div>
                </div>
              </div>
            } />

            {/* Route 404 - doit être en dernier */}
            <Route path="*" element={
              <div className="min-h-screen flex items-center justify-center bg-gray-50 force-desktop w-full">
                <div className="text-center">
                  <h1 className="text-6xl font-bold text-gray-300">404</h1>
                  <p className="text-xl text-gray-600 mt-4">Page non trouvée</p>
                  <div className="mt-6 space-x-4">
                    <button
                      onClick={() => window.history.back()}
                      className="px-4 py-2 bg-gray-600 text-white rounded-lg hover:bg-gray-700"
                    >
                      Retour
                    </button>
                    <a
                      href="/dashboard"
                      className="inline-block px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700"
                    >
                      Dashboard
                    </a>
                  </div>
                </div>
              </div>
            } />
          </Routes>
        </div>
      </Router>
    </AuthProvider>
  </QueryClientProvider>
  );
};

export default App;