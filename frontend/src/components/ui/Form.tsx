// Form.tsx - Composant formulaire avec validation intégrée
import React, { useState, useEffect } from 'react';
import { AlertCircle, Check, Eye, EyeOff, Search } from 'lucide-react';
import { Button } from './Button';

export interface FormFieldProps {
  name: string;
  label?: string;
  type?: 'text' | 'email' | 'password' | 'number' | 'tel' | 'url' | 'search' | 'date' | 'time' | 'datetime-local';
  placeholder?: string;
  value?: string | number;
  defaultValue?: string | number;
  required?: boolean;
  disabled?: boolean;
  readOnly?: boolean;
  autoComplete?: string;
  autoFocus?: boolean;
  pattern?: string;
  min?: number;
  max?: number;
  step?: number;
  maxLength?: number;
  minLength?: number;
  validation?: {
    required?: boolean | string;
    minLength?: number | { value: number; message: string };
    maxLength?: number | { value: number; message: string };
    pattern?: { value: RegExp; message: string };
    custom?: (value: any) => string | boolean;
  };
  onChange?: (value: string | number) => void;
  onBlur?: () => void;
  onFocus?: () => void;
  className?: string;
  error?: string;
  success?: boolean;
  helpText?: string;
  prefix?: React.ReactNode;
  suffix?: React.ReactNode;
  size?: 'sm' | 'md' | 'lg';
}

export interface SelectFieldProps extends Omit<FormFieldProps, 'type'> {
  options: Array<{ value: string | number; label: string; disabled?: boolean }>;
  multiple?: boolean;
  searchable?: boolean;
}

export interface TextAreaFieldProps extends Omit<FormFieldProps, 'type'> {
  rows?: number;
  resize?: 'none' | 'vertical' | 'horizontal' | 'both';
}

export interface FormProps {
  children: React.ReactNode;
  onSubmit?: (data: Record<string, any>) => void | Promise<void>;
  className?: string;
  loading?: boolean;
  disabled?: boolean;
}

// Hook pour gérer l'état du formulaire
export const useForm = (initialValues: Record<string, any> = {}) => {
  const [values, setValues] = useState(initialValues);
  const [errors, setErrors] = useState<Record<string, string>>({});
  const [touched, setTouched] = useState<Record<string, boolean>>({});

  const setValue = (name: string, value: any) => {
    setValues(prev => ({ ...prev, [name]: value }));
    // Nettoyer l'erreur si elle existe
    if (errors[name]) {
      setErrors(prev => {
        const newErrors = { ...prev };
        delete newErrors[name];
        return newErrors;
      });
    }
  };

  const setError = (name: string, error: string) => {
    setErrors(prev => ({ ...prev, [name]: error }));
  };

  const setTouched = (name: string, isTouched = true) => {
    setTouched(prev => ({ ...prev, [name]: isTouched }));
  };

  const validateField = (name: string, value: any, validation?: FormFieldProps['validation']) => {
    if (!validation) return '';

    // Required validation
    if (validation.required) {
      if (value === undefined || value === null || value === '') {
        return typeof validation.required === 'string' 
          ? validation.required 
          : 'Ce champ est requis';
      }
    }

    // Length validations
    if (validation.minLength && typeof value === 'string') {
      const minLength = typeof validation.minLength === 'number' 
        ? validation.minLength 
        : validation.minLength.value;
      const message = typeof validation.minLength === 'object' 
        ? validation.minLength.message 
        : `Minimum ${minLength} caractères`;
      
      if (value.length < minLength) {
        return message;
      }
    }

    if (validation.maxLength && typeof value === 'string') {
      const maxLength = typeof validation.maxLength === 'number' 
        ? validation.maxLength 
        : validation.maxLength.value;
      const message = typeof validation.maxLength === 'object' 
        ? validation.maxLength.message 
        : `Maximum ${maxLength} caractères`;
      
      if (value.length > maxLength) {
        return message;
      }
    }

    // Pattern validation
    if (validation.pattern && typeof value === 'string') {
      if (!validation.pattern.value.test(value)) {
        return validation.pattern.message;
      }
    }

    // Custom validation
    if (validation.custom) {
      const result = validation.custom(value);
      if (typeof result === 'string') {
        return result;
      }
      if (result === false) {
        return 'Valeur invalide';
      }
    }

    return '';
  };

  const validateForm = (fields: Record<string, FormFieldProps['validation']>) => {
    const newErrors: Record<string, string> = {};
    
    Object.entries(fields).forEach(([name, validation]) => {
      const error = validateField(name, values[name], validation);
      if (error) {
        newErrors[name] = error;
      }
    });

    setErrors(newErrors);
    return Object.keys(newErrors).length === 0;
  };

  const reset = (newValues = initialValues) => {
    setValues(newValues);
    setErrors({});
    setTouched({});
  };

  return {
    values,
    errors,
    touched,
    setValue,
    setError,
    setTouched,
    validateField,
    validateForm,
    reset,
    isValid: Object.keys(errors).length === 0,
    isDirty: JSON.stringify(values) !== JSON.stringify(initialValues)
  };
};

