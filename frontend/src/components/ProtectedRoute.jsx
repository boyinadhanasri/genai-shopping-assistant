import React, { useEffect, useState } from 'react';
import { Navigate, useLocation } from 'react-router-dom';
import api from '../services/api';

/**
 * Route protection guard for authenticated routes (/dashboard, /chat, /compare, /profile, etc.)
 * 
 * Strict behavior:
 * 1. Checks JWT token in localStorage.
 * 2. If token is missing -> Immediately redirects to /login.
 * 3. If token exists -> Validates with GET /api/auth/me.
 * 4. If token is invalid or expired -> Clears storage and redirects to /login with session expired message.
 */
export default function ProtectedRoute({ children }) {
  const location = useLocation();
  const [isValidating, setIsValidating] = useState(true);
  const [isAuthenticated, setIsAuthenticated] = useState(false);

  useEffect(() => {
    let isMounted = true;

    const validateSession = async () => {
      const token = localStorage.getItem('shopai_token');
      const user = api.getCurrentUser();

      if (!token || !user || !user.id) {
        if (isMounted) {
          setIsAuthenticated(false);
          setIsValidating(false);
        }
        return;
      }

      try {
        // Validate with backend GET /api/auth/me
        await api.getProfile();
        if (isMounted) {
          setIsAuthenticated(true);
          setIsValidating(false);
        }
      } catch (err) {
        console.warn('Session token validation failed:', err);
        api.logout();
        if (isMounted) {
          setIsAuthenticated(false);
          setIsValidating(false);
        }
      }
    };

    validateSession();

    return () => {
      isMounted = false;
    };
  }, [location.pathname]);

  if (isValidating) {
    return (
      <div className="min-h-screen bg-slate-900 flex flex-col items-center justify-center text-white">
        <div className="w-10 h-10 border-3 border-indigo-500 border-t-transparent rounded-full animate-spin mb-4" />
        <p className="text-slate-400 text-xs font-semibold tracking-wider uppercase">
          Verifying secure session...
        </p>
      </div>
    );
  }

  if (!isAuthenticated) {
    return (
      <Navigate 
        to="/login" 
        state={{ 
          from: location,
          sessionExpired: true 
        }} 
        replace 
      />
    );
  }

  return children;
}
