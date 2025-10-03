import React, { createContext, useContext, useEffect, useState } from 'react';
import { supabase } from '../lib/supabase';

const AuthContext = createContext(null);

export const AuthProvider = ({ children }) => {
  const [user, setUser] = useState(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    // Check if Supabase is configured
    if (!supabase) {
      console.warn('Supabase not configured. Authentication features disabled.');
      setLoading(false);
      return;
    }

    // Get initial session
    const getSession = async () => {
      try {
        const { data: { session } } = await supabase.auth.getSession();
        if (session) {
          const userData = {
            id: session.user.id,
            email: session.user.email,
            full_name: session.user.user_metadata?.full_name || session.user.email,
            username: session.user.user_metadata?.username || session.user.email,
            role: session.user.user_metadata?.role || 'student'
          };
          setUser(userData);
          // Store token for API calls
          localStorage.setItem('supabase_token', session.access_token);
          localStorage.setItem('user', JSON.stringify(userData));
        }
      } catch (error) {
        console.error('Error getting session:', error);
      } finally {
        setLoading(false);
      }
    };

    getSession();

    // Listen for auth changes
    const { data: { subscription } } = supabase.auth.onAuthStateChange(
      async (event, session) => {
        if (session) {
          const userData = {
            id: session.user.id,
            email: session.user.email,
            full_name: session.user.user_metadata?.full_name || session.user.email,
            username: session.user.user_metadata?.username || session.user.email,
            role: session.user.user_metadata?.role || 'student'
          };
          setUser(userData);
          localStorage.setItem('supabase_token', session.access_token);
          localStorage.setItem('user', JSON.stringify(userData));
        } else {
          setUser(null);
          localStorage.removeItem('supabase_token');
          localStorage.removeItem('user');
        }
        setLoading(false);
      }
    );

    return () => subscription.unsubscribe();
  }, []);

  const login = (token, userData) => {
    setUser(userData);
    localStorage.setItem('supabase_token', token);
    localStorage.setItem('user', JSON.stringify(userData));
  };

  const logout = async () => {
    if (supabase) {
      await supabase.auth.signOut();
    }
    setUser(null);
    localStorage.removeItem('supabase_token');
    localStorage.removeItem('user');
  };

  const getToken = () => {
    return localStorage.getItem('supabase_token');
  };

  return (
    <AuthContext.Provider value={{ user, login, logout, loading, getToken }}>
      {children}
    </AuthContext.Provider>
  );
};

export const useAuth = () => {
  const context = useContext(AuthContext);
  if (!context) {
    throw new Error('useAuth must be used within an AuthProvider');
  }
  return context;
};