// Composant Form principal
export const Form: React.FC<FormProps> = ({
  children,
  onSubmit,
  className = '',
  loading = false,
  disabled = false
}) => {
  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    if (onSubmit && !loading && !disabled) {
      const formData = new FormData(e.target as HTMLFormElement);
      const data = Object.fromEntries(formData.entries());
      onSubmit(data);
    }
  };

  return (
    <form onSubmit={handleSubmit} className={className}>
      <fieldset disabled={disabled || loading}>
        {children}
      </fieldset>
    </form>
  );
};

// Composant Input
export const Input: React.FC<FormFieldProps> = ({
  name,
  label,
  type = 'text',
  placeholder,
  value,
  defaultValue,
  required = false,
  disabled = false,
  readOnly = false,
  autoComplete,
  autoFocus = false,
  pattern,
  min,
  max,
  step,
  maxLength,
  minLength,
  onChange,
  onBlur,
  onFocus,
  className = '',
  error,
  success = false,
  helpText,
  prefix,
  suffix,
  size = 'md'
}) => {
  const [showPassword, setShowPassword] = useState(false);
  const [internalValue, setInternalValue] = useState(value || defaultValue || '');

  const sizeClasses = {
    sm: 'px-3 py-2 text-sm',
    md: 'px-4 py-2.5 text-sm',
    lg: 'px-4 py-3 text-base'
  };

  const handleChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const newValue = type === 'number' ? Number(e.target.value) : e.target.value;
    setInternalValue(newValue);
    onChange?.(newValue);
  };

  const inputType = type === 'password' && showPassword ? 'text' : type;

  return (
    <div className={className}>
      {label && (
        <label htmlFor={name} className="block text-sm font-medium text-gray-700 mb-1">
          {label}
          {required && <span className="text-red-500 ml-1">*</span>}
        </label>
      )}
      
      <div className="relative">
        {prefix && (
          <div className="absolute inset-y-0 left-0 pl-3 flex items-center pointer-events-none">
            {prefix}
          </div>
        )}
        
        <input
          id={name}
          name={name}
          type={inputType}
          placeholder={placeholder}
          value={internalValue}
          required={required}
          disabled={disabled}
          readOnly={readOnly}
          autoComplete={autoComplete}
          autoFocus={autoFocus}
          pattern={pattern}
          min={min}
          max={max}
          step={step}
          maxLength={maxLength}
          minLength={minLength}
          onChange={handleChange}
          onBlur={onBlur}
          onFocus={onFocus}
          className={`
            block w-full border border-gray-300 rounded-lg shadow-sm
            focus:outline-none focus:ring-2 focus:ring-primary-500 focus:border-primary-500
            disabled:bg-gray-50 disabled:text-gray-500 disabled:cursor-not-allowed
            ${sizeClasses[size]}
            ${prefix ? 'pl-10' : ''}
            ${suffix || type === 'password' ? 'pr-10' : ''}
            ${error ? 'border-red-300 bg-red-50 focus:ring-red-500 focus:border-red-500' : ''}
            ${success ? 'border-green-300 bg-green-50 focus:ring-green-500 focus:border-green-500' : ''}
          `}
        />
        
        {(suffix || type === 'password') && (
          <div className="absolute inset-y-0 right-0 pr-3 flex items-center">
            {type === 'password' ? (
              <button
                type="button"
                onClick={() => setShowPassword(!showPassword)}
                className="text-gray-400 hover:text-gray-600"
              >
                {showPassword ? <EyeOff className="h-4 w-4" /> : <Eye className="h-4 w-4" />}
              </button>
            ) : (
              suffix
            )}
          </div>
        )}
        
        {error && (
          <div className="absolute inset-y-0 right-0 pr-3 flex items-center pointer-events-none">
            <AlertCircle className="h-4 w-4 text-red-500" />
          </div>
        )}
        
        {success && (
          <div className="absolute inset-y-0 right-0 pr-3 flex items-center pointer-events-none">
            <Check className="h-4 w-4 text-green-500" />
          </div>
        )}
      </div>
      
      {(error || helpText) && (
        <div className="mt-1 text-sm">
          {error && (
            <p className="text-red-600 flex items-center">
              <AlertCircle className="h-3 w-3 mr-1" />
              {error}
            </p>
          )}
          {!error && helpText && (
            <p className="text-gray-500">{helpText}</p>
          )}
        </div>
      )}
    </div>
  );
};

