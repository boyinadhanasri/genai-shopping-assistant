import React, { useState, useEffect } from 'react';
import { BrowserRouter, Routes, Route, Navigate } from 'react-router-dom';
import Login from './pages/Login';
import Register from './pages/Register';
import ForgotPassword from './pages/ForgotPassword';
import ResetPassword from './pages/ResetPassword';
import VerifyOTP from './pages/VerifyOTP';
import VerifyEmail from './pages/VerifyEmail';
import Profile from './pages/Profile';
import Dashboard from './pages/Dashboard';
import ProductDetails from './pages/ProductDetails';
import Compare from './pages/Compare';
import Chat from './pages/Chat';
import ProtectedRoute from './components/ProtectedRoute';

export default function App() {
  // Global comparison set across entire app: id -> product object
  const [compareSet, setCompareSet] = useState(() => {
    try {
      const saved = localStorage.getItem('shopai_compare_tray');
      if (saved) {
        const parsed = JSON.parse(saved);
        return new Map(parsed.map((p) => [p.id, p]));
      }
    } catch (e) {
      console.warn('Failed to restore compare tray:', e);
    }
    return new Map();
  });

  // Persist compare tray in localStorage
  useEffect(() => {
    try {
      const items = Array.from(compareSet.values());
      localStorage.setItem('shopai_compare_tray', JSON.stringify(items));
    } catch (e) {
      console.warn('Failed to save compare tray:', e);
    }
  }, [compareSet]);

  const handleToggleCompare = (product) => {
    if (!product || !product.id) return;
    setCompareSet((prev) => {
      const next = new Map(prev);
      if (next.has(product.id)) {
        next.delete(product.id);
      } else {
        next.set(product.id, product);
      }
      return next;
    });
  };

  return (
    <BrowserRouter>
      <Routes>
        {/* Public Authentication Routes */}
        <Route path="/login" element={<Login />} />
        <Route path="/register" element={<Register />} />
        <Route path="/verify-otp" element={<VerifyOTP />} />
        <Route path="/forgot-password" element={<ForgotPassword />} />
        <Route path="/reset-password" element={<ResetPassword />} />
        <Route path="/reset-password/:token" element={<ResetPassword />} />
        <Route path="/verify-email/:token" element={<VerifyEmail />} />

        {/* Public Browsing Routes (Catalog, Products & Categories) */}
        <Route 
          path="/" 
          element={
            <Dashboard 
              compareSet={compareSet} 
              setCompareSet={setCompareSet} 
              onToggleCompare={handleToggleCompare} 
            />
          } 
        />
        <Route 
          path="/dashboard" 
          element={
            <Dashboard 
              compareSet={compareSet} 
              setCompareSet={setCompareSet} 
              onToggleCompare={handleToggleCompare} 
            />
          } 
        />
        <Route 
          path="/product/:id" 
          element={
            <ProductDetails 
              compareSet={compareSet} 
              onToggleCompare={handleToggleCompare} 
            />
          } 
        />

        {/* AI-Powered & User Protected Routes (Strictly Require JWT Auth) */}
        <Route 
          path="/profile" 
          element={
            <ProtectedRoute>
              <Profile />
            </ProtectedRoute>
          } 
        />

        <Route 
          path="/compare" 
          element={
            <ProtectedRoute>
              <Compare 
                compareSet={compareSet} 
                setCompareSet={setCompareSet} 
                onToggleCompare={handleToggleCompare} 
              />
            </ProtectedRoute>
          } 
        />

        <Route 
          path="/chat" 
          element={
            <ProtectedRoute>
              <Chat 
                compareSet={compareSet} 
                onToggleCompare={handleToggleCompare} 
              />
            </ProtectedRoute>
          } 
        />

        {/* Fallback Route */}
        <Route path="*" element={<Navigate to="/dashboard" replace />} />
      </Routes>
    </BrowserRouter>
  );
}
