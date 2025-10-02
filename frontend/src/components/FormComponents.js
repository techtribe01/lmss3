import React, { forwardRef } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { AlertCircle, CheckCircle, Eye, EyeOff } from 'lucide-react';

// FormField wrapper component
export const FormField = ({ children, error, className = '' }) => (
  <motion.div 
    className={`form-group ${error ? 'error' : ''} ${className}`}
    layout
  >
    {children}
    <AnimatePresence mode="wait">
      {error && (
        <motion.div
          className="form-error"
          initial={{ opacity: 0, y: -10, height: 0 }}
          animate={{ opacity: 1, y: 0, height: 'auto' }}
          exit={{ opacity: 0, y: -10, height: 0 }}
          transition={{ duration: 0.2 }}
        >
          <AlertCircle size={16} />
          <span>{error}</span>
        </motion.div>
      )}
    </AnimatePresence>
  </motion.div>
);

// Enhanced Input component
export const Input = forwardRef(({ 
  label, 
  error, 
  success, 
  hint, 
  icon: Icon, 
  className = '', 
  ...props 
}, ref) => {
  const [isFocused, setIsFocused] = React.useState(false);
  
  return (
    <FormField error={error} className={className}>
      {label && (
        <label className="form-label">
          {label}
          {props.required && <span className="required-asterisk">*</span>}
        </label>
      )}
      <div className={`input-wrapper ${isFocused ? 'focused' : ''} ${error ? 'error' : ''} ${success ? 'success' : ''}`}>
        {Icon && <Icon className="input-icon" size={20} />}
        <input
          ref={ref}
          className="form-input"
          onFocus={() => setIsFocused(true)}
          onBlur={() => setIsFocused(false)}
          {...props}
        />
        {success && <CheckCircle className="input-success-icon" size={20} />}
      </div>
      {hint && !error && (
        <motion.p 
          className="form-hint"
          initial={{ opacity: 0 }}
          animate={{ opacity: 1 }}
        >
          {hint}
        </motion.p>
      )}
    </FormField>
  );
});

// Password Input with show/hide toggle
export const PasswordInput = forwardRef(({ 
  label = 'Password', 
  error, 
  success,
  showStrength = false,
  ...props 
}, ref) => {
  const [showPassword, setShowPassword] = React.useState(false);
  const [strength, setStrength] = React.useState(0);

  // Calculate password strength
  const calculateStrength = (password) => {
    if (!password) return 0;
    
    let score = 0;
    if (password.length >= 8) score += 1;
    if (/[A-Z]/.test(password)) score += 1;
    if (/[a-z]/.test(password)) score += 1;
    if (/[0-9]/.test(password)) score += 1;
    if (/[^A-Za-z0-9]/.test(password)) score += 1;
    
    return score;
  };

  const handlePasswordChange = (e) => {
    const password = e.target.value;
    if (showStrength) {
      setStrength(calculateStrength(password));
    }
    if (props.onChange) {
      props.onChange(e);
    }
  };

  const getStrengthText = () => {
    switch (strength) {
      case 0: return 'Very Weak';
      case 1: return 'Weak';
      case 2: return 'Fair';
      case 3: return 'Good';
      case 4: return 'Strong';
      case 5: return 'Very Strong';
      default: return '';
    }
  };

  const getStrengthColor = () => {
    switch (strength) {
      case 0:
      case 1: return 'strength-very-weak';
      case 2: return 'strength-weak';
      case 3: return 'strength-fair';
      case 4: return 'strength-good';
      case 5: return 'strength-strong';
      default: return '';
    }
  };

  return (
    <FormField error={error}>
      <label className="form-label">
        {label}
        {props.required && <span className="required-asterisk">*</span>}
      </label>
      <div className={`input-wrapper ${error ? 'error' : ''} ${success ? 'success' : ''}`}>
        <input
          ref={ref}
          type={showPassword ? 'text' : 'password'}
          className="form-input"
          onChange={handlePasswordChange}
          {...props}
        />
        <button
          type="button"
          className="password-toggle"
          onClick={() => setShowPassword(!showPassword)}
          aria-label={showPassword ? 'Hide password' : 'Show password'}
        >
          {showPassword ? <EyeOff size={20} /> : <Eye size={20} />}
        </button>
        {success && <CheckCircle className="input-success-icon" size={20} />}
      </div>
      
      {showStrength && props.value && (
        <motion.div 
          className="password-strength"
          initial={{ opacity: 0, height: 0 }}
          animate={{ opacity: 1, height: 'auto' }}
          transition={{ duration: 0.3 }}
        >
          <div className="strength-bar">
            <motion.div 
              className={`strength-fill ${getStrengthColor()}`}
              initial={{ width: 0 }}
              animate={{ width: `${(strength / 5) * 100}%` }}
              transition={{ duration: 0.3 }}
            />
          </div>
          <span className={`strength-text ${getStrengthColor()}`}>
            {getStrengthText()}
          </span>
        </motion.div>
      )}
    </FormField>
  );
});

