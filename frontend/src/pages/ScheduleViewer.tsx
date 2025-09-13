// ScheduleViewer.tsx - Emploi du temps optimisé pour desktop
import React, { useState, useEffect } from 'react';
import { useAuth, useAuthenticatedFetch } from '../contexts/AuthContext';
import { 
  Calendar, ChevronLeft, ChevronRight, Download, Filter,
  Clock, MapPin, User, BookOpen, Users, FileText,
  RefreshCw, Grid, List, Search, Plus, Edit, Eye,
  MoreHorizontal, ChevronDown, Maximize2, X
} from 'lucide-react';
import { toast } from 'react-hot-toast';
import { format, startOfWeek, addWeeks, subWeeks, addDays, isSameDay, isToday } from 'date-fns';
import { fr } from 'date-fns/locale';

// Types
interface Schedule {
  id: number;
  title: string;
  subject_name: string;
  subject_code: string;
  teacher_name: string;
  room_name: string;
  room_capacity: number;
  time_slot_info: {
    id: number;
    day_of_week: number;
    day_display: string;
    start_time: string;
    end_time: string;
    duration_minutes: number;
  };
  programs_list: string[];
  start_date: string;
  end_date: string;
  duration_minutes: number;
  student_count: number;
  is_room_suitable: boolean;
  is_cancelled: boolean;
  is_makeup: boolean;
  notes?: string;
}

interface WeeklySchedule {
  week_start: string;
  week_end: string;
  days: DaySchedule[];
  total_sessions: number;
  total_hours: number;
}

interface DaySchedule {
  date: string;
  day_name: string;
  schedules: Schedule[];
  total_sessions: number;
  total_hours: number;
}

type ViewMode = 'week' | 'month' | 'list';
type FilterMode = 'all' | 'my' | 'program' | 'teacher' | 'room';