// Composant Select
export const Select: React.FC<SelectFieldProps> = ({
  name,
  label,
  options,
  value,
  defaultValue,
  multiple = false,
  searchable = false,
  required = false,
  disabled = false,
  onChange,
  onBlur,
  onFocus,
  className = '',
  error,
  success = false,
  helpText,
  size = 'md'
}) => {
  const [isOpen, setIsOpen] = useState(false);
  const [searchTerm, setSearchTerm] = useState('');
  const [internalValue, setInternalValue] = useState(value || defaultValue || (multiple ? [] : ''));

  const sizeClasses = {
    sm: 'px-3 py-2 text-sm',
    md: 'px-4 py-2.5 text-sm',
    lg: 'px-4 py-3 text-base'
  };

  const filteredOptions = searchable
    ? options.filter(option =>
        option.label.toLowerCase().includes(searchTerm.toLowerCase())
      )
    : options;

  const handleSelect = (optionValue: string | number) => {
    let newValue;
    
    if (multiple) {
      const currentArray = Array.isArray(internalValue) ? internalValue : [];
      newValue = currentArray.includes(optionValue)
        ? currentArray.filter(v => v !== optionValue)
        : [...currentArray, optionValue];
    } else {
      newValue = optionValue;
      setIsOpen(false);
    }
    
    setInternalValue(newValue);
    onChange?.(newValue);
  };

  const getDisplayValue = () => {
    if (multiple && Array.isArray(internalValue)) {
      if (internalValue.length === 0) return '';
      if (internalValue.length === 1) {
        const option = options.find(opt => opt.value === internalValue[0]);
        return option?.label || '';
      }
      return `${internalValue.length} éléments sélectionnés`;
    }
    
    const option = options.find(opt => opt.value === internalValue);
    return option?.label || '';
  };

  return (
    <div className={className}>
      {label && (
        <label htmlFor={name} className="block text-sm font-medium text-gray-700 mb-1">
          {label}
          {required && <span className="text-red-500 ml-1">*</span>}
        </label>
      )}
      
      <div className="relative">
        <button
          type="button"
          onClick={() => setIsOpen(!isOpen)}
          disabled={disabled}
          className={`
            block w-full text-left border border-gray-300 rounded-lg shadow-sm
            focus:outline-none focus:ring-2 focus:ring-primary-500 focus:border-primary-500
            disabled:bg-gray-50 disabled:text-gray-500 disabled:cursor-not-allowed
            ${sizeClasses[size]}
            ${error ? 'border-red-300 bg-red-50 focus:ring-red-500 focus:border-red-500' : ''}
            ${success ? 'border-green-300 bg-green-50 focus:ring-green-500 focus:border-green-500' : ''}
          `}
        >
          <span className={getDisplayValue() ? '' : 'text-gray-400'}>
            {getDisplayValue() || 'Sélectionner...'}
          </span>
        </button>
        
        {isOpen && (
          <div className="absolute z-10 mt-1 w-full bg-white shadow-lg max-h-60 rounded-md border border-gray-300 overflow-auto">
            {searchable && (
              <div className="p-2 border-b border-gray-200">
                <div className="relative">
                  <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 h-4 w-4 text-gray-400" />
                  <input
                    type="text"
                    placeholder="Rechercher..."
                    value={searchTerm}
                    onChange={(e) => setSearchTerm(e.target.value)}
                    className="w-full pl-10 pr-3 py-2 border border-gray-300 rounded text-sm focus:outline-none focus:ring-1 focus:ring-primary-500"
                  />
                </div>
              </div>
            )}
            
            {filteredOptions.map((option) => {
              const isSelected = multiple
                ? Array.isArray(internalValue) && internalValue.includes(option.value)
                : internalValue === option.value;
              
              return (
                <button
                  key={option.value}
                  type="button"
                  onClick={() => handleSelect(option.value)}
                  disabled={option.disabled}
                  className={`
                    w-full text-left px-4 py-2 hover:bg-gray-100 disabled:text-gray-400 disabled:cursor-not-allowed
                    ${isSelected ? 'bg-primary-100 text-primary-700' : ''}
                  `}
                >
                  <div className="flex items-center justify-between">
                    <span>{option.label}</span>
                    {multiple && isSelected && (
                      <Check className="h-4 w-4 text-primary-600" />
                    )}
                  </div>
                </button>
              );
            })}
            
            {filteredOptions.length === 0 && (
              <div className="px-4 py-2 text-gray-500 text-center">
                Aucun résultat trouvé
              </div>
            )}
          </div>
        )}
      </div>
      
      {(error || helpText) && (
        <div className="mt-1 text-sm">
          {error && (
            <p className="text-red-600 flex items-center">
              <AlertCircle className="h-3 w-3 mr-1" />
              {error}
            </p>
          )}
          {!error && helpText && (
            <p className="text-gray-500">{helpText}</p>
          )}
        </div>
      )}
      
      {/* Click outside to close */}
      {isOpen && (
        <div
          className="fixed inset-0 z-0"
          onClick={() => setIsOpen(false)}
        />
      )}
    </div>
  );
};

