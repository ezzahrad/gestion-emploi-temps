// Card.tsx - Composant carte réutilisable optimisé pour desktop
import React from 'react';
import { LucideIcon } from 'lucide-react';

interface CardProps {
  children: React.ReactNode;
  className?: string;
  hover?: boolean;
  padding?: 'sm' | 'md' | 'lg' | 'xl';
  border?: boolean;
  shadow?: 'none' | 'sm' | 'md' | 'lg';
}

interface StatCardProps {
  title: string;
  value: string | number;
  icon: React.ReactNode;
  color: string;
  trend?: {
    value: number;
    direction: 'up' | 'down' | 'stable';
  };
  subtitle?: string;
  onClick?: () => void;
}

interface ActionCardProps {
  title: string;
  description: string;
  icon: React.ReactNode;
  color: string;
  onClick?: () => void;
  href?: string;
  badge?: string;
  priority?: 'high' | 'medium' | 'low';
  disabled?: boolean;
}

// Composant de base Card
export const Card: React.FC<CardProps> = ({
  children,
  className = '',
  hover = false,
  padding = 'md',
  border = true,
  shadow = 'sm'
}) => {
  const paddingClasses = {
    sm: 'p-4',
    md: 'p-6',
    lg: 'p-8',
    xl: 'p-10'
  };

  const shadowClasses = {
    none: '',
    sm: 'shadow-sm',
    md: 'shadow-md',
    lg: 'shadow-lg'
  };

  return (
    <div
      className={`
        bg-white rounded-xl
        ${border ? 'border border-gray-200' : ''}
        ${shadowClasses[shadow]}
        ${hover ? 'hover:shadow-md transition-shadow duration-200' : ''}
        ${paddingClasses[padding]}
        ${className}
      `}
    >
      {children}
    </div>
  );
};

// Composant StatCard pour les statistiques
export const StatCard: React.FC<StatCardProps> = ({
  title,
  value,
  icon,
  color,
  trend,
  subtitle,
  onClick
}) => {
  const getTrendIcon = () => {
    if (!trend) return null;
    
    switch (trend.direction) {
      case 'up':
        return <span className="text-green-600">↗</span>;
      case 'down':
        return <span className="text-red-600">↘</span>;
      default:
        return <span className="text-gray-600">→</span>;
    }
  };

  const getTrendColor = () => {
    if (!trend) return '';
    
    switch (trend.direction) {
      case 'up':
        return 'text-green-600 bg-green-100';
      case 'down':
        return 'text-red-600 bg-red-100';
      default:
        return 'text-gray-600 bg-gray-100';
    }
  };

  return (
    <Card 
      hover 
      className={onClick ? 'cursor-pointer' : ''}
      onClick={onClick}
    >
      <div className="flex items-center justify-between">
        <div className="flex items-center">
          <div className={`flex-shrink-0 bg-gradient-to-br ${color} p-3 rounded-lg shadow-sm`}>
            <div className="text-white">
              {icon}
            </div>
          </div>
          <div className="ml-4">
            <p className="text-sm font-medium text-gray-500">{title}</p>
            <p className="text-2xl font-bold text-gray-900">{value}</p>
            {subtitle && (
              <p className="text-xs text-gray-500 mt-1">{subtitle}</p>
            )}
          </div>
        </div>
        
        {trend && trend.value !== 0 && (
          <div className={`flex items-center px-2 py-1 rounded-full text-xs font-medium ${getTrendColor()}`}>
            {getTrendIcon()}
            <span className="ml-1">{Math.abs(trend.value)}%</span>
          </div>
        )}
      </div>
    </Card>
  );
};

// Composant ActionCard pour les actions rapides
export const ActionCard: React.FC<ActionCardProps> = ({
  title,
  description,
  icon,
  color,
  onClick,
  href,
  badge,
  priority = 'medium',
  disabled = false
}) => {
  const getPriorityIndicator = () => {
    const colors = {
      high: 'bg-red-400',
      medium: 'bg-yellow-400',
      low: 'bg-green-400'
    };
    
    return (
      <div className={`w-2 h-2 rounded-full ${colors[priority]}`} />
    );
  };

  const CardContent = () => (
    <div className={`
      relative bg-gradient-to-r ${color} text-white p-6 rounded-xl shadow-sm 
      hover:shadow-lg transition-all duration-300 transform hover:-translate-y-1 
      group ${disabled ? 'opacity-50 cursor-not-allowed' : 'cursor-pointer'}
    `}>
      {badge && (
        <span className="absolute -top-2 -right-2 bg-yellow-400 text-yellow-900 text-xs font-bold px-2 py-1 rounded-full">
          {badge}
        </span>
      )}
      
      <div className="flex items-start justify-between">
        <div className="flex-1">
          <div className="flex items-center mb-2">
            {icon}
            <div className="ml-2">
              {getPriorityIndicator()}
            </div>
          </div>
          <h3 className="font-semibold text-lg leading-tight">{title}</h3>
          <p className="text-sm opacity-90 mt-1">{description}</p>
        </div>
      </div>
      
      <div className="mt-4 opacity-0 group-hover:opacity-100 transition-opacity">
        <div className="text-xs font-medium">
          {disabled ? 'Non disponible' : 'Cliquer pour accéder →'}
        </div>
      </div>
    </div>
  );

  if (href && !disabled) {
    return (
      <a href={href} className="block">
        <CardContent />
      </a>
    );
  }

  return (
    <div onClick={disabled ? undefined : onClick}>
      <CardContent />
    </div>
  );
};

// Composant CardHeader
export const CardHeader: React.FC<{
  title: string;
  subtitle?: string;
  action?: React.ReactNode;
  className?: string;
}> = ({ title, subtitle, action, className = '' }) => (
  <div className={`border-b border-gray-200 pb-4 mb-4 ${className}`}>
    <div className="flex items-center justify-between">
      <div>
        <h3 className="text-lg font-semibold text-gray-900">{title}</h3>
        {subtitle && (
          <p className="text-sm text-gray-600 mt-1">{subtitle}</p>
        )}
      </div>
      {action && <div>{action}</div>}
    </div>
  </div>
);

// Composant CardGrid pour organiser les cartes
export const CardGrid: React.FC<{
  children: React.ReactNode;
  cols?: 1 | 2 | 3 | 4 | 5 | 6;
  gap?: 'sm' | 'md' | 'lg';
  className?: string;
}> = ({ children, cols = 3, gap = 'md', className = '' }) => {
  const colsClasses = {
    1: 'grid-cols-1',
    2: 'grid-cols-1 md:grid-cols-2',
    3: 'grid-cols-1 md:grid-cols-2 lg:grid-cols-3',
    4: 'grid-cols-1 md:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4',
    5: 'grid-cols-1 md:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4 2xl:grid-cols-5',
    6: 'grid-cols-1 md:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4 2xl:grid-cols-6'
  };

  const gapClasses = {
    sm: 'gap-4',
    md: 'gap-6',
    lg: 'gap-8'
  };

  return (
    <div className={`grid ${colsClasses[cols]} ${gapClasses[gap]} ${className}`}>
      {children}
    </div>
  );
};