const ScheduleViewer: React.FC = () => {
  const { user, hasRole } = useAuth();
  const authenticatedFetch = useAuthenticatedFetch();
  
  // States
  const [currentWeek, setCurrentWeek] = useState(startOfWeek(new Date(), { locale: fr }));
  const [weeklySchedule, setWeeklySchedule] = useState<WeeklySchedule | null>(null);
  const [viewMode, setViewMode] = useState<ViewMode>('week');
  const [filterMode, setFilterMode] = useState<FilterMode>('all');
  const [searchTerm, setSearchTerm] = useState('');
  const [loading, setLoading] = useState(false);
  const [selectedSchedule, setSelectedSchedule] = useState<Schedule | null>(null);
  const [showFilters, setShowFilters] = useState(false);
  
  // Filtres avancés
  const [filters, setFilters] = useState({
    program: '',
    teacher: '',
    room: '',
    subject: '',
    startTime: '',
    endTime: ''
  });

  // Chargement des données
  const loadWeeklySchedule = async () => {
    try {
      setLoading(true);
      
      const params = new URLSearchParams({
        week_start: format(currentWeek, 'yyyy-MM-dd'),
        format: 'json'
      });

      // Ajouter les filtres
      if (filterMode === 'my' && user) {
        if (user.role === 'teacher') {
          params.append('teacher', user.id.toString());
        } else if (user.role === 'student') {
          params.append('student', user.id.toString());
        }
      }
      
      Object.entries(filters).forEach(([key, value]) => {
        if (value) params.append(key, value);
      });

      const response = await authenticatedFetch(`/api/schedule/schedules/by-week/?${params}`);
      
      if (response.ok) {
        const data = await response.json();
        setWeeklySchedule(data);
      } else {
        throw new Error('Erreur lors du chargement');
      }
    } catch (error) {
      console.error('Erreur:', error);
      toast.error('Impossible de charger l\'emploi du temps');
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    loadWeeklySchedule();
  }, [currentWeek, filterMode, filters]);

  // Navigation
  const goToPreviousWeek = () => setCurrentWeek(prev => subWeeks(prev, 1));
  const goToNextWeek = () => setCurrentWeek(prev => addWeeks(prev, 1));
  const goToToday = () => setCurrentWeek(startOfWeek(new Date(), { locale: fr }));

  // Export functions
  const exportToPDF = async () => {
    try {
      const params = new URLSearchParams({
        week_start: format(currentWeek, 'yyyy-MM-dd'),
        format: 'pdf'
      });
      
      window.open(`/api/schedule/schedules/by-week/?${params}`, '_blank');
      toast.success('Export PDF en cours...');
    } catch (error) {
      toast.error('Erreur lors de l\'export PDF');
    }
  };

  const exportToExcel = async () => {
    try {
      const params = new URLSearchParams({
        week_start: format(currentWeek, 'yyyy-MM-dd'),
        format: 'excel'
      });
      
      window.open(`/api/schedule/schedules/by-week/?${params}`, '_blank');
      toast.success('Export Excel en cours...');
    } catch (error) {
      toast.error('Erreur lors de l\'export Excel');
    }
  };

  // Rendu des créneaux
  const renderScheduleItem = (schedule: Schedule, compact = false) => {
    const getStatusColor = () => {
      if (schedule.is_cancelled) return 'border-red-300 bg-red-50';
      if (schedule.is_makeup) return 'border-orange-300 bg-orange-50';
      if (!schedule.is_room_suitable) return 'border-yellow-300 bg-yellow-50';
      return 'border-blue-300 bg-blue-50';
    };

    const getStatusText = () => {
      if (schedule.is_cancelled) return 'Annulé';
      if (schedule.is_makeup) return 'Rattrapage';
      if (!schedule.is_room_suitable) return 'Salle inadaptée';
      return '';
    };

    return (
      <div
        key={schedule.id}
        className={`${getStatusColor()} border-l-4 rounded-lg p-4 hover:shadow-md transition-all duration-200 cursor-pointer group`}
        onClick={() => setSelectedSchedule(schedule)}
      >
        <div className="flex items-start justify-between">
          <div className="flex-1 min-w-0">
            <div className="flex items-center space-x-2 mb-2">
              <Clock className="h-4 w-4 text-gray-500 flex-shrink-0" />
              <span className="text-sm font-semibold text-gray-900">
                {schedule.time_slot_info.start_time} - {schedule.time_slot_info.end_time}
              </span>
              {getStatusText() && (
                <span className="inline-flex items-center px-2 py-0.5 rounded-full text-xs font-medium bg-red-100 text-red-800">
                  {getStatusText()}
                </span>
              )}
            </div>
            
            <h3 className={`font-semibold text-gray-900 ${compact ? 'text-sm' : 'text-base'} truncate mb-1`}>
              {schedule.subject_name}
            </h3>
            
            {!compact && (
              <>
                <div className="flex items-center text-sm text-gray-600 mb-1">
                  <User className="h-3 w-3 mr-1" />
                  <span className="truncate">{schedule.teacher_name}</span>
                </div>
                
                <div className="flex items-center text-sm text-gray-600 mb-1">
                  <MapPin className="h-3 w-3 mr-1" />
                  <span className="truncate">{schedule.room_name}</span>
                  <span className="ml-2 text-xs text-gray-500">
                    ({schedule.student_count}/{schedule.room_capacity})
                  </span>
                </div>
                
                {schedule.programs_list.length > 0 && (
                  <div className="flex items-center text-sm text-gray-600">
                    <Users className="h-3 w-3 mr-1" />
                    <span className="truncate">{schedule.programs_list.join(', ')}</span>
                  </div>
                )}
              </>
            )}
          </div>
          
          <div className="flex-shrink-0 ml-2">
            <button className="opacity-0 group-hover:opacity-100 transition-opacity p-1 hover:bg-white rounded">
              <MoreHorizontal className="h-4 w-4 text-gray-500" />
            </button>
          </div>
        </div>
        
        {schedule.notes && !compact && (
          <div className="mt-2 text-xs text-gray-500 italic">
            {schedule.notes}
          </div>
        )}
      </div>
    );
  };

  // Rendu de la vue semaine
  const renderWeekView = () => {
    if (!weeklySchedule) return null;

    const timeSlots = Array.from(new Set(
      weeklySchedule.days.flatMap(day => 
        day.schedules.map(s => `${s.time_slot_info.start_time}-${s.time_slot_info.end_time}`)
      )
    )).sort();

    return (
      <div className="overflow-hidden bg-white rounded-xl shadow-sm border border-gray-200">
        {/* En-tête des jours */}
        <div className="grid grid-cols-8 border-b border-gray-200">
          <div className="p-4 bg-gray-50 border-r border-gray-200">
            <span className="text-sm font-medium text-gray-500">Heure</span>
          </div>
          {weeklySchedule.days.map((day) => (
            <div key={day.date} className={`p-4 text-center border-r border-gray-200 last:border-r-0 ${
              isToday(new Date(day.date)) ? 'bg-blue-50' : 'bg-gray-50'
            }`}>
              <div className="text-sm font-medium text-gray-900">{day.day_name}</div>
              <div className={`text-sm ${isToday(new Date(day.date)) ? 'text-blue-600 font-semibold' : 'text-gray-500'}`}>
                {format(new Date(day.date), 'd MMM', { locale: fr })}
              </div>
              <div className="text-xs text-gray-400 mt-1">
                {day.total_sessions} cours
              </div>
            </div>
          ))}
        </div>

        {/* Grille des cours */}
        <div className="max-h-96 overflow-y-auto">
          {timeSlots.map((timeSlot) => (
            <div key={timeSlot} className="grid grid-cols-8 border-b border-gray-100 last:border-b-0 min-h-[120px]">
              <div className="p-3 bg-gray-50 border-r border-gray-200 flex items-start">
                <span className="text-xs font-medium text-gray-600">{timeSlot}</span>
              </div>
              {weeklySchedule.days.map((day) => {
                const daySchedules = day.schedules.filter(s => 
                  `${s.time_slot_info.start_time}-${s.time_slot_info.end_time}` === timeSlot
                );
                
                return (
                  <div key={day.date} className="p-2 border-r border-gray-200 last:border-r-0 space-y-1">
                    {daySchedules.map(schedule => renderScheduleItem(schedule, true))}
                  </div>
                );
              })}
            </div>
          ))}
        </div>
      </div>
    );
  };

  // Rendu de la vue liste
  const renderListView = () => {
    if (!weeklySchedule) return null;

    return (
      <div className="space-y-4">
        {weeklySchedule.days.map((day) => {
          const daySchedules = day.schedules.filter(schedule => 
            !searchTerm || 
            schedule.subject_name.toLowerCase().includes(searchTerm.toLowerCase()) ||
            schedule.teacher_name.toLowerCase().includes(searchTerm.toLowerCase()) ||
            schedule.room_name.toLowerCase().includes(searchTerm.toLowerCase())
          );

          if (daySchedules.length === 0) return null;

          return (
            <div key={day.date} className="bg-white rounded-xl shadow-sm border border-gray-200 overflow-hidden">
              <div className={`px-6 py-4 border-b border-gray-200 ${
                isToday(new Date(day.date)) ? 'bg-blue-50' : 'bg-gray-50'
              }`}>
                <div className="flex items-center justify-between">
                  <div>
                    <h3 className={`text-lg font-semibold ${
                      isToday(new Date(day.date)) ? 'text-blue-900' : 'text-gray-900'
                    }`}>
                      {day.day_name}
                    </h3>
                    <p className="text-sm text-gray-600">
                      {format(new Date(day.date), 'EEEE d MMMM yyyy', { locale: fr })}
                    </p>
                  </div>
                  <div className="text-right">
                    <p className="text-sm font-medium text-gray-900">{day.total_sessions} cours</p>
                    <p className="text-xs text-gray-500">{day.total_hours}h total</p>
                  </div>
                </div>
              </div>
              
              <div className="p-6 space-y-4">
                {daySchedules.map(schedule => renderScheduleItem(schedule))}
              </div>
            </div>
          );
        })}
      </div>
    );
  };

  return (
    <div className="min-h-screen bg-gray-50">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        
        {/* En-tête */}
        <div className="mb-8">
          <div className="flex flex-col lg:flex-row lg:items-center lg:justify-between gap-4">
            <div>
              <h1 className="text-3xl font-bold text-gray-900">Emploi du Temps</h1>
              <p className="text-gray-600 mt-1">
                Semaine du {format(currentWeek, 'd MMMM yyyy', { locale: fr })}
              </p>
            </div>
            
            <div className="flex items-center space-x-4">
              {/* Barre de recherche */}
              <div className="relative">
                <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 h-4 w-4 text-gray-400" />
                <input
                  type="text"
                  placeholder="Rechercher..."
                  value={searchTerm}
                  onChange={(e) => setSearchTerm(e.target.value)}
                  className="pl-10 pr-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-primary-500 focus:border-primary-500 text-sm"
                />
              </div>
              
              {/* Boutons d'export */}
              <div className="flex space-x-2">
                <button
                  onClick={exportToPDF}
                  className="btn-secondary text-sm"
                  title="Exporter en PDF"
                >
                  <FileText className="h-4 w-4 mr-2" />
                  PDF
                </button>
                <button
                  onClick={exportToExcel}
                  className="btn-secondary text-sm"
                  title="Exporter en Excel"
                >
                  <Download className="h-4 w-4 mr-2" />
                  Excel
                </button>
              </div>
            </div>
          </div>
        </div>

        {/* Contrôles */}
        <div className="mb-6 flex flex-col lg:flex-row lg:items-center lg:justify-between gap-4">
          
          {/* Navigation semaine */}
          <div className="flex items-center space-x-4">
            <div className="flex items-center bg-white rounded-lg border border-gray-200 p-1">
              <button
                onClick={goToPreviousWeek}
                className="p-2 hover:bg-gray-100 rounded transition-colors"
                title="Semaine précédente"
              >
                <ChevronLeft className="h-4 w-4" />
              </button>
              
              <button
                onClick={goToToday}
                className="px-4 py-2 text-sm font-medium text-gray-700 hover:bg-gray-100 rounded transition-colors"
              >
                Aujourd'hui
              </button>
              
              <button
                onClick={goToNextWeek}
                className="p-2 hover:bg-gray-100 rounded transition-colors"
                title="Semaine suivante"
              >
                <ChevronRight className="h-4 w-4" />
              </button>
            </div>
            
            <button
              onClick={loadWeeklySchedule}
              disabled={loading}
              className="p-2 text-gray-500 hover:text-gray-700 transition-colors"
              title="Actualiser"
            >
              <RefreshCw className={`h-4 w-4 ${loading ? 'animate-spin' : ''}`} />
            </button>
          </div>

          {/* Modes de vue et filtres */}
          <div className="flex items-center space-x-4">
            
            {/* Mode de vue */}
            <div className="flex items-center bg-white rounded-lg border border-gray-200 p-1">
              <button
                onClick={() => setViewMode('week')}
                className={`p-2 rounded transition-colors ${
                  viewMode === 'week' ? 'bg-primary-100 text-primary-700' : 'text-gray-500 hover:text-gray-700'
                }`}
                title="Vue semaine"
              >
                <Grid className="h-4 w-4" />
              </button>
              <button
                onClick={() => setViewMode('list')}
                className={`p-2 rounded transition-colors ${
                  viewMode === 'list' ? 'bg-primary-100 text-primary-700' : 'text-gray-500 hover:text-gray-700'
                }`}
                title="Vue liste"
              >
                <List className="h-4 w-4" />
              </button>
            </div>

            {/* Filtre rapide */}
            <select
              value={filterMode}
              onChange={(e) => setFilterMode(e.target.value as FilterMode)}
              className="border border-gray-300 rounded-lg px-3 py-2 text-sm focus:ring-2 focus:ring-primary-500 focus:border-primary-500"
            >
              <option value="all">Tous les cours</option>
              <option value="my">Mes cours</option>
              <option value="program">Par programme</option>
              <option value="teacher">Par enseignant</option>
              <option value="room">Par salle</option>
            </select>

            {/* Filtres avancés */}
            <button
              onClick={() => setShowFilters(!showFilters)}
              className={`p-2 rounded transition-colors ${
                showFilters ? 'bg-primary-100 text-primary-700' : 'text-gray-500 hover:text-gray-700'
              }`}
              title="Filtres avancés"
            >
              <Filter className="h-4 w-4" />
            </button>
          </div>
        </div>

        {/* Statistiques rapides */}
        {weeklySchedule && (
          <div className="mb-6 grid grid-cols-1 md:grid-cols-3 gap-4">
            <div className="bg-white rounded-xl shadow-sm border border-gray-200 p-6">
              <div className="flex items-center">
                <div className="flex-shrink-0">
                  <Calendar className="h-8 w-8 text-blue-600" />
                </div>
                <div className="ml-4">
                  <p className="text-sm font-medium text-gray-500">Sessions total</p>
                  <p className="text-2xl font-bold text-gray-900">{weeklySchedule.total_sessions}</p>
                </div>
              </div>
            </div>
            
            <div className="bg-white rounded-xl shadow-sm border border-gray-200 p-6">
              <div className="flex items-center">
                <div className="flex-shrink-0">
                  <Clock className="h-8 w-8 text-green-600" />
                </div>
                <div className="ml-4">
                  <p className="text-sm font-medium text-gray-500">Heures total</p>
                  <p className="text-2xl font-bold text-gray-900">{weeklySchedule.total_hours}h</p>
                </div>
              </div>
            </div>
            
            <div className="bg-white rounded-xl shadow-sm border border-gray-200 p-6">
              <div className="flex items-center">
                <div className="flex-shrink-0">
                  <Users className="h-8 w-8 text-purple-600" />
                </div>
                <div className="ml-4">
                  <p className="text-sm font-medium text-gray-500">Jours actifs</p>
                  <p className="text-2xl font-bold text-gray-900">
                    {weeklySchedule.days.filter(d => d.total_sessions > 0).length}/7
                  </p>
                </div>
              </div>
            </div>
          </div>
        )}

        {/* Contenu principal */}
        {loading ? (
          <div className="flex items-center justify-center py-12">
            <div className="text-center">
              <RefreshCw className="h-8 w-8 animate-spin text-primary-600 mx-auto mb-4" />
              <p className="text-gray-600">Chargement de l\'emploi du temps...</p>
            </div>
          </div>
        ) : weeklySchedule ? (
          <div>
            {viewMode === 'week' ? renderWeekView() : renderListView()}
          </div>
        ) : (
          <div className="text-center py-12">
            <Calendar className="h-16 w-16 text-gray-400 mx-auto mb-4" />
            <h3 className="text-lg font-medium text-gray-900 mb-2">Aucun emploi du temps</h3>
            <p className="text-gray-600">Aucun cours trouvé pour cette semaine.</p>
          </div>
        )}

        {/* Modal de détails */}
        {selectedSchedule && (
          <div className="fixed inset-0 bg-gray-600 bg-opacity-75 flex items-center justify-center z-50 p-4">
            <div className="bg-white rounded-xl shadow-2xl max-w-2xl w-full max-h-full overflow-y-auto">
              <div className="p-6 border-b border-gray-200">
                <div className="flex items-center justify-between">
                  <h2 className="text-xl font-semibold text-gray-900">
                    Détails du cours
                  </h2>
                  <button
                    onClick={() => setSelectedSchedule(null)}
                    className="text-gray-400 hover:text-gray-600 transition-colors"
                  >
                    <X className="h-6 w-6" />
                  </button>
                </div>
              </div>
              
              <div className="p-6 space-y-6">
                <div>
                  <h3 className="text-lg font-semibold text-gray-900 mb-2">
                    {selectedSchedule.subject_name}
                  </h3>
                  <p className="text-sm text-gray-600">{selectedSchedule.subject_code}</p>
                </div>
                
                <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                  <div>
                    <h4 className="text-sm font-medium text-gray-900 mb-3">Informations</h4>
                    <div className="space-y-2 text-sm">
                      <div className="flex items-center">
                        <Clock className="h-4 w-4 text-gray-400 mr-2" />
                        <span>{selectedSchedule.time_slot_info.start_time} - {selectedSchedule.time_slot_info.end_time}</span>
                      </div>
                      <div className="flex items-center">
                        <User className="h-4 w-4 text-gray-400 mr-2" />
                        <span>{selectedSchedule.teacher_name}</span>
                      </div>
                      <div className="flex items-center">
                        <MapPin className="h-4 w-4 text-gray-400 mr-2" />
                        <span>{selectedSchedule.room_name}</span>
                      </div>
                      <div className="flex items-center">
                        <Users className="h-4 w-4 text-gray-400 mr-2" />
                        <span>{selectedSchedule.student_count}/{selectedSchedule.room_capacity} étudiants</span>
                      </div>
                    </div>
                  </div>
                  
                  <div>
                    <h4 className="text-sm font-medium text-gray-900 mb-3">Programmes concernés</h4>
                    <div className="space-y-1">
                      {selectedSchedule.programs_list.map((program, index) => (
                        <span key={index} className="inline-block bg-blue-100 text-blue-800 text-xs px-2 py-1 rounded-full mr-1 mb-1">
                          {program}
                        </span>
                      ))}
                    </div>
                  </div>
                </div>
                
                {selectedSchedule.notes && (
                  <div>
                    <h4 className="text-sm font-medium text-gray-900 mb-2">Notes</h4>
                    <p className="text-sm text-gray-600 bg-gray-50 p-3 rounded-lg">
                      {selectedSchedule.notes}
                    </p>
                  </div>
                )}
              </div>
              
              <div className="p-6 border-t border-gray-200 flex justify-end space-x-2">
                {hasRole(['admin', 'department_head', 'program_head']) && (
                  <button className="btn-primary">
                    <Edit className="h-4 w-4 mr-2" />
                    Modifier
                  </button>
                )}
                <button
                  onClick={() => setSelectedSchedule(null)}
                  className="btn-secondary"
                >
                  Fermer
                </button>
              </div>
            </div>
          </div>
        )}

      </div>
    </div>
  );
};

export default ScheduleViewer;