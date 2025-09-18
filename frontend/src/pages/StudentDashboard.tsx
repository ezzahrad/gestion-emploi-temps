import React from 'react';
import { motion } from 'framer-motion';
import { useQuery } from 'react-query';
import { 
  Calendar, 
  BookOpen, 
  Clock, 
  MapPin,
  Users,
  GraduationCap
} from 'lucide-react';
import { scheduleAPI } from '../services/api';
import { useAuth } from '../contexts/AuthContext';

export const StudentDashboard: React.FC = () => {
  useAuth();

  // Get student's program schedule for current week
  const { data: weekData, isLoading } = useQuery(
    'student-week-schedule',
    () => {
      const today = new Date();
      const weekStart = new Date(today.setDate(today.getDate() - today.getDay() + 1));
      const params = {
        week_start: weekStart.toISOString().split('T')[0],
      };
      return scheduleAPI.getScheduleByWeek(params).then((res: { data: any; }) => res.data);
    }
  );

  // Extract schedules from the API response structure
  const weekSchedules = React.useMemo(() => {
    if (!weekData || !weekData.days) return [];
    
    // Flatten all schedules from all days into a single array
    return weekData.days.reduce((allSchedules: any[], day: any) => {
      return allSchedules.concat(day.schedules || []);
    }, []);
  }, [weekData]);

  // Get today's schedule
  const today = new Date();
  const todaySchedules = weekSchedules.filter((schedule: any) => {
    return schedule.day_of_week === today.getDay();
  });

  // Get next course
  const now = new Date();
  const currentTime = now.getHours() * 60 + now.getMinutes();
  
  const nextCourse = todaySchedules.find((schedule: any) => {
    const [hour, minute] = schedule.start_time.split(':');
    const scheduleTime = parseInt(hour) * 60 + parseInt(minute);
    return scheduleTime > currentTime;
  });

  // Week statistics
  const weekStats = {
    totalHours: weekSchedules.reduce((sum: number, schedule: any) => {
      const start = new Date(`2000-01-01 ${schedule.start_time}`);
      const end = new Date(`2000-01-01 ${schedule.end_time}`);
      return sum + ((end.getTime() - start.getTime()) / (1000 * 60 * 60));
    }, 0),
    totalCourses: weekSchedules.length,
    subjects: new Set(weekSchedules.map((s: any) => s.subject_name)).size,
    teachers: new Set(weekSchedules.map((s: any) => s.teacher_name)).size,
  };

  return (
    <div className="space-y-6">
      {/* Welcome header */}
      <motion.div
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        className="bg-gradient-to-r from-purple-600 to-pink-600 rounded-2xl p-8 text-white"
      >
        <h1 className="text-3xl font-bold mb-2">
          Espace Étudiant
        </h1>
        <p className="text-purple-100 text-lg">
          Consultez votre emploi du temps et restez informé
        </p>
        <div className="mt-4 grid grid-cols-2 md:grid-cols-4 gap-4">
          <div className="text-center">
            <div className="text-2xl font-bold">{weekStats.totalHours}h</div>
            <div className="text-sm text-purple-200">Cette semaine</div>
          </div>
          <div className="text-center">
            <div className="text-2xl font-bold">{weekStats.totalCourses}</div>
            <div className="text-sm text-purple-200">Cours</div>
          </div>
          <div className="text-center">
            <div className="text-2xl font-bold">{weekStats.subjects}</div>
            <div className="text-sm text-purple-200">Matières</div>
          </div>
          <div className="text-center">
            <div className="text-2xl font-bold">{weekStats.teachers}</div>
            <div className="text-sm text-purple-200">Enseignants</div>
          </div>
        </div>
      </motion.div>

      {/* Next course */}
      {nextCourse && (
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.1 }}
          className="bg-gradient-to-r from-blue-50 to-indigo-50 border border-blue-200 rounded-xl p-6"
        >
          <div className="flex items-center mb-4">
            <Clock className="w-6 h-6 text-blue-600 mr-2" />
            <h2 className="text-xl font-bold text-gray-900">Prochain cours</h2>
          </div>
          <div className="bg-white rounded-lg p-4">
            <h3 className="font-semibold text-gray-900 text-lg mb-2">
              {nextCourse.subject_name}
            </h3>
            <div className="grid grid-cols-2 gap-4 text-sm">
              <div className="flex items-center text-gray-600">
                <Users className="w-4 h-4 mr-2" />
                {nextCourse.teacher_name}
              </div>
              <div className="flex items-center text-gray-600">
                <MapPin className="w-4 h-4 mr-2" />
                {nextCourse.room_name}
              </div>
              <div className="flex items-center text-gray-600">
                <Clock className="w-4 h-4 mr-2" />
                {nextCourse.start_time} - {nextCourse.end_time}
              </div>
              <div className="flex items-center text-gray-600">
                <GraduationCap className="w-4 h-4 mr-2" />
                {nextCourse.program_name}
              </div>
            </div>
          </div>
        </motion.div>
      )}

      {/* Today's schedule */}
      <motion.div
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ delay: 0.2 }}
        className="bg-white rounded-xl p-6 shadow-lg border border-gray-100"
      >
        <div className="flex items-center justify-between mb-6">
          <h2 className="text-xl font-bold text-gray-900 flex items-center">
            <Calendar className="w-6 h-6 mr-2 text-purple-600" />
            Planning d'aujourd'hui
          </h2>
          <span className="text-sm text-gray-500">
            {today.toLocaleDateString('fr-FR', { 
              weekday: 'long', 
              year: 'numeric', 
              month: 'long', 
              day: 'numeric' 
            })}
          </span>
        </div>

        {todaySchedules.length === 0 ? (
          <div className="text-center py-8">
            <Calendar className="w-12 h-12 text-gray-300 mx-auto mb-4" />
            <p className="text-gray-500">Aucun cours prévu aujourd'hui</p>
          </div>
        ) : (
          <div className="space-y-3">
            {todaySchedules.map((schedule: any) => (
              <div key={schedule.id} className="flex items-center justify-between p-4 bg-gray-50 rounded-lg hover:bg-gray-100 transition-colors">
                <div className="flex items-center">
                  <div className="w-3 h-3 bg-purple-500 rounded-full mr-4"></div>
                  <div>
                    <h3 className="font-medium text-gray-900">{schedule.subject_name}</h3>
                    <div className="flex items-center text-sm text-gray-600 mt-1">
                      <Users className="w-4 h-4 mr-1" />
                      {schedule.teacher_name}
                      <MapPin className="w-4 h-4 ml-4 mr-1" />
                      {schedule.room_name}
                    </div>
                  </div>
                </div>
                <div className="text-right">
                  <p className="text-sm font-medium text-gray-900">
                    {schedule.start_time} - {schedule.end_time}
                  </p>
                  <div className="flex items-center text-xs text-gray-500 mt-1">
                    <BookOpen className="w-3 h-3 mr-1" />
                    {schedule.subject?.subject_type === 'lecture' ? 'Cours' :
                     schedule.subject?.subject_type === 'td' ? 'TD' :
                     schedule.subject?.subject_type === 'lab' ? 'TP' : 'Examen'}
                  </div>
                </div>
              </div>
            ))}
          </div>
        )}
      </motion.div>

      {/* Weekly overview */}
      <motion.div
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ delay: 0.3 }}
        className="bg-white rounded-xl p-6 shadow-lg border border-gray-100"
      >
        <h3 className="text-lg font-semibold text-gray-900 mb-4 flex items-center">
          <Calendar className="w-5 h-5 mr-2 text-purple-600" />
          Aperçu de la semaine
        </h3>
        
        <div className="grid grid-cols-1 md:grid-cols-7 gap-4">
          {['Lun', 'Mar', 'Mer', 'Jeu', 'Ven', 'Sam', 'Dim'].map((day, index) => {
            const daySchedules = weekSchedules.filter((s: any) => s.day_of_week === index);
            const isToday = index === today.getDay();
            
            return (
              <div key={day} className={`p-3 rounded-lg ${isToday ? 'bg-purple-50 border-2 border-purple-200' : 'bg-gray-50'}`}>
                <h4 className={`text-sm font-medium mb-2 ${isToday ? 'text-purple-700' : 'text-gray-700'}`}>
                  {day}
                </h4>
                <div className="space-y-1">
                  {daySchedules.map((schedule: any) => (
                    <div key={schedule.id} className="text-xs bg-white rounded p-2 border">
                      <div className="font-medium">{schedule.subject_name}</div>
                      <div className="text-gray-500">{schedule.start_time}</div>
                    </div>
                  ))}
                  {daySchedules.length === 0 && (
                    <div className="text-xs text-gray-400 italic">Libre</div>
                  )}
                </div>
              </div>
            );
          })}
        </div>
      </motion.div>
    </div>
  );
};