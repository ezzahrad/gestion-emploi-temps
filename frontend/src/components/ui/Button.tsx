// Button.tsx - Composant bouton réutilisable optimisé pour desktop
import React from 'react';
import { LucideIcon } from 'lucide-react';

export interface ButtonProps {
  children: React.ReactNode;
  variant?: 'primary' | 'secondary' | 'success' | 'warning' | 'error' | 'ghost' | 'outline';
  size?: 'xs' | 'sm' | 'md' | 'lg' | 'xl';
  disabled?: boolean;
  loading?: boolean;
  fullWidth?: boolean;
  icon?: React.ReactNode;
  iconPosition?: 'left' | 'right';
  onClick?: () => void;
  type?: 'button' | 'submit' | 'reset';
  className?: string;
  tooltip?: string;
}

export const Button: React.FC<ButtonProps> = ({
  children,
  variant = 'primary',
  size = 'md',
  disabled = false,
  loading = false,
  fullWidth = false,
  icon,
  iconPosition = 'left',
  onClick,
  type = 'button',
  className = '',
  tooltip
}) => {
  const baseClasses = 'inline-flex items-center justify-center font-medium rounded-lg transition-all duration-200 focus:outline-none focus:ring-2 focus:ring-offset-2 disabled:opacity-50 disabled:cursor-not-allowed';

  const variantClasses = {
    primary: 'bg-primary-600 text-white hover:bg-primary-700 focus:ring-primary-500 shadow-sm hover:shadow-md',
    secondary: 'bg-gray-200 text-gray-900 hover:bg-gray-300 focus:ring-gray-500',
    success: 'bg-green-600 text-white hover:bg-green-700 focus:ring-green-500 shadow-sm hover:shadow-md',
    warning: 'bg-yellow-600 text-white hover:bg-yellow-700 focus:ring-yellow-500 shadow-sm hover:shadow-md',
    error: 'bg-red-600 text-white hover:bg-red-700 focus:ring-red-500 shadow-sm hover:shadow-md',
    ghost: 'text-gray-600 hover:text-gray-900 hover:bg-gray-100 focus:ring-gray-500',
    outline: 'border-2 border-current bg-transparent hover:bg-current hover:text-white focus:ring-current'
  };

  const sizeClasses = {
    xs: 'px-2 py-1 text-xs',
    sm: 'px-3 py-1.5 text-sm',
    md: 'px-4 py-2 text-sm',
    lg: 'px-6 py-3 text-base',
    xl: 'px-8 py-4 text-lg'
  };

  const LoadingSpinner = () => (
    <svg className="animate-spin h-4 w-4" fill="none" viewBox="0 0 24 24">
      <circle cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4" className="opacity-25" />
      <path fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z" className="opacity-75" />
    </svg>
  );

  const buttonContent = (
    <>
      {loading && <LoadingSpinner />}
      {!loading && icon && iconPosition === 'left' && <span className="mr-2">{icon}</span>}
      <span>{children}</span>
      {!loading && icon && iconPosition === 'right' && <span className="ml-2">{icon}</span>}
    </>
  );

  return (
    <button
      type={type}
      onClick={onClick}
      disabled={disabled || loading}
      title={tooltip}
      className={`
        ${baseClasses}
        ${variantClasses[variant]}
        ${sizeClasses[size]}
        ${fullWidth ? 'w-full' : ''}
        ${className}
      `}
    >
      {buttonContent}
    </button>
  );
};

// Composant ButtonGroup pour grouper des boutons
export const ButtonGroup: React.FC<{
  children: React.ReactNode;
  className?: string;
  orientation?: 'horizontal' | 'vertical';
}> = ({ children, className = '', orientation = 'horizontal' }) => {
  return (
    <div className={`
      inline-flex ${orientation === 'vertical' ? 'flex-col' : 'flex-row'}
      ${orientation === 'horizontal' ? 'space-x-2' : 'space-y-2'}
      ${className}
    `}>
      {children}
    </div>
  );
};

// Composant IconButton pour les boutons avec icône uniquement
export const IconButton: React.FC<{
  icon: React.ReactNode;
  onClick?: () => void;
  variant?: ButtonProps['variant'];
  size?: ButtonProps['size'];
  disabled?: boolean;
  tooltip?: string;
  className?: string;
}> = ({ icon, onClick, variant = 'ghost', size = 'md', disabled = false, tooltip, className = '' }) => {
  const sizeClasses = {
    xs: 'p-1',
    sm: 'p-1.5',
    md: 'p-2',
    lg: 'p-3',
    xl: 'p-4'
  };

  return (
    <Button
      variant={variant}
      onClick={onClick}
      disabled={disabled}
      tooltip={tooltip}
      className={`${sizeClasses[size]} ${className}`}
    >
      {icon}
    </Button>
  );
};

// Composant FloatingActionButton
export const FloatingActionButton: React.FC<{
  icon: React.ReactNode;
  onClick?: () => void;
  position?: 'bottom-right' | 'bottom-left' | 'top-right' | 'top-left';
  size?: 'md' | 'lg';
  color?: string;
  tooltip?: string;
}> = ({ 
  icon, 
  onClick, 
  position = 'bottom-right', 
  size = 'lg', 
  color = 'bg-primary-600 hover:bg-primary-700',
  tooltip 
}) => {
  const positionClasses = {
    'bottom-right': 'fixed bottom-6 right-6',
    'bottom-left': 'fixed bottom-6 left-6',
    'top-right': 'fixed top-6 right-6',
    'top-left': 'fixed top-6 left-6'
  };

  const sizeClasses = {
    md: 'w-12 h-12',
    lg: 'w-16 h-16'
  };

  return (
    <button
      onClick={onClick}
      title={tooltip}
      className={`
        ${positionClasses[position]}
        ${sizeClasses[size]}
        ${color}
        text-white rounded-full shadow-lg hover:shadow-xl
        transition-all duration-200 transform hover:scale-105
        focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-primary-500
        z-50 flex items-center justify-center
      `}
    >
      {icon}
    </button>
  );
};