// Loading.tsx - Composants de chargement et skeleton
import React from 'react';
import { Loader2, RefreshCw } from 'lucide-react';

export interface LoadingSpinnerProps {
  size?: 'xs' | 'sm' | 'md' | 'lg' | 'xl';
  color?: string;
  className?: string;
}

export interface SkeletonProps {
  width?: string | number;
  height?: string | number;
  className?: string;
  animate?: boolean;
  variant?: 'text' | 'circular' | 'rectangular';
}

export interface LoadingOverlayProps {
  loading: boolean;
  children: React.ReactNode;
  message?: string;
  className?: string;
}

// Composant Spinner de base
export const LoadingSpinner: React.FC<LoadingSpinnerProps> = ({
  size = 'md',
  color = 'text-primary-600',
  className = ''
}) => {
  const sizeClasses = {
    xs: 'h-3 w-3',
    sm: 'h-4 w-4',
    md: 'h-6 w-6',
    lg: 'h-8 w-8',
    xl: 'h-12 w-12'
  };

  return (
    <Loader2 className={`animate-spin ${sizeClasses[size]} ${color} ${className}`} />
  );
};

// Composant Skeleton
export const Skeleton: React.FC<SkeletonProps> = ({
  width = '100%',
  height = '1rem',
  className = '',
  animate = true,
  variant = 'rectangular'
}) => {
  const baseClasses = 'bg-gray-200';
  const animateClass = animate ? 'animate-pulse' : '';
  
  const variantClasses = {
    text: 'rounded',
    circular: 'rounded-full',
    rectangular: 'rounded-md'
  };

  const style = {
    width: typeof width === 'number' ? `${width}px` : width,
    height: typeof height === 'number' ? `${height}px` : height
  };

  return (
    <div
      className={`${baseClasses} ${variantClasses[variant]} ${animateClass} ${className}`}
      style={style}
    />
  );
};

// Overlay de chargement
export const LoadingOverlay: React.FC<LoadingOverlayProps> = ({
  loading,
  children,
  message = 'Chargement...',
  className = ''
}) => {
  return (
    <div className={`relative ${className}`}>
      {children}
      {loading && (
        <div className="absolute inset-0 bg-white bg-opacity-75 flex items-center justify-center z-10">
          <div className="text-center">
            <LoadingSpinner size="lg" />
            <p className="mt-2 text-sm text-gray-600">{message}</p>
          </div>
        </div>
      )}
    </div>
  );
};

// Skeleton pour Card
export const CardSkeleton: React.FC<{
  hasHeader?: boolean;
  lines?: number;
  hasFooter?: boolean;
  className?: string;
}> = ({
  hasHeader = true,
  lines = 3,
  hasFooter = false,
  className = ''
}) => (
  <div className={`bg-white rounded-xl shadow-sm border border-gray-200 p-6 ${className}`}>
    {hasHeader && (
      <div className="mb-4">
        <Skeleton height="1.5rem" width="60%" className="mb-2" />
        <Skeleton height="1rem" width="40%" />
      </div>
    )}
    
    <div className="space-y-3">
      {Array.from({ length: lines }).map((_, index) => (
        <Skeleton 
          key={index}
          height="1rem" 
          width={index === lines - 1 ? '70%' : '100%'} 
        />
      ))}
    </div>
    
    {hasFooter && (
      <div className="mt-4 pt-4 border-t border-gray-200">
        <div className="flex space-x-2">
          <Skeleton height="2rem" width="5rem" />
          <Skeleton height="2rem" width="5rem" />
        </div>
      </div>
    )}
  </div>
);

// Skeleton pour Table
export const TableSkeleton: React.FC<{
  rows?: number;
  columns?: number;
  hasHeader?: boolean;
  className?: string;
}> = ({
  rows = 5,
  columns = 4,
  hasHeader = true,
  className = ''
}) => (
  <div className={`overflow-hidden shadow ring-1 ring-black ring-opacity-5 rounded-lg ${className}`}>
    {hasHeader && (
      <div className="bg-gray-50 px-6 py-3 border-b border-gray-200">
        <div className="grid gap-4" style={{ gridTemplateColumns: `repeat(${columns}, 1fr)` }}>
          {Array.from({ length: columns }).map((_, index) => (
            <Skeleton key={index} height="1rem" width="80%" />
          ))}
        </div>
      </div>
    )}
    
    <div className="bg-white">
      {Array.from({ length: rows }).map((_, rowIndex) => (
        <div key={rowIndex} className="px-6 py-4 border-b border-gray-200 last:border-b-0">
          <div className="grid gap-4" style={{ gridTemplateColumns: `repeat(${columns}, 1fr)` }}>
            {Array.from({ length: columns }).map((_, colIndex) => (
              <Skeleton key={colIndex} height="1rem" />
            ))}
          </div>
        </div>
      ))}
    </div>
  </div>
);

