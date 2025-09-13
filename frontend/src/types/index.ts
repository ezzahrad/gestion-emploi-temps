export interface User {
  id: number;
  email: string;
  username: string;
  first_name: string;
  last_name: string;
  full_name: string;
  role: 'admin' | 'department_head' | 'program_head' | 'teacher' | 'student';
  department?: number;
  program?: number;
  phone_number?: string;
  is_active: boolean;
  created_at: string;
}

export interface Department {
  id: number;
  name: string;
  code: string;
  description?: string;
  head?: number;
  head_name?: string;
  programs_count: number;
  created_at: string;
  updated_at: string;
}

export interface Program {
  id: number;
  name: string;
  code: string;
  department: number;
  department_name: string;
  level: 'L1' | 'L2' | 'L3' | 'M1' | 'M2';
  head?: number;
  head_name?: string;
  capacity: number;
  students_count: number;
  created_at: string;
  updated_at: string;
}

export interface Room {
  id: number;
  name: string;
  code: string;
  room_type: 'lecture' | 'td' | 'lab' | 'amphitheater';
  capacity: number;
  department: number;
  department_name: string;
  equipment?: string;
  is_available: boolean;
  created_at: string;
  updated_at: string;
}

export interface Subject {
  id: number;
  name: string;
  code: string;
  department: number;
  department_name: string;
  program: number[];
  subject_type: 'lecture' | 'td' | 'lab' | 'exam';
  credits: number;
  hours_per_week: number;
  semester: number;
  description?: string;
  teachers_count: number;
  created_at: string;
  updated_at: string;
}

export interface Schedule {
  id: number;
  title: string;
  subject: number;
  subject_name: string;
  teacher: number;
  teacher_name: string;
  room: number;
  room_name: string;
  program: number;
  program_name: string;
  day_of_week: number;
  day_name: string;
  start_time: string;
  end_time: string;
  week_start: string;
  week_end: string;
  is_active: boolean;
  notes?: string;
  created_by?: number;
  created_at: string;
  updated_at: string;
}

export interface Notification {
  id: number;
  title: string;
  message: string;
  notification_type: 'schedule_change' | 'absence' | 'makeup' | 'conflict' | 'reminder' | 'system';
  priority: 'low' | 'medium' | 'high' | 'urgent';
  is_read: boolean;
  time_ago: string;
  created_at: string;
}

export interface DashboardStats {
  total_departments?: number;
  total_programs?: number;
  total_teachers?: number;
  total_students?: number;
  total_subjects?: number;
  total_rooms?: number;
  department_programs?: number;
  department_teachers?: number;
  department_students?: number;
  department_subjects?: number;
  department_rooms?: number;
  program_students?: number;
  program_subjects?: number;
}