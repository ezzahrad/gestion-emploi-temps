// Modal.tsx - Composant modal réutilisable optimisé pour desktop
import React, { useEffect, useRef } from 'react';
import { X } from 'lucide-react';
import { Button } from './Button';

interface ModalProps {
  isOpen: boolean;
  onClose: () => void;
  title?: string;
  children: React.ReactNode;
  size?: 'sm' | 'md' | 'lg' | 'xl' | 'full';
  showCloseButton?: boolean;
  closeOnOverlayClick?: boolean;
  closeOnEscape?: boolean;
  className?: string;
}

interface ModalHeaderProps {
  title: string;
  onClose?: () => void;
  showCloseButton?: boolean;
  className?: string;
}

interface ModalBodyProps {
  children: React.ReactNode;
  className?: string;
  padding?: 'none' | 'sm' | 'md' | 'lg';
}

interface ModalFooterProps {
  children: React.ReactNode;
  className?: string;
  justify?: 'start' | 'center' | 'end' | 'between';
}

export const Modal: React.FC<ModalProps> = ({
  isOpen,
  onClose,
  title,
  children,
  size = 'md',
  showCloseButton = true,
  closeOnOverlayClick = true,
  closeOnEscape = true,
  className = ''
}) => {
  const modalRef = useRef<HTMLDivElement>(null);

  // Gestion de l'échappement
  useEffect(() => {
    if (!isOpen || !closeOnEscape) return;

    const handleEscape = (e: KeyboardEvent) => {
      if (e.key === 'Escape') {
        onClose();
      }
    };

    document.addEventListener('keydown', handleEscape);
    return () => document.removeEventListener('keydown', handleEscape);
  }, [isOpen, closeOnEscape, onClose]);

  // Gestion du focus
  useEffect(() => {
    if (isOpen && modalRef.current) {
      modalRef.current.focus();
    }
  }, [isOpen]);

  // Prévention du scroll du body
  useEffect(() => {
    if (isOpen) {
      document.body.style.overflow = 'hidden';
    } else {
      document.body.style.overflow = 'unset';
    }

    return () => {
      document.body.style.overflow = 'unset';
    };
  }, [isOpen]);

  if (!isOpen) return null;

  const sizeClasses = {
    sm: 'max-w-md',
    md: 'max-w-lg',
    lg: 'max-w-2xl',
    xl: 'max-w-4xl',
    full: 'max-w-full mx-4'
  };

  const handleOverlayClick = (e: React.MouseEvent) => {
    if (closeOnOverlayClick && e.target === e.currentTarget) {
      onClose();
    }
  };

  return (
    <div 
      className="fixed inset-0 bg-gray-600 bg-opacity-75 flex items-center justify-center z-50 p-4"
      onClick={handleOverlayClick}
    >
      <div 
        ref={modalRef}
        tabIndex={-1}
        className={`
          relative w-full ${sizeClasses[size]} shadow-2xl rounded-xl bg-white 
          max-h-full overflow-hidden animate-scale-in
          ${className}
        `}
      >
        {/* Header par défaut si title est fourni */}
        {title && (
          <ModalHeader 
            title={title} 
            onClose={onClose} 
            showCloseButton={showCloseButton} 
          />
        )}
        
        {/* Contenu */}
        <div className="flex-1 overflow-y-auto">
          {children}
        </div>
      </div>
    </div>
  );
};

export const ModalHeader: React.FC<ModalHeaderProps> = ({
  title,
  onClose,
  showCloseButton = true,
  className = ''
}) => (
  <div className={`flex items-center justify-between p-6 border-b border-gray-200 ${className}`}>
    <h2 className="text-xl font-semibold text-gray-900">{title}</h2>
    {showCloseButton && onClose && (
      <button
        onClick={onClose}
        className="text-gray-400 hover:text-gray-600 transition-colors p-1 rounded-lg hover:bg-gray-100"
        aria-label="Fermer"
      >
        <X className="h-6 w-6" />
      </button>
    )}
  </div>
);

export const ModalBody: React.FC<ModalBodyProps> = ({
  children,
  className = '',
  padding = 'md'
}) => {
  const paddingClasses = {
    none: '',
    sm: 'p-4',
    md: 'p-6',
    lg: 'p-8'
  };

  return (
    <div className={`${paddingClasses[padding]} ${className}`}>
      {children}
    </div>
  );
};

