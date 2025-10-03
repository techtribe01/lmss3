const BACKEND_URL = process.env.REACT_APP_BACKEND_URL || 'http://localhost:8001';

// Get auth token from localStorage
const getAuthToken = () => {
  return localStorage.getItem('supabase_token');
};

// Base API call function with authentication
export const apiCall = async (endpoint, options = {}) => {
  const token = getAuthToken();
  
  const config = {
    headers: {
      'Content-Type': 'application/json',
      ...(token && { Authorization: `Bearer ${token}` }),
      ...options.headers,
    },
    ...options,
  };

  const url = `${BACKEND_URL}/api${endpoint}`;
  
  const response = await fetch(url, config);
  
  if (!response.ok) {
    const errorData = await response.json().catch(() => ({}));
    throw new Error(errorData.detail || `HTTP error! status: ${response.status}`);
  }
  
  return response.json();
};

// Convenience methods
export const get = (endpoint, options = {}) => 
  apiCall(endpoint, { method: 'GET', ...options });

export const post = (endpoint, data, options = {}) => 
  apiCall(endpoint, { 
    method: 'POST', 
    body: JSON.stringify(data), 
    ...options 
  });

export const put = (endpoint, data, options = {}) => 
  apiCall(endpoint, { 
    method: 'PUT', 
    body: JSON.stringify(data), 
    ...options 
  });

export const del = (endpoint, options = {}) => 
  apiCall(endpoint, { method: 'DELETE', ...options });