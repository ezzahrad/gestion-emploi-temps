import React, { useState } from 'react';
import { motion } from 'framer-motion';
import { useQuery } from 'react-query';
import { Calendar, dateFnsLocalizer } from 'react-big-calendar';
import { format, parse, startOfWeek, getDay } from 'date-fns';
import { fr } from 'date-fns/locale';
import { Plus, Filter, Download } from 'lucide-react';
import { scheduleAPI } from '../services/api';
import { useAuth } from '../contexts/AuthContext';
import 'react-big-calendar/lib/css/react-big-calendar.css';

const locales = { fr };
const localizer = dateFnsLocalizer({
  format,
  parse,
  startOfWeek: () => startOfWeek(new Date(), { weekStartsOn: 1 }),
  getDay,
  locales,
});

// Custom messages in French
const messages = {
  allDay: 'Toute la journée',
  previous: 'Précédent',
  next: 'Suivant',
  today: "Aujourd'hui",
  month: 'Mois',
  week: 'Semaine',
  day: 'Jour',
  agenda: 'Agenda',
  date: 'Date',
  time: 'Heure',
  event: 'Événement',
  noEventsInRange: 'Aucun cours dans cette période',
  showMore: (total: any) => `+ ${total} de plus`,
};

export const ScheduleCalendar: React.FC = () => {
  const { user } = useAuth();
  const [currentDate, setCurrentDate] = useState(new Date());
  const [view] = useState<'month' | 'week' | 'day'>('week');
  const [, setShowCreateModal] = useState(false);

  // Get week dates for API call
  const getWeekDates = (date: Date) => {
    const start = startOfWeek(date, { weekStartsOn: 1 });
    const end = new Date(start);
    end.setDate(start.getDate() + 6);
    return {
      week_start: format(start, 'yyyy-MM-dd'),
      week_end: format(end, 'yyyy-MM-dd')
    };
  };

  const { data: schedules = [], isLoading } = useQuery(
    ['schedules', currentDate],
    () => {
      const dates = getWeekDates(currentDate);
      return scheduleAPI.getScheduleByWeek(dates).then((res: { data: any; }) => res.data);
    }
  );

  // Convert schedules to calendar events
  const events = schedules.map((schedule: any) => {
    const eventDate = new Date(schedule.week_start);
    eventDate.setDate(eventDate.getDate() + schedule.day_of_week);
    
    const [startHour, startMinute] = schedule.start_time.split(':');
    const [endHour, endMinute] = schedule.end_time.split(':');
    
    const start = new Date(eventDate);
    start.setHours(parseInt(startHour), parseInt(startMinute));
    
    const end = new Date(eventDate);
    end.setHours(parseInt(endHour), parseInt(endMinute));

    return {
      id: schedule.id,
      title: `${schedule.subject_name} - ${schedule.room_name}`,
      start,
      end,
      resource: schedule,
    };
  });

  const eventStyleGetter = (event: any) => {
    const colors = {
      lecture: { backgroundColor: '#3B82F6', borderColor: '#2563EB' },
      td: { backgroundColor: '#10B981', borderColor: '#059669' },
      lab: { backgroundColor: '#F59E0B', borderColor: '#D97706' },
      exam: { backgroundColor: '#EF4444', borderColor: '#DC2626' },
    };

    const type = event.resource?.subject?.subject_type || 'lecture';
    return {
      style: {
        ...colors[type as keyof typeof colors],
        color: 'white',
        border: 'none',
        borderRadius: '6px',
        fontSize: '12px',
        padding: '2px 6px',
      }
    };
  };

  const canCreateSchedule = ['admin', 'department_head', 'program_head'].includes(user?.role || '');

  if (isLoading) {
    return (
      <div className="flex items-center justify-center h-64">
        <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600"></div>
      </div>
    );
  }

  return (
    <div className="space-y-6">
      {/* Header */}
      <motion.div
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        className="flex flex-col sm:flex-row justify-between items-start sm:items-center gap-4"
      >
        <div>
          <h1 className="text-2xl font-bold text-gray-900">Emploi du temps</h1>
          <p className="text-gray-600">Gestion et consultation des plannings</p>
        </div>
        
        <div className="flex items-center space-x-3">
          <button className="flex items-center px-4 py-2 text-gray-600 bg-white border border-gray-300 rounded-lg hover:bg-gray-50 transition-colors">
            <Filter className="w-4 h-4 mr-2" />
            Filtrer
          </button>
          
          <button className="flex items-center px-4 py-2 text-gray-600 bg-white border border-gray-300 rounded-lg hover:bg-gray-50 transition-colors">
            <Download className="w-4 h-4 mr-2" />
            Exporter
          </button>
          
          {canCreateSchedule && (
            <motion.button
              whileHover={{ scale: 1.02 }}
              whileTap={{ scale: 0.98 }}
              onClick={() => setShowCreateModal(true)}
              className="flex items-center px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors"
            >
              <Plus className="w-4 h-4 mr-2" />
              Nouveau cours
            </motion.button>
          )}
        </div>
      </motion.div>

      {/* Calendar */}
      <motion.div
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ delay: 0.2 }}
        className="bg-white rounded-xl shadow-lg border border-gray-100 p-6"
      >
        <div style={{ height: '600px' }}>
          <Calendar
            localizer={localizer}
            events={events}
            startAccessor="start"
            endAccessor="end"
            style={{ height: '100%' }}
            view={view}
          
            date={currentDate}
            onNavigate={setCurrentDate}
            eventPropGetter={eventStyleGetter}
            messages={messages}
            min={new Date(2024, 0, 1, 8, 0)}
            max={new Date(2024, 0, 1, 18, 0)}
            step={30}
            timeslots={2}
            views={['month', 'week', 'day']}
            popup
            selectable={canCreateSchedule}
            onSelectSlot={(slotInfo: any) => {
              if (canCreateSchedule) {
                console.log('Slot selected:', slotInfo);
                setShowCreateModal(true);
              }
            }}
            onSelectEvent={(event: any) => {
              console.log('Event selected:', event);
            }}
          />
        </div>
      </motion.div>

      {/* Legend */}
      <motion.div
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ delay: 0.3 }}
        className="bg-white rounded-xl p-6 shadow-lg border border-gray-100"
      >
        <h3 className="text-lg font-semibold text-gray-900 mb-4">Légende</h3>
        <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
          <div className="flex items-center">
            <div className="w-4 h-4 bg-blue-500 rounded mr-2"></div>
            <span className="text-sm text-gray-700">Cours Magistral</span>
          </div>
          <div className="flex items-center">
            <div className="w-4 h-4 bg-green-500 rounded mr-2"></div>
            <span className="text-sm text-gray-700">Travaux Dirigés</span>
          </div>
          <div className="flex items-center">
            <div className="w-4 h-4 bg-yellow-500 rounded mr-2"></div>
            <span className="text-sm text-gray-700">Travaux Pratiques</span>
          </div>
          <div className="flex items-center">
            <div className="w-4 h-4 bg-red-500 rounded mr-2"></div>
            <span className="text-sm text-gray-700">Examens</span>
          </div>
        </div>
      </motion.div>
    </div>
  );
};