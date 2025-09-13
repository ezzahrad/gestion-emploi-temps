// Breadcrumb.tsx - Composant de navigation fil d'Ariane
import React from 'react';
import { Link } from 'react-router-dom';
import { ChevronRight, Home } from 'lucide-react';

export interface BreadcrumbItem {
  label: string;
  href?: string;
  icon?: React.ReactNode;
  current?: boolean;
}

export interface BreadcrumbProps {
  items: BreadcrumbItem[];
  separator?: React.ReactNode;
  showHome?: boolean;
  homeHref?: string;
  className?: string;
  maxItems?: number;
}

export const Breadcrumb: React.FC<BreadcrumbProps> = ({
  items,
  separator = <ChevronRight className="h-4 w-4 text-gray-400" />,
  showHome = true,
  homeHref = '/',
  className = '',
  maxItems
}) => {
  // Gérer le nombre maximum d'éléments affichés
  const displayItems = React.useMemo(() => {
    if (!maxItems || items.length <= maxItems) {
      return items;
    }

    // Si on dépasse, on garde le premier, on ajoute "...", et les derniers
    const firstItems = items.slice(0, 1);
    const lastItems = items.slice(-(maxItems - 2));
    
    return [
      ...firstItems,
      { label: '...', current: false },
      ...lastItems
    ];
  }, [items, maxItems]);

  return (
    <nav className={`flex ${className}`} aria-label="Breadcrumb">
      <ol className="flex items-center space-x-2">
        {/* Home link */}
        {showHome && (
          <li>
            <Link
              to={homeHref}
              className="text-gray-400 hover:text-gray-600 transition-colors"
              title="Accueil"
            >
              <Home className="h-4 w-4" />
            </Link>
          </li>
        )}
        
        {/* Breadcrumb items */}
        {displayItems.map((item, index) => (
          <React.Fragment key={index}>
            {/* Separator */}
            {(index > 0 || showHome) && (
              <li className="flex items-center">
                {separator}
              </li>
            )}
            
            {/* Breadcrumb item */}
            <li className="flex items-center">
              {item.href && !item.current ? (
                <Link
                  to={item.href}
                  className="flex items-center text-sm font-medium text-gray-500 hover:text-gray-700 transition-colors"
                >
                  {item.icon && (
                    <span className="mr-2">{item.icon}</span>
                  )}
                  {item.label}
                </Link>
              ) : (
                <span className={`flex items-center text-sm font-medium ${
                  item.current 
                    ? 'text-gray-900 cursor-default' 
                    : 'text-gray-500'
                }`}>
                  {item.icon && (
                    <span className="mr-2">{item.icon}</span>
                  )}
                  {item.label}
                </span>
              )}
            </li>
          </React.Fragment>
        ))}
      </ol>
    </nav>
  );
};

// Hook pour générer automatiquement les breadcrumbs basés sur l'URL
export const useBreadcrumbs = (
  pathname: string,
  customLabels?: Record<string, string>
) => {
  return React.useMemo(() => {
    const segments = pathname.split('/').filter(Boolean);
    
    const breadcrumbs: BreadcrumbItem[] = segments.map((segment, index) => {
      const href = '/' + segments.slice(0, index + 1).join('/');
      const isLast = index === segments.length - 1;
      
      // Utiliser les labels personnalisés ou formater le segment
      const label = customLabels?.[segment] || 
        segment.charAt(0).toUpperCase() + segment.slice(1).replace(/-/g, ' ');
      
      return {
        label,
        href: isLast ? undefined : href,
        current: isLast
      };
    });
    
    return breadcrumbs;
  }, [pathname, customLabels]);
};

// Composant BreadcrumbWithActions pour inclure des actions
export const BreadcrumbWithActions: React.FC<BreadcrumbProps & {
  actions?: React.ReactNode;
}> = ({ actions, ...breadcrumbProps }) => (
  <div className="flex items-center justify-between mb-6">
    <Breadcrumb {...breadcrumbProps} />
    {actions && (
      <div className="flex items-center space-x-2">
        {actions}
      </div>
    )}
  </div>
);

// Breadcrumb pour pages d'administration
export const AdminBreadcrumb: React.FC<{
  currentPage: string;
  parentPages?: Array<{ label: string; href: string }>;
  actions?: React.ReactNode;
}> = ({ currentPage, parentPages = [], actions }) => {
  const items: BreadcrumbItem[] = [
    { label: 'Administration', href: '/admin' },
    ...parentPages.map(page => ({ label: page.label, href: page.href })),
    { label: currentPage, current: true }
  ];

  return (
    <BreadcrumbWithActions
      items={items}
      actions={actions}
      className="mb-6"
    />
  );
};

// Breadcrumb pour pages enseignant
export const TeacherBreadcrumb: React.FC<{
  currentPage: string;
  parentPages?: Array<{ label: string; href: string }>;
  actions?: React.ReactNode;
}> = ({ currentPage, parentPages = [], actions }) => {
  const items: BreadcrumbItem[] = [
    { label: 'Espace Enseignant', href: '/teacher' },
    ...parentPages.map(page => ({ label: page.label, href: page.href })),
    { label: currentPage, current: true }
  ];

  return (
    <BreadcrumbWithActions
      items={items}
      actions={actions}
      className="mb-6"
    />
  );
};

// Breadcrumb pour pages étudiant
export const StudentBreadcrumb: React.FC<{
  currentPage: string;
  parentPages?: Array<{ label: string; href: string }>;
  actions?: React.ReactNode;
}> = ({ currentPage, parentPages = [], actions }) => {
  const items: BreadcrumbItem[] = [
    { label: 'Espace Étudiant', href: '/student' },
    ...parentPages.map(page => ({ label: page.label, href: page.href })),
    { label: currentPage, current: true }
  ];

  return (
    <BreadcrumbWithActions
      items={items}
      actions={actions}
      className="mb-6"
    />
  );
};

// Breadcrumb dynamique avec détection automatique
export const AutoBreadcrumb: React.FC<{
  customLabels?: Record<string, string>;
  actions?: React.ReactNode;
  className?: string;
}> = ({ customLabels, actions, className }) => {
  const pathname = window.location.pathname;
  const breadcrumbs = useBreadcrumbs(pathname, customLabels);

  return (
    <BreadcrumbWithActions
      items={breadcrumbs}
      actions={actions}
      className={className}
    />
  );
};