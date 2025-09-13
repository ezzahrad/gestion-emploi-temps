from datetime import datetime
from django.db.models import Q
from .models import Schedule
from core.models import Room, TeacherAvailability
from core.serializers import RoomSerializer

def check_conflicts(teacher_id, room_id, day_of_week, start_time, end_time, week_start, week_end, exclude_id=None):
    """Check for scheduling conflicts"""
    conflicts = []
    
    # Convert string times to time objects if needed
    if isinstance(start_time, str):
        start_time = datetime.strptime(start_time, '%H:%M').time()
    if isinstance(end_time, str):
        end_time = datetime.strptime(end_time, '%H:%M').time()
    
    # Check room conflicts
    room_conflicts = Schedule.objects.filter(
        room_id=room_id,
        day_of_week=day_of_week,
        week_start=week_start,
        week_end=week_end,
        is_active=True
    )
    
    if exclude_id:
        room_conflicts = room_conflicts.exclude(id=exclude_id)
    
    for conflict in room_conflicts:
        if start_time < conflict.end_time and end_time > conflict.start_time:
            conflicts.append({
                'type': 'room',
                'message': f'Conflit de salle avec le cours "{conflict.title}"',
                'schedule': {
                    'id': conflict.id,
                    'title': conflict.title,
                    'start_time': conflict.start_time.strftime('%H:%M'),
                    'end_time': conflict.end_time.strftime('%H:%M')
                }
            })
    
    # Check teacher conflicts
    teacher_conflicts = Schedule.objects.filter(
        teacher_id=teacher_id,
        day_of_week=day_of_week,
        week_start=week_start,
        week_end=week_end,
        is_active=True
    )
    
    if exclude_id:
        teacher_conflicts = teacher_conflicts.exclude(id=exclude_id)
    
    for conflict in teacher_conflicts:
        if start_time < conflict.end_time and end_time > conflict.start_time:
            conflicts.append({
                'type': 'teacher',
                'message': f'Conflit enseignant avec le cours "{conflict.title}"',
                'schedule': {
                    'id': conflict.id,
                    'title': conflict.title,
                    'start_time': conflict.start_time.strftime('%H:%M'),
                    'end_time': conflict.end_time.strftime('%H:%M')
                }
            })
    
    # Check teacher availability
    try:
        availability = TeacherAvailability.objects.filter(
            teacher_id=teacher_id,
            day_of_week=day_of_week,
            is_available=True
        ).first()
        
        if availability:
            if not (start_time >= availability.start_time and end_time <= availability.end_time):
                conflicts.append({
                    'type': 'availability',
                    'message': f'L\'enseignant n\'est pas disponible à ces heures',
                    'available_hours': {
                        'start': availability.start_time.strftime('%H:%M'),
                        'end': availability.end_time.strftime('%H:%M')
                    }
                })
    except Exception:
        pass
    
    return conflicts

def get_available_rooms(day_of_week, start_time, end_time, week_start, week_end, room_type=None):
    """Get available rooms for a specific time slot"""
    # Convert string times to time objects if needed
    if isinstance(start_time, str):
        start_time = datetime.strptime(start_time, '%H:%M').time()
    if isinstance(end_time, str):
        end_time = datetime.strptime(end_time, '%H:%M').time()
    
    # Get all rooms
    rooms = Room.objects.filter(is_available=True)
    
    if room_type:
        rooms = rooms.filter(room_type=room_type)
    
    # Get rooms that have conflicts
    conflicted_rooms = Schedule.objects.filter(
        day_of_week=day_of_week,
        week_start=week_start,
        week_end=week_end,
        is_active=True
    ).filter(
        Q(start_time__lt=end_time) & Q(end_time__gt=start_time)
    ).values_list('room_id', flat=True)
    
    # Exclude conflicted rooms
    available_rooms = rooms.exclude(id__in=conflicted_rooms)
    
    return RoomSerializer(available_rooms, many=True).data

def generate_schedule_suggestions(conflicts):
    """Generate suggestions to resolve conflicts"""
    suggestions = []
    
    for conflict in conflicts:
        if conflict['type'] == 'room':
            # Suggest alternative rooms
            suggestions.append({
                'type': 'alternative_room',
                'message': 'Salles alternatives disponibles',
                'action': 'change_room'
            })
        elif conflict['type'] == 'teacher':
            # Suggest alternative time slots
            suggestions.append({
                'type': 'alternative_time',
                'message': 'Créneaux horaires alternatifs',
                'action': 'change_time'
            })
    
    return suggestions