import React, { useState, useEffect, useCallback, useRef } from "react";
import {
  ChevronLeft,
  ChevronRight,
  Plus,
  Filter,
  Search,
  AlertTriangle,
  Info,
} from "lucide-react";

interface CalendarEvent {
  id: string;
  title: string;
  description?: string;
  subject: {
    id: string;
    name: string;
    code: string;
    color: string;
  };
  teacher: {
    id: string;
    name: string;
    avatar?: string;
  };
  room: {
    id: string;
    name: string;
    capacity: number;
    building: string;
  };
  programs: Array<{
    id: string;
    name: string;
    studentsCount: number;
  }>;
  startTime: string;
  endTime: string;
  date: string;
  duration: number; // in minutes
  type: "CM" | "TD" | "TP" | "EXAM" | "PROJECT";
  status: "scheduled" | "ongoing" | "completed" | "cancelled" | "conflict";
  conflicts?: ConflictInfo[];
  isRecurring?: boolean;
  recurringPattern?: string;
  attendees?: number;
  notes?: string;
  createdBy: string;
  lastModified: string;
}

interface ConflictInfo {
  type:
    | "teacher_conflict"
    | "room_conflict"
    | "student_conflict"
    | "capacity_exceeded";
  severity: "low" | "medium" | "high" | "critical";
  message: string;
  conflictingEvent?: {
    id: string;
    title: string;
    time: string;
  };
}

interface CalendarFilter {
  teachers: string[];
  rooms: string[];
  programs: string[];
  subjects: string[];
  types: string[];
  showConflicts: boolean;
  showCompleted: boolean;
}

interface CalendarView {
  mode: "day" | "week" | "month" | "agenda";
  date: Date;
  timeRange: {
    start: string;
    end: string;
  };
}