// Composant TextArea
export const TextArea: React.FC<TextAreaFieldProps> = ({
  name,
  label,
  placeholder,
  value,
  defaultValue,
  rows = 3,
  resize = 'vertical',
  required = false,
  disabled = false,
  readOnly = false,
  maxLength,
  minLength,
  onChange,
  onBlur,
  onFocus,
  className = '',
  error,
  success = false,
  helpText,
  size = 'md'
}) => {
  const [internalValue, setInternalValue] = useState(value || defaultValue || '');

  const sizeClasses = {
    sm: 'px-3 py-2 text-sm',
    md: 'px-4 py-2.5 text-sm',
    lg: 'px-4 py-3 text-base'
  };

  const resizeClasses = {
    none: 'resize-none',
    vertical: 'resize-y',
    horizontal: 'resize-x',
    both: 'resize'
  };

  const handleChange = (e: React.ChangeEvent<HTMLTextAreaElement>) => {
    const newValue = e.target.value;
    setInternalValue(newValue);
    onChange?.(newValue);
  };

  return (
    <div className={className}>
      {label && (
        <label htmlFor={name} className="block text-sm font-medium text-gray-700 mb-1">
          {label}
          {required && <span className="text-red-500 ml-1">*</span>}
        </label>
      )}
      
      <textarea
        id={name}
        name={name}
        rows={rows}
        placeholder={placeholder}
        value={internalValue}
        required={required}
        disabled={disabled}
        readOnly={readOnly}
        maxLength={maxLength}
        minLength={minLength}
        onChange={handleChange}
        onBlur={onBlur}
        onFocus={onFocus}
        className={`
          block w-full border border-gray-300 rounded-lg shadow-sm
          focus:outline-none focus:ring-2 focus:ring-primary-500 focus:border-primary-500
          disabled:bg-gray-50 disabled:text-gray-500 disabled:cursor-not-allowed
          ${sizeClasses[size]}
          ${resizeClasses[resize]}
          ${error ? 'border-red-300 bg-red-50 focus:ring-red-500 focus:border-red-500' : ''}
          ${success ? 'border-green-300 bg-green-50 focus:ring-green-500 focus:border-green-500' : ''}
        `}
      />
      
      {(error || helpText || maxLength) && (
        <div className="mt-1 flex justify-between text-sm">
          <div>
            {error && (
              <p className="text-red-600 flex items-center">
                <AlertCircle className="h-3 w-3 mr-1" />
                {error}
              </p>
            )}
            {!error && helpText && (
              <p className="text-gray-500">{helpText}</p>
            )}
          </div>
          {maxLength && (
            <p className="text-gray-400">
              {String(internalValue).length}/{maxLength}
            </p>
          )}
        </div>
      )}
    </div>
  );
};