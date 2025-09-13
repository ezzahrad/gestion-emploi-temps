// Layout.tsx - Layout DESKTOP FORCÉ - Utilisation complète de l'écran
import React, { useState, useEffect } from 'react';
import { Link, useLocation, useNavigate } from 'react-router-dom';
import { useAuth, roleDisplayNames, roleColors } from '../contexts/AuthContext';
import { 
  Menu, X, Calendar, Home, Users, BookOpen, MapPin, Settings,
  Upload, BarChart3, User, LogOut, Bell, Search,
  ChevronDown, Grid, Clock, Target, Maximize2, Minimize2,
  ChevronLeft, ChevronRight
} from 'lucide-react';
import { toast } from 'react-hot-toast';

interface LayoutProps {
  children: React.ReactNode;
}

interface NavigationItem {
  name: string;
  href: string;
  icon: React.ReactNode;
  permission?: string;
  roles?: string[];
  children?: NavigationItem[];
}

const Layout: React.FC<LayoutProps> = ({ children }) => {
  const { user, logout, hasRole, hasPermission } = useAuth();
  const location = useLocation();
  const navigate = useNavigate();
  
  const [sidebarExpanded, setSidebarExpanded] = useState(true);
  const [userMenuOpen, setUserMenuOpen] = useState(false);
  const [expandedMenus, setExpandedMenus] = useState<string[]>([]);

  // FORCER L'AFFICHAGE DESKTOP
  useEffect(() => {
    document.body.classList.add('force-desktop');
    document.documentElement.classList.add('force-desktop');
    
    return () => {
      document.body.classList.remove('force-desktop');
      document.documentElement.classList.remove('force-desktop');
    };
  }, []);

  // Configuration de navigation selon les rôles
  const getNavigationItems = (): NavigationItem[] => {
    const items: NavigationItem[] = [
      {
        name: 'Tableau de bord',
        href: '/dashboard',
        icon: <Home className="h-5 w-5" />
      },
      {
        name: 'Emploi du temps',
        href: '/schedule',
        icon: <Calendar className="h-5 w-5" />
      }
    ];

    // Navigation pour les administrateurs
    if (hasRole('admin')) {
      items.push(
        {
          name: 'Administration',
          href: '/admin',
          icon: <Settings className="h-5 w-5" />,
          children: [
            {
              name: 'Départements',
              href: '/admin/departments',
              icon: <Grid className="h-4 w-4" />
            },
            {
              name: 'Programmes',
              href: '/admin/programs',
              icon: <BookOpen className="h-4 w-4" />
            },
            {
              name: 'Enseignants',
              href: '/admin/teachers',
              icon: <Users className="h-4 w-4" />
            },
            {
              name: 'Étudiants',
              href: '/admin/students',
              icon: <Users className="h-4 w-4" />
            },
            {
              name: 'Salles',
              href: '/admin/rooms',
              icon: <MapPin className="h-4 w-4" />
            },
            {
              name: 'Matières',
              href: '/admin/subjects',
              icon: <BookOpen className="h-4 w-4" />
            }
          ]
        },
        {
          name: 'Outils',
          href: '/admin/tools',
          icon: <Target className="h-5 w-5" />,
          children: [
            {
              name: 'Génération EDT',
              href: '/admin/generate-timetable',
              icon: <Clock className="h-4 w-4" />
            },
            {
              name: 'Import Excel',
              href: '/admin/import-excel',
              icon: <Upload className="h-4 w-4" />
            },
            {
              name: 'Rapports',
              href: '/reports',
              icon: <BarChart3 className="h-4 w-4" />
            }
          ]
        }
      );
    }

    // Navigation pour les enseignants
    if (hasRole('teacher')) {
      items.push({
        name: 'Enseignement',
        href: '/teacher',
        icon: <BookOpen className="h-5 w-5" />,
        children: [
          {
            name: 'Mes cours',
            href: '/teacher/schedules',
            icon: <Calendar className="h-4 w-4" />
          },
          {
            name: 'Mes étudiants',
            href: '/teacher/students',
            icon: <Users className="h-4 w-4" />
          },
          {
            name: 'Disponibilités',
            href: '/teacher/availability',
            icon: <Clock className="h-4 w-4" />
          }
        ]
      });
    }

    // Navigation pour les étudiants
    if (hasRole('student')) {
      items.push({
        name: 'Mes études',
        href: '/student',
        icon: <BookOpen className="h-5 w-5" />,
        children: [
          {
            name: 'Mon programme',
            href: '/student/program',
            icon: <BookOpen className="h-4 w-4" />
          }
        ]
      });
    }

    // Éléments communs
    items.push({
      name: 'Profil & Paramètres',
      href: '/profile',
      icon: <User className="h-5 w-5" />,
      children: [
        {
          name: 'Mon profil',
          href: '/profile',
          icon: <User className="h-4 w-4" />
        },
        {
          name: 'Paramètres',
          href: '/settings',
          icon: <Settings className="h-4 w-4" />
        }
      ]
    });

    return items;
  };

  const handleLogout = async () => {
    try {
      await logout();
      navigate('/login');
      toast.success('Déconnexion réussie');
    } catch (error) {
      toast.error('Erreur lors de la déconnexion');
    }
  };

  const toggleExpanded = (itemName: string) => {
    setExpandedMenus(prev => 
      prev.includes(itemName) 
        ? prev.filter(name => name !== itemName)
        : [...prev, itemName]
    );
  };

  const renderNavigationItem = (item: NavigationItem, level = 0) => {
    const isActive = location.pathname === item.href || location.pathname.startsWith(item.href);
    const hasChildren = item.children && item.children.length > 0;
    const isExpanded = expandedMenus.includes(item.name);
    
    const itemClass = `
      flex items-center justify-between px-4 py-3 text-gray-700 hover:bg-gray-100 
      transition-all duration-200 rounded-lg mx-2 mb-1
      ${isActive ? 'bg-primary-100 text-primary-700 font-semibold' : ''}
      ${level > 0 ? 'ml-4 text-sm' : ''}
    `;

    return (
      <div key={item.name}>
        {hasChildren ? (
          <button
            onClick={() => toggleExpanded(item.name)}
            className={itemClass}
          >
            <div className="flex items-center">
              <span className="mr-3 flex-shrink-0">{item.icon}</span>
              {sidebarExpanded && (
                <span className="font-medium truncate">{item.name}</span>
              )}
            </div>
            {sidebarExpanded && (
              <ChevronDown 
                className={`h-4 w-4 transition-transform duration-200 ${
                  isExpanded ? 'transform rotate-180' : ''
                }`} 
              />
            )}
          </button>
        ) : (
          <Link to={item.href} className={itemClass}>
            <div className="flex items-center">
              <span className="mr-3 flex-shrink-0">{item.icon}</span>
              {sidebarExpanded && (
                <span className="font-medium truncate">{item.name}</span>
              )}
            </div>
          </Link>
        )}
        
        {hasChildren && isExpanded && sidebarExpanded && (
          <div className="ml-4 space-y-1">
            {item.children?.map(child => renderNavigationItem(child, level + 1))}
          </div>
        )}
      </div>
    );
  };

  const navigationItems = getNavigationItems();

  return (
    <div className="desktop-layout force-desktop">
      {/* SIDEBAR DESKTOP - TOUJOURS VISIBLE */}
      <aside className={`desktop-sidebar ${sidebarExpanded ? 'expanded' : 'collapsed'}`}>
        
        {/* Header Sidebar */}
        <div className="flex items-center justify-between p-4 border-b border-gray-200">
          {sidebarExpanded && (
            <div className="flex items-center">
              <div className="w-8 h-8 bg-gradient-to-br from-primary-500 to-primary-600 rounded-lg flex items-center justify-center">
                <Calendar className="h-5 w-5 text-white" />
              </div>
              <div className="ml-3">
                <h1 className="text-lg font-bold text-gray-900">AppGET</h1>
                <p className="text-xs text-gray-500">Gestion EDT</p>
              </div>
            </div>
          )}
          
          <button
            onClick={() => setSidebarExpanded(!sidebarExpanded)}
            className="p-2 rounded-lg hover:bg-gray-100 transition-colors"
            title={sidebarExpanded ? 'Réduire la barre latérale' : 'Étendre la barre latérale'}
          >
            {sidebarExpanded ? (
              <ChevronLeft className="h-5 w-5 text-gray-600" />
            ) : (
              <ChevronRight className="h-5 w-5 text-gray-600" />
            )}
          </button>
        </div>

        {/* Navigation */}
        <nav className="flex-1 overflow-y-auto py-4">
          <div className="space-y-1">
            {navigationItems.map(item => renderNavigationItem(item))}
          </div>
        </nav>

        {/* User Info en bas */}
        <div className="border-t border-gray-200 p-4">
          {sidebarExpanded ? (
            <div className="flex items-center">
              <div className="w-8 h-8 bg-gradient-to-br from-gray-400 to-gray-500 rounded-full flex items-center justify-center">
                <User className="h-4 w-4 text-white" />
              </div>
              <div className="ml-3 flex-1 min-w-0">
                <p className="text-sm font-medium text-gray-900 truncate">
                  {user?.first_name} {user?.last_name}
                </p>
                <p className={`text-xs truncate ${roleColors[user?.role || 'student']}`}>
                  {roleDisplayNames[user?.role || 'student']}
                </p>
              </div>
              <button
                onClick={handleLogout}
                className="p-1 text-gray-400 hover:text-red-500 transition-colors"
                title="Déconnexion"
              >
                <LogOut className="h-4 w-4" />
              </button>
            </div>
          ) : (
            <div className="flex flex-col items-center space-y-2">
              <div className="w-8 h-8 bg-gradient-to-br from-gray-400 to-gray-500 rounded-full flex items-center justify-center">
                <User className="h-4 w-4 text-white" />
              </div>
              <button
                onClick={handleLogout}
                className="p-1 text-gray-400 hover:text-red-500 transition-colors"
                title="Déconnexion"
              >
                <LogOut className="h-4 w-4" />
              </button>
            </div>
          )}
        </div>
      </aside>

      {/* CONTENU PRINCIPAL - UTILISE TOUTE LA LARGEUR RESTANTE */}
      <div className={`desktop-main ${sidebarExpanded ? '' : 'sidebar-collapsed'} force-full-width`}>
        
        {/* TOPBAR DESKTOP */}
        <header className="desktop-topbar">
          <div className="flex items-center">
            <h2 className="text-xl font-semibold text-gray-900">
              {location.pathname === '/dashboard' && 'Tableau de bord'}
              {location.pathname === '/schedule' && 'Emploi du temps'}
              {location.pathname.startsWith('/admin') && 'Administration'}
              {location.pathname.startsWith('/teacher') && 'Espace Enseignant'}
              {location.pathname.startsWith('/student') && 'Espace Étudiant'}
            </h2>
          </div>
          
          <div className="flex items-center space-x-4">
            {/* Barre de recherche étendue */}
            <div className="hidden lg:block">
              <div className="relative">
                <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 h-4 w-4 text-gray-400" />
                <input
                  type="text"
                  placeholder="Rechercher..."
                  className="pl-10 pr-4 py-2 border border-gray-300 rounded-lg text-sm focus:outline-none focus:ring-2 focus:ring-primary-500 focus:border-primary-500 w-64"
                />
              </div>
            </div>
            
            {/* Notifications */}
            <button className="p-2 text-gray-400 hover:text-gray-600 transition-colors relative">
              <Bell className="h-5 w-5" />
              <span className="absolute -top-1 -right-1 h-4 w-4 bg-red-500 rounded-full flex items-center justify-center text-xs text-white">
                3
              </span>
            </button>
            
            {/* User Menu */}
            <div className="relative">
              <button
                onClick={() => setUserMenuOpen(!userMenuOpen)}
                className="flex items-center space-x-2 p-2 rounded-lg hover:bg-gray-100 transition-colors"
              >
                <div className="w-8 h-8 bg-gradient-to-br from-primary-400 to-primary-500 rounded-full flex items-center justify-center">
                  <User className="h-4 w-4 text-white" />
                </div>
                <div className="hidden md:block text-left">
                  <p className="text-sm font-medium text-gray-900">
                    {user?.first_name} {user?.last_name}
                  </p>
                  <p className={`text-xs ${roleColors[user?.role || 'student']}`}>
                    {roleDisplayNames[user?.role || 'student']}
                  </p>
                </div>
                <ChevronDown className="h-4 w-4 text-gray-400" />
              </button>
              
              {userMenuOpen && (
                <div className="absolute right-0 mt-2 w-48 bg-white rounded-lg shadow-lg border border-gray-200 py-1 z-50">
                  <Link
                    to="/profile"
                    className="flex items-center px-4 py-2 text-sm text-gray-700 hover:bg-gray-100"
                    onClick={() => setUserMenuOpen(false)}
                  >
                    <User className="h-4 w-4 mr-2" />
                    Mon profil
                  </Link>
                  <Link
                    to="/settings"
                    className="flex items-center px-4 py-2 text-sm text-gray-700 hover:bg-gray-100"
                    onClick={() => setUserMenuOpen(false)}
                  >
                    <Settings className="h-4 w-4 mr-2" />
                    Paramètres
                  </Link>
                  <hr className="my-1 border-gray-200" />
                  <button
                    onClick={() => {
                      setUserMenuOpen(false);
                      handleLogout();
                    }}
                    className="flex items-center w-full px-4 py-2 text-sm text-red-600 hover:bg-red-50"
                  >
                    <LogOut className="h-4 w-4 mr-2" />
                    Déconnexion
                  </button>
                </div>
              )}
            </div>
          </div>
        </header>

        {/* CONTENU PRINCIPAL - LARGEUR COMPLÈTE */}
        <main className="desktop-content force-full-width">
          {children}
        </main>
      </div>

      {/* Click outside handler pour fermer les menus */}
      {userMenuOpen && (
        <div
          className="fixed inset-0 z-40"
          onClick={() => setUserMenuOpen(false)}
        />
      )}
    </div>
  );
};

export default Layout;