const InteractiveCalendar: React.FC = () => {
  const [events, setEvents] = useState<CalendarEvent[]>([]);
  const [filteredEvents, setFilteredEvents] = useState<CalendarEvent[]>([]);
  const [view, setView] = useState<CalendarView>({
    mode: "week",
    date: new Date(),
    timeRange: { start: "08:00", end: "18:00" },
  });
  const [filters, setFilters] = useState<CalendarFilter>({
    teachers: [],
    rooms: [],
    programs: [],
    subjects: [],
    types: [],
    showConflicts: true,
    showCompleted: false,
  });
  const [draggedEvent, setDraggedEvent] = useState<CalendarEvent | null>(null);
  const [showFilters, setShowFilters] = useState(false);
  const [searchTerm, setSearchTerm] = useState("");
  const calendarRef = useRef<HTMLDivElement>(null);

  const timeSlots: string[] = [];
  for (let hour = 8; hour <= 18; hour++) {
    timeSlots.push(`${hour.toString().padStart(2, "0")}:00`);
    timeSlots.push(`${hour.toString().padStart(2, "0")}:30`);
  }
  const daysOfWeek = [
    "Lundi",
    "Mardi",
    "Mercredi",
    "Jeudi",
    "Vendredi",
    "Samedi",
    "Dimanche",
  ];

  useEffect(() => {
    loadEvents();
    const interval = setInterval(loadEvents, 30000);
    return () => clearInterval(interval);
  }, [view.date]);

  useEffect(() => {
    filterEvents();
  }, [events, filters, searchTerm]);

  const loadEvents = async () => {
    try {
      await new Promise((resolve) => setTimeout(resolve, 500));
      const mockEvents: CalendarEvent[] = [
        {
          id: "event_001",
          title: "Programmation Orientée Objet",
          description: "Introduction aux concepts de la POO avec Java",
          subject: {
            id: "subj_001",
            name: "POO",
            code: "POO101",
            color: "#3B82F6",
          },
          teacher: {
            id: "teacher_001",
            name: "Prof. Fatima Alami",
            avatar: "/avatars/alami.jpg",
          },
          room: {
            id: "room_001",
            name: "AMPH-A",
            capacity: 150,
            building: "Bâtiment Principal",
          },
          programs: [
            { id: "prog_001", name: "L3 Informatique", studentsCount: 85 },
          ],
          startTime: "08:00",
          endTime: "10:00",
          date: "2024-12-09",
          duration: 120,
          type: "CM",
          status: "scheduled",
          attendees: 85,
          createdBy: "admin",
          lastModified: "2024-12-08T15:30:00Z",
        },
      ];
      setEvents(mockEvents);
    } catch (e) {
      console.error("Erreur lors du chargement des événements:", e);
    }
  };

  const filterEvents = () => {
    let filtered = events;
    if (searchTerm) {
      filtered = filtered.filter(
        (event) =>
          event.title.toLowerCase().includes(searchTerm.toLowerCase()) ||
          event.subject.name.toLowerCase().includes(searchTerm.toLowerCase()) ||
          event.teacher.name.toLowerCase().includes(searchTerm.toLowerCase()) ||
          event.room.name.toLowerCase().includes(searchTerm.toLowerCase())
      );
    }
    if (filters.teachers.length > 0)
      filtered = filtered.filter((e) =>
        filters.teachers.includes(e.teacher.id)
      );
    if (filters.rooms.length > 0)
      filtered = filtered.filter((e) => filters.rooms.includes(e.room.id));
    if (filters.types.length > 0)
      filtered = filtered.filter((e) => filters.types.includes(e.type));
    if (!filters.showConflicts)
      filtered = filtered.filter((e) => e.status !== "conflict");
    if (!filters.showCompleted)
      filtered = filtered.filter((e) => e.status !== "completed");
    setFilteredEvents(filtered);
  };

  // Collaboration simulée omise dans cette version allégée

  const handleEventClick = (_event: CalendarEvent) => {
    // Ouvrir un panneau de détails (omis dans cette version)
  };
  const handleEventDrag = useCallback((event: CalendarEvent) => {
    setDraggedEvent(event);
  }, []);
  const addMinutesToTime = (time: string, minutes: number): string => {
    const [h, m] = time.split(":").map(Number);
    const total = h * 60 + m + minutes;
    const nh = Math.floor(total / 60);
    const nm = total % 60;
    return `${nh.toString().padStart(2, "0")}:${nm
      .toString()
      .padStart(2, "0")}`;
  };
  const handleEventDrop = useCallback(
    (event: CalendarEvent, newDate: string, newTime: string) => {
      setEvents((prev) =>
        prev.map((e) =>
          e.id === event.id
            ? {
                ...e,
                date: newDate,
                startTime: newTime,
                endTime: addMinutesToTime(newTime, e.duration),
                lastModified: new Date().toISOString(),
              }
            : e
        )
      );
      setDraggedEvent(null);
    },
    []
  );

  const timeToMinutes = (time: string) => {
    const [h, m] = time.split(":").map(Number);
    return h * 60 + m;
  };

  const navigateDate = (direction: "prev" | "next") => {
    const newDate = new Date(view.date);
    switch (view.mode) {
      case "day":
        newDate.setDate(newDate.getDate() + (direction === "next" ? 1 : -1));
        break;
      case "week":
        newDate.setDate(newDate.getDate() + (direction === "next" ? 7 : -7));
        break;
      case "month":
        newDate.setMonth(newDate.getMonth() + (direction === "next" ? 1 : -1));
        break;
    }
    setView((prev) => ({ ...prev, date: newDate }));
  };

  const getWeekDates = (date: Date) => {
    const start = new Date(date);
    const day = start.getDay();
    const diff = start.getDate() - day + (day === 0 ? -6 : 1);
    start.setDate(diff);
    const dates: Date[] = [];
    for (let i = 0; i < 7; i++) {
      const d = new Date(start);
      d.setDate(start.getDate() + i);
      dates.push(d);
    }
    return dates;
  };

  const formatDate = (date: Date) => date.toISOString().split("T")[0];

  const getEventStyle = (event: CalendarEvent) => ({
    backgroundColor: event.subject.color,
    borderLeft: `4px solid ${event.subject.color}`,
    opacity: event.status === "completed" ? 0.6 : 1,
    borderColor: event.status === "conflict" ? "#EF4444" : event.subject.color,
  });

  const getConflictIcon = (severity: string) => {
    switch (severity) {
      case "critical":
        return <AlertTriangle className="w-4 h-4 text-red-600" />;
      case "high":
        return <AlertTriangle className="w-4 h-4 text-orange-600" />;
      case "medium":
        return <AlertTriangle className="w-4 h-4 text-yellow-600" />;
      default:
        return <Info className="w-4 h-4 text-blue-600" />;
    }
  };

  const renderWeekView = () => {
    const weekDates = getWeekDates(view.date);
    return (
      <div className="flex flex-col h-full">
        <div className="grid grid-cols-8 border-b border-gray-200">
          <div className="p-4 bg-gray-50 border-r border-gray-200">
            <span className="text-sm font-medium text-gray-700">Heure</span>
          </div>
          {weekDates.map((date, index) => (
            <div
              key={index}
              className="p-4 bg-gray-50 border-r border-gray-200 text-center"
            >
              <div className="text-sm font-medium text-gray-700">
                {daysOfWeek[index]}
              </div>
              <div className="text-lg font-bold text-gray-900">
                {date.getDate()}
              </div>
            </div>
          ))}
        </div>
        <div className="flex-1 overflow-auto">
          <div className="grid grid-cols-8 h-full">
            <div className="border-r border-gray-200">
              {timeSlots.map((time, index) => (
                <div
                  key={index}
                  className="h-16 border-b border-gray-100 flex items-center justify-center text-sm text-gray-600"
                >
                  {time}
                </div>
              ))}
            </div>
            {weekDates.map((date, dayIndex) => (
              <div key={dayIndex} className="border-r border-gray-200 relative">
                {timeSlots.map((time, timeIndex) => (
                  <div
                    key={timeIndex}
                    className="h-16 border-b border-gray-100 relative"
                    onDragOver={(e) => e.preventDefault()}
                    onDrop={(e) => {
                      e.preventDefault();
                      if (draggedEvent)
                        handleEventDrop(draggedEvent, formatDate(date), time);
                    }}
                  >
                    {filteredEvents
                      .filter(
                        (event) =>
                          event.date === formatDate(date) &&
                          event.startTime <= time &&
                          addMinutesToTime(time, 30) <= event.endTime
                      )
                      .map((event) => {
                        const eventStart = timeToMinutes(event.startTime);
                        const slotStart = timeToMinutes(time);
                        const isFirstSlot =
                          eventStart >= slotStart &&
                          eventStart < slotStart + 30;
                        if (!isFirstSlot) return null;
                        const eventHeight = (event.duration / 30) * 64;
                        return (
                          <div
                            key={event.id}
                            className="absolute left-1 right-1 bg-white rounded shadow-sm border cursor-pointer hover:shadow-md transition-shadow"
                            style={{
                              ...getEventStyle(event),
                              height: `${eventHeight - 4}px`,
                              zIndex: 10,
                            }}
                            onClick={() => handleEventClick(event)}
                            draggable
                            onDragStart={() => handleEventDrag(event)}
                          >
                            <div className="p-2 text-xs">
                              <div className="font-medium text-white truncate">
                                {event.title}
                              </div>
                              <div className="text-white opacity-90 truncate">
                                {event.teacher.name}
                              </div>
                              <div className="text-white opacity-90 truncate">
                                {event.room.name}
                              </div>
                              {event.conflicts &&
                                event.conflicts.length > 0 && (
                                  <div className="mt-1">
                                    {getConflictIcon(
                                      event.conflicts[0].severity
                                    )}
                                  </div>
                                )}
                            </div>
                          </div>
                        );
                      })}
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
      <div className="bg-white border-b border-gray-200 p-4">
        <div className="flex items-center justify-between">
          <div className="flex items-center space-x-4">
            <div className="flex items-center space-x-2">
              <button
                onClick={() => navigateDate("prev")}
                className="p-2 hover:bg-gray-100 rounded-lg"
              >
                <ChevronLeft className="w-5 h-5" />
              </button>
              <button
                onClick={() =>
                  setView((prev) => ({ ...prev, date: new Date() }))
                }
                className="px-4 py-2 text-lg font-semibold text-gray-900 hover:bg-gray-100 rounded-lg"
              >
                {view.mode === "month"
                  ? view.date.toLocaleDateString("fr-FR", {
                      month: "long",
                      year: "numeric",
                    })
                  : view.mode === "week"
                  ? `Semaine du ${getWeekDates(view.date)[0].toLocaleDateString(
                      "fr-FR",
                      { day: "numeric", month: "short" }
                    )}`
                  : view.date.toLocaleDateString("fr-FR", {
                      weekday: "long",
                      day: "numeric",
                      month: "long",
                    })}
              </button>
              <button
                onClick={() => navigateDate("next")}
                className="p-2 hover:bg-gray-100 rounded-lg"
              >
                <ChevronRight className="w-5 h-5" />
              </button>
            </div>
            <div className="flex space-x-1 bg-gray-100 rounded-lg p-1">
              {[
                { id: "day", label: "Jour" },
                { id: "week", label: "Semaine" },
                { id: "month", label: "Mois" },
                { id: "agenda", label: "Agenda" },
              ].map((mode) => (
                <button
                  key={mode.id}
                  onClick={() =>
                    setView((prev) => ({ ...prev, mode: mode.id as any }))
                  }
                  className={`px-3 py-2 text-sm font-medium rounded-md transition-colors ${
                    view.mode === mode.id
                      ? "bg-white text-blue-600 shadow-sm"
                      : "text-gray-600 hover:text-gray-900"
                  }`}
                >
                  {mode.label}
                </button>
              ))}
            </div>
          </div>
          <div className="flex items-center space-x-3">
            <div className="relative">
              <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 w-4 h-4 text-gray-400" />
              <input
                type="text"
                placeholder="Rechercher..."
                value={searchTerm}
                onChange={(e) => setSearchTerm(e.target.value)}
                className="pl-9 pr-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent w-64"
              />
            </div>
            <button
              onClick={() => setShowFilters(!showFilters)}
              className="px-4 py-2 border border-gray-300 rounded-lg hover:bg-gray-50 flex items-center"
            >
              <Filter className="w-4 h-4 mr-2" />
              Filtres
            </button>
            <button className="px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 flex items-center">
              <Plus className="w-4 h-4 mr-2" />
              Nouveau cours
            </button>
          </div>
        </div>
        {showFilters && (
          <div className="mt-4 p-4 bg-gray-50 rounded-lg border">
            <div className="grid grid-cols-2 md:grid-cols-5 gap-4">
              <div className="flex items-center">
                <input
                  type="checkbox"
                  id="showConflicts"
                  checked={filters.showConflicts}
                  onChange={(e) =>
                    setFilters((prev) => ({
                      ...prev,
                      showConflicts: e.target.checked,
                    }))
                  }
                  className="h-4 w-4 text-blue-600 focus:ring-blue-500 border-gray-300 rounded"
                />
                <label
                  htmlFor="showConflicts"
                  className="ml-2 text-sm text-gray-700"
                >
                  Afficher conflits
                </label>
              </div>
              <div className="flex items-center">
                <input
                  type="checkbox"
                  id="showCompleted"
                  checked={filters.showCompleted}
                  onChange={(e) =>
                    setFilters((prev) => ({
                      ...prev,
                      showCompleted: e.target.checked,
                    }))
                  }
                  className="h-4 w-4 text-blue-600 focus:ring-blue-500 border-gray-300 rounded"
                />
                <label
                  htmlFor="showCompleted"
                  className="ml-2 text-sm text-gray-700"
                >
                  Afficher terminés
                </label>
              </div>
              <select
                className="px-3 py-2 text-sm border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500"
                value=""
                onChange={(e) => {
                  if (e.target.value) {
                    setFilters((prev) => ({
                      ...prev,
                      types: [...prev.types, e.target.value],
                    }));
                  }
                }}
              >
                <option value="">Type de cours</option>
                <option value="CM">Cours Magistral</option>
                <option value="TD">Travaux Dirigés</option>
                <option value="TP">Travaux Pratiques</option>
                <option value="EXAM">Examen</option>
                <option value="PROJECT">Projet</option>
              </select>
              <button
                onClick={() =>
                  setFilters({
                    teachers: [],
                    rooms: [],
                    programs: [],
                    subjects: [],
                    types: [],
                    showConflicts: true,
                    showCompleted: false,
                  })
                }
                className="px-3 py-2 text-sm border border-gray-300 rounded-lg hover:bg-gray-50"
              >
                Réinitialiser
              </button>
            </div>
          </div>
        )}
      </div>
      <div className="flex-1 overflow-hidden" ref={calendarRef}>
        {view.mode === "week" && renderWeekView()}
        {view.mode === "agenda" && (
          <div className="p-8 text-center text-gray-500">
            Vue agenda en développement
          </div>
        )}
        {view.mode === "day" && (
          <div className="p-8 text-center text-gray-500">
            Vue jour en développement
          </div>
        )}
        {view.mode === "month" && (
          <div className="p-8 text-center text-gray-500">
            Vue mois en développement
          </div>
        )}
      </div>
    </div>
  );
};

export default InteractiveCalendar;
