// ===== TYPES ÉTENDUS POUR LES NOUVELLES FONCTIONNALITÉS =====

// 1. NOTIFICATIONS AVANCÉES
export interface NotificationEnhanced {
  id: number;
  title: string;
  message: string;
  notification_type: 'schedule_change' | 'absence' | 'makeup' | 'conflict' | 'reminder' | 'system' | 'grade' | 'evaluation';
  priority: 'low' | 'medium' | 'high' | 'urgent';
  is_read: boolean;
  is_sent: boolean;
  metadata: {
    schedule_id?: number;
    absence_id?: number;
    grade_id?: number;
    action_url?: string;
    expires_at?: string;
  };
  time_ago: string;
  created_at: string;
  read_at?: string;
}

export interface NotificationSettings {
  email_notifications: boolean;
  push_notifications: boolean;
  schedule_changes: boolean;
  absence_reminders: boolean;
  grade_updates: boolean;
  system_announcements: boolean;
  makeup_requests: boolean;
}

// 2. ABSENCES ET RATTRAPAGES
export interface Absence {
  id: number;
  student: number;
  student_name: string;
  schedule: number;
  schedule_details: {
    subject_name: string;
    teacher_name: string;
    room_name: string;
    date: string;
    start_time: string;
    end_time: string;
  };
  absence_type: 'justified' | 'unjustified' | 'medical' | 'family' | 'other';
  reason: string;
  justification_document?: string;
  status: 'pending' | 'approved' | 'rejected';
  is_makeup_required: boolean;
  makeup_completed: boolean;
  created_at: string;
  approved_at?: string;
  approved_by?: number;
}

export interface MakeupSession {
  id: number;
  absence: number;
  absence_details: Absence;
  original_schedule: number;
  makeup_date: string;
  makeup_start_time: string;
  makeup_end_time: string;
  room: number;
  room_name: string;
  teacher: number;
  teacher_name: string;
  status: 'scheduled' | 'completed' | 'cancelled' | 'rescheduled';
  attendance_confirmed: boolean;
  notes?: string;
  created_at: string;
  updated_at: string;
}

// 3. NOTES ET ÉVALUATIONS
export interface Grade {
  id: number;
  student: number;
  student_name: string;
  subject: number;
  subject_name: string;
  evaluation_type: 'exam' | 'quiz' | 'homework' | 'project' | 'participation' | 'final';
  grade_value: number;
  max_grade: number;
  percentage: number;
  grade_letter: 'A+' | 'A' | 'B+' | 'B' | 'C+' | 'C' | 'D+' | 'D' | 'F';
  coefficient: number;
  evaluation_date: string;
  teacher: number;
  teacher_name: string;
  comments?: string;
  is_published: boolean;
  created_at: string;
  updated_at: string;
}

export interface SubjectGrades {
  subject_id: number;
  subject_name: string;
  subject_code: string;
  teacher_name: string;
  credits: number;
  grades: Grade[];
  average: number;
  grade_letter: string;
  total_coefficient: number;
}

export interface StudentTranscript {
  student_id: number;
  student_name: string;
  program_name: string;
  level: string;
  semester: number;
  academic_year: string;
  subjects: SubjectGrades[];
  overall_average: number;
  overall_grade_letter: string;
  total_credits: number;
  acquired_credits: number;
  gpa: number;
  rank?: number;
  total_students?: number;
}

// 4. EXPORT PDF
export interface PDFExportOptions {
  type: 'schedule' | 'transcript' | 'absence_report' | 'attendance_report';
  format: 'A4' | 'A3' | 'Letter';
  orientation: 'portrait' | 'landscape';
  date_range?: {
    start_date: string;
    end_date: string;
  };
  include_details: boolean;
  include_statistics: boolean;
  watermark?: string;
  language: 'fr' | 'en' | 'ar';
}

export interface PDFGenerationStatus {
  id: string;
  status: 'pending' | 'processing' | 'completed' | 'failed';
  progress: number;
  download_url?: string;
  error_message?: string;
  created_at: string;
  completed_at?: string;
}

// 5. STATISTIQUES ÉTENDUES
export interface StudentStats {
  total_absences: number;
  justified_absences: number;
  unjustified_absences: number;
  absence_rate: number;
  pending_makeups: number;
  completed_makeups: number;
  current_average: number;
  subjects_count: number;
  credits_acquired: number;
  credits_total: number;
  attendance_rate: number;
  grade_trend: 'improving' | 'stable' | 'declining';
}

export interface AttendanceRecord {
  id: number;
  student: number;
  schedule: number;
  schedule_details: {
    subject_name: string;
    date: string;
    start_time: string;
    end_time: string;
  };
  status: 'present' | 'absent' | 'late' | 'excused';
  arrival_time?: string;
  notes?: string;
  recorded_by: number;
  recorded_at: string;
}

// 6. CONFIGURATION SYSTÈME
export interface SystemSettings {
  notification_settings: NotificationSettings;
  grade_scale: {
    A_plus: number;
    A: number;
    B_plus: number;
    B: number;
    C_plus: number;
    C: number;
    D_plus: number;
    D: number;
    F: number;
  };
  absence_policies: {
    max_unjustified_absences: number;
    makeup_deadline_days: number;
    justification_required_hours: number;
  };
  academic_calendar: {
    semester_start: string;
    semester_end: string;
    exam_period_start: string;
    exam_period_end: string;
    holidays: Array<{
      name: string;
      start_date: string;
      end_date: string;
    }>;
  };
}

// 7. ÉVÉNEMENTS EN TEMPS RÉEL
export interface RealTimeEvent {
  type: 'notification' | 'schedule_update' | 'grade_published' | 'absence_reported';
  data: any;
  timestamp: string;
  user_id: number;
}

export interface WebSocketMessage {
  event_type: string;
  data: RealTimeEvent;
  user_id?: number;
  room?: string;
}