// Enhanced Select component
export const Select = forwardRef(({ 
  label, 
  options = [], 
  error, 
  success, 
  placeholder = 'Select an option',
  className = '',
  ...props 
}, ref) => (
  <FormField error={error} className={className}>
    {label && (
      <label className="form-label">
        {label}
        {props.required && <span className="required-asterisk">*</span>}
      </label>
    )}
    <div className={`select-wrapper ${error ? 'error' : ''} ${success ? 'success' : ''}`}>
      <select ref={ref} className="form-select" {...props}>
        <option value="">{placeholder}</option>
        {options.map((option, index) => (
          <option key={index} value={option.value}>
            {option.label}
          </option>
        ))}
      </select>
      {success && <CheckCircle className="input-success-icon" size={20} />}
    </div>
  </FormField>
));

// Enhanced Textarea component
export const Textarea = forwardRef(({ 
  label, 
  error, 
  success, 
  hint,
  maxLength,
  showCount = false,
  className = '',
  ...props 
}, ref) => {
  const [count, setCount] = React.useState(props.value?.length || 0);

  const handleChange = (e) => {
    setCount(e.target.value.length);
    if (props.onChange) {
      props.onChange(e);
    }
  };

  return (
    <FormField error={error} className={className}>
      {label && (
        <label className="form-label">
          {label}
          {props.required && <span className="required-asterisk">*</span>}
        </label>
      )}
      <div className={`textarea-wrapper ${error ? 'error' : ''} ${success ? 'success' : ''}`}>
        <textarea
          ref={ref}
          className="form-textarea"
          maxLength={maxLength}
          onChange={handleChange}
          {...props}
        />
        {success && <CheckCircle className="textarea-success-icon" size={20} />}
      </div>
      <div className="textarea-footer">
        {hint && !error && (
          <motion.p 
            className="form-hint"
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
          >
            {hint}
          </motion.p>
        )}
        {showCount && maxLength && (
          <span className={`character-count ${count > maxLength * 0.9 ? 'warning' : ''}`}>
            {count}/{maxLength}
          </span>
        )}
      </div>
    </FormField>
  );
});

// Enhanced Button component
export const Button = ({ 
  children, 
  variant = 'primary', 
  size = 'md', 
  isLoading = false, 
  leftIcon: LeftIcon, 
  rightIcon: RightIcon,
  className = '',
  ...props 
}) => (
  <motion.button
    className={`btn btn-${variant} btn-${size} ${isLoading ? 'loading' : ''} ${className}`}
    disabled={isLoading || props.disabled}
    whileHover={!isLoading && !props.disabled ? { scale: 1.02 } : {}}
    whileTap={!isLoading && !props.disabled ? { scale: 0.98 } : {}}
    transition={{ duration: 0.1 }}
    {...props}
  >
    {isLoading && (
      <motion.div
        className="loading-spinner"
        animate={{ rotate: 360 }}
        transition={{ duration: 1, repeat: Infinity, ease: "linear" }}
      />
    )}
    {LeftIcon && !isLoading && <LeftIcon size={18} />}
    <span>{children}</span>
    {RightIcon && !isLoading && <RightIcon size={18} />}
  </motion.button>
);

// Form validation summary component
export const FormValidationSummary = ({ errors }) => {
  const errorEntries = Object.entries(errors || {});
  
  if (errorEntries.length === 0) return null;

  return (
    <motion.div
      className="validation-summary"
      initial={{ opacity: 0, y: -10 }}
      animate={{ opacity: 1, y: 0 }}
      exit={{ opacity: 0, y: -10 }}
    >
      <div className="validation-summary-header">
        <AlertCircle size={20} />
        <span>Please fix the following errors:</span>
      </div>
      <ul className="validation-summary-list">
        {errorEntries.map(([field, error]) => (
          <motion.li
            key={field}
            initial={{ opacity: 0, x: -10 }}
            animate={{ opacity: 1, x: 0 }}
            transition={{ delay: 0.1 }}
          >
            {error.message}
          </motion.li>
        ))}
      </ul>
    </motion.div>
  );
};