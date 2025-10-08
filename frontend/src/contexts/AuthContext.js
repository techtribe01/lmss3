import React, { createContext, useContext, useEffect, useState } from 'react';
import { supabase } from '../lib/supabase';

const AuthContext = createContext(null);

export const AuthProvider = ({ children }) => {
  const [user, setUser] = useState(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    // First, try to restore session from localStorage
    const restoreSession = () => {
      try {
        const storedUser = localStorage.getItem('user');
        const storedToken = localStorage.getItem('supabase_token');
        
        if (storedUser && storedToken) {
          const userData = JSON.parse(storedUser);
          console.log('Restoring session for user:', userData.email, 'with role:', userData.role);
          setUser(userData);
          setLoading(false);
          return true;
        }
      } catch (error) {
        console.error('Error restoring session:', error);
        localStorage.removeItem('user');
        localStorage.removeItem('supabase_token');
      }
      return false;
    };

    // Check if Supabase is configured
    if (!supabase) {
      console.warn('Supabase not configured. Checking localStorage...');
      if (!restoreSession()) {
        setLoading(false);
      }
      return;
    }

    // If session restored from localStorage, still verify with Supabase
    const sessionRestored = restoreSession();

    // Get current Supabase session
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
          console.log('Supabase session found for:', userData.email, 'with role:', userData.role);
          setUser(userData);
          localStorage.setItem('supabase_token', session.access_token);
          localStorage.setItem('user', JSON.stringify(userData));
        } else if (!sessionRestored) {
          // Only clear if we didn't restore from localStorage
          setUser(null);
          localStorage.removeItem('supabase_token');
          localStorage.removeItem('user');
        }
      } catch (error) {
        console.error('Error getting session:', error);
        if (!sessionRestored) {
          setUser(null);
          localStorage.removeItem('supabase_token');
          localStorage.removeItem('user');
        }
      } finally {
        setLoading(false);
      }
    };

    getSession();

    // Listen for auth changes
    const { data: { subscription } } = supabase.auth.onAuthStateChange(
      async (event, session) => {
        console.log('Auth state changed:', event, session?.user?.email);
        
        if (session) {
          const userData = {
            id: session.user.id,
            email: session.user.email,
            full_name: session.user.user_metadata?.full_name || session.user.email,
            username: session.user.user_metadata?.username || session.user.email,
            role: session.user.user_metadata?.role || 'student'
          };
          console.log('Setting user from auth change:', userData.email, 'with role:', userData.role);
          setUser(userData);
          localStorage.setItem('supabase_token', session.access_token);
          localStorage.setItem('user', JSON.stringify(userData));
        } else if (event === 'SIGNED_OUT') {
          console.log('User signed out, clearing session');
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