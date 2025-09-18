import React, { useState, useEffect, useCallback } from 'react';
import {
  ChevronLeft,
  ChevronRight,
  Plus,
  Filter,
  RefreshCw,
  Download,
  Share,
  Calendar as CalendarIcon,
  Clock
} from 'lucide-react';
import { toast } from 'react-hot-toast';
import { useAuth } from '../contexts/AuthContext';
import { scheduleAPI } from '../services/api';

interface CalendarEvent {
  id: string;
  title: string;
  subject: {
    id: string;
    name: string;
    code: string;
    color: string;
  };
  teacher: {
    id: string;
    name: string;
  };
  room: {
    id: string;
    name: string;
    capacity: number;
  };
  programs: Array<{
    id: string;
    name: string;
    studentsCount: number;
  }>;
  startTime: string;
  endTime: string;
  date: string;
  duration: number;
  type: 'CM' | 'TD' | 'TP' | 'EXAM' | 'PROJECT';
  status: 'scheduled' | 'ongoing' | 'completed' | 'cancelled';
}

interface CalendarView {
  mode: 'day' | 'week' | 'month';
  date: Date;
}

const InteractiveCalendar: React.FC = () => {
  const { user } = useAuth();
  const [events, setEvents] = useState<CalendarEvent[]>([]);
  const [view, setView] = useState<CalendarView>({
    mode: 'week',
    date: new Date(),
  });
  const [loading, setLoading] = useState(false);

  const daysOfWeek = ['Lundi', 'Mardi', 'Mercredi', 'Jeudi', 'Vendredi'];
  const timeSlots: string[] = [];
  
  // Générer les créneaux horaires de 00:00 à 02:00 (comme dans l'image)
  for (let hour = 0; hour <= 2; hour++) {
    timeSlots.push(`${hour.toString().padStart(2, '0')}:00`);
  }

  useEffect(() => {
    loadEvents();
  }, [view.date, view.mode]);

  const loadEvents = async () => {
    setLoading(true);
    try {
      const startDate = getWeekStart(view.date);
      const endDate = getWeekEnd(view.date);
      
      const response = await scheduleAPI.getScheduleByWeek({
        start_date: startDate.toISOString().split('T')[0],
        end_date: endDate.toISOString().split('T')[0],
      });
      
      setEvents(response.data.results || []);
    } catch (error) {
      console.error('Erreur chargement événements:', error);
      // Données de démonstration si l'API n'est pas disponible
      setEvents([]);
    } finally {
      setLoading(false);
    }
  };

  const getWeekStart = (date: Date): Date => {
    const start = new Date(date);
    const day = start.getDay();
    const diff = start.getDate() - day + (day === 0 ? -6 : 1);
    start.setDate(diff);
    start.setHours(0, 0, 0, 0);
    return start;
  };

  const getWeekEnd = (date: Date): Date => {
    const start = getWeekStart(date);
    const end = new Date(start);
    end.setDate(start.getDate() + 6);
    end.setHours(23, 59, 59, 999);
    return end;
  };

  const getWeekDates = (date: Date): Date[] => {
    const start = getWeekStart(date);
    const dates: Date[] = [];
    for (let i = 0; i < 5; i++) { // Seulement lundi à vendredi
      const d = new Date(start);
      d.setDate(start.getDate() + i);
      dates.push(d);
    }
    return dates;
  };

  const navigateDate = (direction: 'prev' | 'next') => {
    const newDate = new Date(view.date);
    switch (view.mode) {
      case 'day':
        newDate.setDate(newDate.getDate() + (direction === 'next' ? 1 : -1));
        break;
      case 'week':
        newDate.setDate(newDate.getDate() + (direction === 'next' ? 7 : -7));
        break;
      case 'month':
        newDate.setMonth(newDate.getMonth() + (direction === 'next' ? 1 : -1));
        break;
    }
    setView(prev => ({ ...prev, date: newDate }));
  };

  const goToToday = () => {
    const today = new Date();
    setView(prev => ({ ...prev, date: today }));
  };

  const getDateDisplay = () => {
    const currentDate = new Date();
    return {
      month: currentDate.toLocaleDateString('fr-FR', { month: 'long' }),
      year: currentDate.getFullYear().toString()
    };
  };

  const handleNewCourse = () => {
    toast.success('Nouvelle fonctionnalité de cours à implémenter');
  };

  const handleRefresh = async () => {
    await loadEvents();
    toast.success('Calendrier actualisé');
  };

  const handleExport = () => {
    toast.success('Export à implémenter');
  };

  const handleShare = () => {
    toast.success('Partage à implémenter');
  };

  const renderWeekView = () => {
    const weekDates = getWeekDates(view.date);
    const { month, year } = getDateDisplay();
    
    return (
      <div className="flex flex-col h-full bg-white">
        {/* En-tête du calendrier */}
        <div className="border-b border-gray-200 bg-white px-6 py-4">
          <div className="flex items-center justify-between">
            {/* Navigation et titre */}
            <div className="flex items-center space-x-6">
              <div className="flex items-center space-x-2">
                <button
                  onClick={() => navigateDate('prev')}
                  className="p-2 hover:bg-gray-100 rounded-lg transition-colors"
                  disabled={loading}
                >
                  <ChevronLeft className="w-5 h-5 text-gray-600" />
                </button>
                
                <button
                  onClick={goToToday}
                  className="px-4 py-2 bg-blue-600 text-white text-sm font-medium rounded-lg hover:bg-blue-700 transition-colors"
                >
                  Aujourd'hui
                </button>
                
                <button
                  onClick={() => navigateDate('next')}
                  className="p-2 hover:bg-gray-100 rounded-lg transition-colors"
                  disabled={loading}
                >
                  <ChevronRight className="w-5 h-5 text-gray-600" />
                </button>
              </div>

              <h1 className="text-xl font-semibold text-gray-900">
                {month} {year}
              </h1>
            </div>

            {/* Contrôles de vue et actions */}
            <div className="flex items-center space-x-4">
              {/* Sélecteur de vue */}
              <div className="flex bg-gray-100 rounded-lg p-1">
                {[
                  { id: 'day', label: 'Jour' },
                  { id: 'week', label: 'Semaine' },
                  { id: 'month', label: 'Mois' }
                ].map((mode) => (
                  <button
                    key={mode.id}
                    onClick={() => setView(prev => ({ ...prev, mode: mode.id as any }))}
                    className={`px-3 py-1.5 text-sm font-medium rounded-md transition-all ${
                      view.mode === mode.id
                        ? 'bg-white text-blue-600 shadow-sm'
                        : 'text-gray-600 hover:text-gray-900'
                    }`}
                  >
                    {mode.label}
                  </button>
                ))}
              </div>

              {/* Actions */}
              <div className="flex items-center space-x-2">
                <button
                  onClick={handleRefresh}
                  disabled={loading}
                  className="p-2 text-gray-600 hover:text-gray-900 hover:bg-gray-100 rounded-lg transition-colors"
                  title="Actualiser"
                >
                  <RefreshCw className={`w-5 h-5 ${loading ? 'animate-spin' : ''}`} />
                </button>

                <button
                  onClick={() => {}}
                  className="p-2 text-gray-600 hover:text-gray-900 hover:bg-gray-100 rounded-lg transition-colors"
                  title="Filtres"
                >
                  <Filter className="w-5 h-5" />
                </button>

                <button
                  onClick={handleExport}
                  className="p-2 text-gray-600 hover:text-gray-900 hover:bg-gray-100 rounded-lg transition-colors"
                  title="Exporter"
                >
                  <Download className="w-5 h-5" />
                </button>

                <button
                  onClick={handleShare}
                  className="p-2 text-gray-600 hover:text-gray-900 hover:bg-gray-100 rounded-lg transition-colors"
                  title="Partager"
                >
                  <Share className="w-5 h-5" />
                </button>

                <button
                  onClick={handleNewCourse}
                  className="px-4 py-2 bg-blue-600 text-white text-sm font-medium rounded-lg hover:bg-blue-700 transition-colors flex items-center space-x-2 ml-2"
                >
                  <Plus className="w-4 h-4" />
                  <span>Nouveau Cours</span>
                </button>
              </div>
            </div>
          </div>
        </div>

        {/* Titre de la section */}
        <div className="px-6 py-4 border-b border-gray-200 bg-gray-50">
          <h2 className="text-lg font-semibold text-gray-900 flex items-center space-x-2">
            <CalendarIcon className="w-5 h-5" />
            <span>Calendrier Interactif</span>
          </h2>
        </div>

        {/* En-tête des jours de la semaine */}
        <div className="grid grid-cols-6 border-b border-gray-200 bg-gray-50">
          <div className="p-4 text-center border-r border-gray-200">
            <div className="w-12 h-12 flex items-center justify-center">
              <Clock className="w-4 h-4 text-gray-400" />
            </div>
          </div>
          {weekDates.map((date, index) => (
            <div key={index} className="p-4 text-center border-r border-gray-200">
              <div className="text-sm font-medium text-gray-600 mb-1">
                {daysOfWeek[index]}
              </div>
              <div className={`text-lg font-bold ${
                date.toDateString() === new Date().toDateString() 
                  ? 'text-blue-600' 
                  : 'text-gray-900'
              }`}>
                {date.getDate()} {date.toLocaleDateString('fr-FR', { month: 'short' })}
              </div>
            </div>
          ))}
        </div>

        {/* Grille des heures */}
        <div className="flex-1 overflow-auto">
          <div className="grid grid-cols-6">
            {/* Colonne des heures */}
            <div className="border-r border-gray-200">
              {timeSlots.map((time, index) => (
                <div
                  key={index}
                  className="h-16 border-b border-gray-100 flex items-center justify-center bg-gray-50"
                >
                  <span className="text-sm text-gray-600 font-medium">{time}</span>
                </div>
              ))}
            </div>

            {/* Colonnes des jours */}
            {weekDates.map((date, dayIndex) => (
              <div key={dayIndex} className="border-r border-gray-200 relative">
                {timeSlots.map((time, timeIndex) => (
                  <div
                    key={timeIndex}
                    className="h-16 border-b border-gray-100 relative hover:bg-gray-50 cursor-pointer transition-colors"
                    onClick={() => {
                      // Logique pour créer un nouveau cours à cette heure
                      console.log(`Nouveau cours le ${date.toISOString().split('T')[0]} à ${time}`);
                    }}
                  >
                    {/* Espace pour les événements (vide pour l'instant comme dans l'image) */}
                    <div className="absolute inset-1">
                      {/* Les événements seraient rendus ici s'il y en avait */}
                    </div>
                  </div>
                ))}
              </div>
            ))}
          </div>
        </div>
      </div>
    );
  };

  return (
    <div className="h-full flex flex-col bg-gray-50">
      {/* Contenu principal */}
      <div className="flex-1 overflow-hidden">
        {view.mode === 'week' && renderWeekView()}
        
        {view.mode === 'day' && (
          <div className="h-full flex items-center justify-center bg-white">
            <div className="text-center py-12">
              <CalendarIcon className="w-16 h-16 text-gray-300 mx-auto mb-4" />
              <h3 className="text-lg font-medium text-gray-900 mb-2">Vue Jour</h3>
              <p className="text-gray-500">
                La vue détaillée par jour sera disponible prochainement
              </p>
            </div>
          </div>
        )}
        
        {view.mode === 'month' && (
          <div className="h-full flex items-center justify-center bg-white">
            <div className="text-center py-12">
              <CalendarIcon className="w-16 h-16 text-gray-300 mx-auto mb-4" />
              <h3 className="text-lg font-medium text-gray-900 mb-2">Vue Mensuelle</h3>
              <p className="text-gray-500">
                La vue mensuelle sera disponible prochainement
              </p>
            </div>
          </div>
        )}
      </div>

      {/* Indicateur de chargement */}
      {loading && (
        <div className="absolute inset-0 bg-white bg-opacity-50 flex items-center justify-center z-50">
          <div className="bg-white p-4 rounded-lg shadow-lg flex items-center space-x-3">
            <RefreshCw className="w-5 h-5 text-blue-600 animate-spin" />
            <span className="text-sm font-medium text-gray-900">Chargement...</span>
          </div>
        </div>
      )}
    </div>
  );
};

export default InteractiveCalendar;