// Skeleton pour Dashboard Stats
export const StatCardSkeleton: React.FC<{ className?: string }> = ({ className = '' }) => (
  <div className={`bg-white rounded-xl shadow-sm border border-gray-200 p-6 ${className}`}>
    <div className="flex items-center">
      <Skeleton variant="circular" width="48px" height="48px" />
      <div className="ml-4 flex-1">
        <Skeleton height="1rem" width="60%" className="mb-2" />
        <Skeleton height="1.5rem" width="40%" />
      </div>
    </div>
  </div>
);

// Skeleton pour Liste
export const ListSkeleton: React.FC<{
  items?: number;
  hasAvatar?: boolean;
  hasAction?: boolean;
  className?: string;
}> = ({
  items = 5,
  hasAvatar = false,
  hasAction = false,
  className = ''
}) => (
  <div className={`space-y-4 ${className}`}>
    {Array.from({ length: items }).map((_, index) => (
      <div key={index} className="flex items-start space-x-3 p-3">
        {hasAvatar && (
          <Skeleton variant="circular" width="40px" height="40px" />
        )}
        <div className="flex-1 space-y-2">
          <Skeleton height="1rem" width="80%" />
          <Skeleton height="0.875rem" width="60%" />
        </div>
        {hasAction && (
          <Skeleton width="2rem" height="2rem" />
        )}
      </div>
    ))}
  </div>
);

// Skeleton pour Formulaire
export const FormSkeleton: React.FC<{
  fields?: number;
  hasSubmit?: boolean;
  className?: string;
}> = ({
  fields = 4,
  hasSubmit = true,
  className = ''
}) => (
  <div className={`space-y-6 ${className}`}>
    {Array.from({ length: fields }).map((_, index) => (
      <div key={index} className="space-y-2">
        <Skeleton height="1rem" width="25%" />
        <Skeleton height="2.5rem" width="100%" />
      </div>
    ))}
    
    {hasSubmit && (
      <div className="flex space-x-2 pt-4">
        <Skeleton height="2.5rem" width="6rem" />
        <Skeleton height="2.5rem" width="6rem" />
      </div>
    )}
  </div>
);

// Skeleton pour Page entière
export const PageSkeleton: React.FC<{
  hasHeader?: boolean;
  hasStats?: boolean;
  hasTable?: boolean;
  hasCards?: boolean;
  className?: string;
}> = ({
  hasHeader = true,
  hasStats = true,
  hasTable = false,
  hasCards = false,
  className = ''
}) => (
  <div className={`min-h-screen bg-gray-50 ${className}`}>
    <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
      
      {/* Header */}
      {hasHeader && (
        <div className="mb-8">
          <Skeleton height="2rem" width="40%" className="mb-2" />
          <Skeleton height="1rem" width="60%" />
        </div>
      )}
      
      {/* Stats */}
      {hasStats && (
        <div className="mb-8 grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
          {Array.from({ length: 4 }).map((_, index) => (
            <StatCardSkeleton key={index} />
          ))}
        </div>
      )}
      
      {/* Cards */}
      {hasCards && (
        <div className="mb-8 grid grid-cols-1 lg:grid-cols-2 xl:grid-cols-3 gap-6">
          {Array.from({ length: 6 }).map((_, index) => (
            <CardSkeleton key={index} />
          ))}
        </div>
      )}
      
      {/* Table */}
      {hasTable && (
        <TableSkeleton />
      )}
      
    </div>
  </div>
);

// Spinner pour boutons
export const ButtonSpinner: React.FC<{ className?: string }> = ({ className = '' }) => (
  <RefreshCw className={`animate-spin h-4 w-4 ${className}`} />
);

// Hook pour gérer les états de chargement
export const useLoading = (initialState = false) => {
  const [loading, setLoading] = React.useState(initialState);

  const startLoading = React.useCallback(() => setLoading(true), []);
  const stopLoading = React.useCallback(() => setLoading(false), []);
  const toggleLoading = React.useCallback(() => setLoading(prev => !prev), []);

  const withLoading = React.useCallback(async (fn: () => Promise<any>) => {
    startLoading();
    try {
      return await fn();
    } finally {
      stopLoading();
    }
  }, [startLoading, stopLoading]);

  return {
    loading,
    startLoading,
    stopLoading,
    toggleLoading,
    withLoading
  };
};

// Composant de chargement avec délai (évite les flashs)
export const DelayedLoading: React.FC<{
  loading: boolean;
  delay?: number;
  children: React.ReactNode;
  fallback?: React.ReactNode;
}> = ({
  loading,
  delay = 300,
  children,
  fallback = <LoadingSpinner />
}) => {
  const [showLoading, setShowLoading] = React.useState(false);

  React.useEffect(() => {
    let timer: NodeJS.Timeout;
    
    if (loading) {
      timer = setTimeout(() => {
        setShowLoading(true);
      }, delay);
    } else {
      setShowLoading(false);
    }

    return () => {
      if (timer) clearTimeout(timer);
    };
  }, [loading, delay]);

  if (loading && showLoading) {
    return <>{fallback}</>;
  }

  return <>{children}</>;
};