export const ModalFooter: React.FC<ModalFooterProps> = ({
  children,
  className = '',
  justify = 'end'
}) => {
  const justifyClasses = {
    start: 'justify-start',
    center: 'justify-center',
    end: 'justify-end',
    between: 'justify-between'
  };

  return (
    <div className={`
      flex items-center ${justifyClasses[justify]} 
      p-6 border-t border-gray-200 bg-gray-50 space-x-2
      ${className}
    `}>
      {children}
    </div>
  );
};

// Modal de confirmation
export const ConfirmModal: React.FC<{
  isOpen: boolean;
  onClose: () => void;
  onConfirm: () => void;
  title: string;
  message: string;
  confirmText?: string;
  cancelText?: string;
  variant?: 'danger' | 'warning' | 'info';
  loading?: boolean;
}> = ({
  isOpen,
  onClose,
  onConfirm,
  title,
  message,
  confirmText = 'Confirmer',
  cancelText = 'Annuler',
  variant = 'info',
  loading = false
}) => {
  const getConfirmVariant = () => {
    switch (variant) {
      case 'danger': return 'error';
      case 'warning': return 'warning';
      default: return 'primary';
    }
  };

  return (
    <Modal isOpen={isOpen} onClose={onClose} size="sm">
      <ModalHeader title={title} onClose={onClose} />
      <ModalBody>
        <p className="text-gray-600">{message}</p>
      </ModalBody>
      <ModalFooter>
        <Button variant="secondary" onClick={onClose} disabled={loading}>
          {cancelText}
        </Button>
        <Button 
          variant={getConfirmVariant()} 
          onClick={onConfirm} 
          loading={loading}
        >
          {confirmText}
        </Button>
      </ModalFooter>
    </Modal>
  );
};

// Modal d'alerte
export const AlertModal: React.FC<{
  isOpen: boolean;
  onClose: () => void;
  title: string;
  message: string;
  variant?: 'success' | 'error' | 'warning' | 'info';
}> = ({
  isOpen,
  onClose,
  title,
  message,
  variant = 'info'
}) => {
  const getIcon = () => {
    switch (variant) {
      case 'success':
        return <div className="w-12 h-12 bg-green-100 rounded-full flex items-center justify-center">
          <svg className="w-6 h-6 text-green-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M5 13l4 4L19 7" />
          </svg>
        </div>;
      case 'error':
        return <div className="w-12 h-12 bg-red-100 rounded-full flex items-center justify-center">
          <svg className="w-6 h-6 text-red-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
          </svg>
        </div>;
      case 'warning':
        return <div className="w-12 h-12 bg-yellow-100 rounded-full flex items-center justify-center">
          <svg className="w-6 h-6 text-yellow-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-2.5L13.732 4c-.77-.833-1.964-.833-2.732 0L3.732 16.5c-.77.833.192 2.5 1.732 2.5z" />
          </svg>
        </div>;
      default:
        return <div className="w-12 h-12 bg-blue-100 rounded-full flex items-center justify-center">
          <svg className="w-6 h-6 text-blue-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M13 16h-1v-4h-1m1-4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
          </svg>
        </div>;
    }
  };

  return (
    <Modal isOpen={isOpen} onClose={onClose} size="sm">
      <ModalBody className="text-center">
        <div className="flex flex-col items-center">
          {getIcon()}
          <h3 className="text-lg font-semibold text-gray-900 mt-4">{title}</h3>
          <p className="text-gray-600 mt-2">{message}</p>
        </div>
      </ModalBody>
      <ModalFooter justify="center">
        <Button onClick={onClose}>
          OK
        </Button>
      </ModalFooter>
    </Modal>
  );
};

// Hook pour gérer l'état des modals
export const useModal = (initialState = false) => {
  const [isOpen, setIsOpen] = React.useState(initialState);

  const openModal = React.useCallback(() => setIsOpen(true), []);
  const closeModal = React.useCallback(() => setIsOpen(false), []);
  const toggleModal = React.useCallback(() => setIsOpen(prev => !prev), []);

  return {
    isOpen,
    openModal,
    closeModal,
    toggleModal
  };
};