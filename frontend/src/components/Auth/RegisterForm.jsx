import React, { useState } from 'react';
import { useNavigate, Link } from 'react-router-dom';
import { 
  User, 
  Mail, 
  Lock, 
  Eye, 
  EyeOff, 
  ArrowRight, 
  CheckCircle2, 
  AlertCircle,
  Sparkles 
} from 'lucide-react';
import api from '../../services/api';

export default function RegisterForm({ onSuccess }) {
  const navigate = useNavigate();
  const [name, setName] = useState('');
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [confirmPassword, setConfirmPassword] = useState('');
  const [showPassword, setShowPassword] = useState(false);
  const [showConfirmPassword, setShowConfirmPassword] = useState(false);
  
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');
  const [success, setSuccess] = useState('');

  const handleSubmit = async (e) => {
    e.preventDefault();
    setError('');
    setSuccess('');

    // Frontend Validations
    if (!name.trim()) {
      setError('Full Name cannot be empty.');
      return;
    }
    if (!email.trim()) {
      setError('Email cannot be empty.');
      return;
    }
    if (!password) {
      setError('Password cannot be empty.');
      return;
    }
    if (!confirmPassword) {
      setError('Confirm Password cannot be empty.');
      return;
    }
    if (password !== confirmPassword) {
      setError('Passwords do not match.');
      return;
    }
    if (password.length < 4) {
      setError('Password must be at least 4 characters long.');
      return;
    }

    setLoading(true);

    try {
      const res = await api.register({
        name: name.trim(),
        email: email.trim().toLowerCase(),
        password,
        confirm_password: confirmPassword,
      });

      setSuccess('✓ Registration successful');
      if (onSuccess) {
        onSuccess(res);
      } else {
        setTimeout(() => {
          navigate('/dashboard');
        }, 800);
      }
    } catch (err) {
      const errMsg = err.message || 'Registration failed.';
      if (errMsg.toLowerCase().includes('already exists') || errMsg.toLowerCase().includes('already registered')) {
        setError('An account with this email already exists. Please sign in or use a different email.');
      } else {
        setError(errMsg);
      }
    } finally {
      setLoading(false);
    }
  };

  return (
    <form onSubmit={handleSubmit} className="space-y-4">
      {/* Error Message Box */}
      {error && (
        <div className="p-3.5 rounded-xl bg-rose-500/10 border border-rose-500/30 text-rose-300 text-xs flex items-start gap-2.5 animate-in fade-in duration-200">
          <AlertCircle className="w-4 h-4 text-rose-400 shrink-0 mt-0.5" />
          <div className="leading-relaxed font-medium">
            <span className="font-bold text-rose-400">✗ </span>{error}
          </div>
        </div>
      )}

      {/* Success Message Box */}
      {success && (
        <div className="p-3.5 rounded-xl bg-emerald-500/10 border border-emerald-500/30 text-emerald-300 text-xs flex items-center gap-2.5 animate-in fade-in duration-200">
          <CheckCircle2 className="w-4 h-4 text-emerald-400 shrink-0" />
          <span className="font-semibold">{success}</span>
        </div>
      )}

      {/* Full Name Field */}
      <div>
        <label className="block text-xs font-semibold text-slate-300 mb-1.5">
          Full Name
        </label>
        <div className="relative group">
          <div className="absolute inset-y-0 left-0 pl-3.5 flex items-center pointer-events-none text-slate-500 group-focus-within:text-indigo-400 transition-colors">
            <User className="w-4 h-4" />
          </div>
          <input
            type="text"
            required
            value={name}
            onChange={(e) => setName(e.target.value)}
            placeholder="Divya Sharma"
            className="w-full pl-10 pr-4 py-2.5 bg-slate-800/80 hover:bg-slate-800 text-white placeholder-slate-500 text-sm rounded-xl border border-slate-700/80 focus:border-indigo-500 focus:ring-4 focus:ring-indigo-500/20 transition-all outline-hidden"
          />
        </div>
      </div>

      {/* Email Field */}
      <div>
        <label className="block text-xs font-semibold text-slate-300 mb-1.5">
          Email Address
        </label>
        <div className="relative group">
          <div className="absolute inset-y-0 left-0 pl-3.5 flex items-center pointer-events-none text-slate-500 group-focus-within:text-indigo-400 transition-colors">
            <Mail className="w-4 h-4" />
          </div>
          <input
            type="email"
            required
            value={email}
            onChange={(e) => setEmail(e.target.value)}
            placeholder="divya@gmail.com"
            className="w-full pl-10 pr-4 py-2.5 bg-slate-800/80 hover:bg-slate-800 text-white placeholder-slate-500 text-sm rounded-xl border border-slate-700/80 focus:border-indigo-500 focus:ring-4 focus:ring-indigo-500/20 transition-all outline-hidden"
          />
        </div>
      </div>

      {/* Password Field */}
      <div>
        <label className="block text-xs font-semibold text-slate-300 mb-1.5">
          Password
        </label>
        <div className="relative group">
          <div className="absolute inset-y-0 left-0 pl-3.5 flex items-center pointer-events-none text-slate-500 group-focus-within:text-indigo-400 transition-colors">
            <Lock className="w-4 h-4" />
          </div>
          <input
            type={showPassword ? 'text' : 'password'}
            required
            value={password}
            onChange={(e) => setPassword(e.target.value)}
            placeholder="••••••••"
            className="w-full pl-10 pr-10 py-2.5 bg-slate-800/80 hover:bg-slate-800 text-white placeholder-slate-500 text-sm rounded-xl border border-slate-700/80 focus:border-indigo-500 focus:ring-4 focus:ring-indigo-500/20 transition-all outline-hidden"
          />
          <button
            type="button"
            onClick={() => setShowPassword(!showPassword)}
            className="absolute inset-y-0 right-0 pr-3.5 flex items-center text-slate-500 hover:text-slate-300 transition-colors"
          >
            {showPassword ? <EyeOff className="w-4 h-4" /> : <Eye className="w-4 h-4" />}
          </button>
        </div>
      </div>

      {/* Confirm Password Field */}
      <div>
        <label className="block text-xs font-semibold text-slate-300 mb-1.5">
          Confirm Password
        </label>
        <div className="relative group">
          <div className="absolute inset-y-0 left-0 pl-3.5 flex items-center pointer-events-none text-slate-500 group-focus-within:text-indigo-400 transition-colors">
            <Lock className="w-4 h-4" />
          </div>
          <input
            type={showConfirmPassword ? 'text' : 'password'}
            required
            value={confirmPassword}
            onChange={(e) => setConfirmPassword(e.target.value)}
            placeholder="••••••••"
            className="w-full pl-10 pr-10 py-2.5 bg-slate-800/80 hover:bg-slate-800 text-white placeholder-slate-500 text-sm rounded-xl border border-slate-700/80 focus:border-indigo-500 focus:ring-4 focus:ring-indigo-500/20 transition-all outline-hidden"
          />
          <button
            type="button"
            onClick={() => setShowConfirmPassword(!showConfirmPassword)}
            className="absolute inset-y-0 right-0 pr-3.5 flex items-center text-slate-500 hover:text-slate-300 transition-colors"
          >
            {showConfirmPassword ? <EyeOff className="w-4 h-4" /> : <Eye className="w-4 h-4" />}
          </button>
        </div>
      </div>

      {/* Submit Button */}
      <button
        type="submit"
        disabled={loading}
        className="w-full mt-3 py-3 px-4 rounded-xl ai-gradient-bg text-white font-bold text-sm shadow-lg shadow-indigo-600/30 hover:shadow-indigo-600/50 hover:opacity-95 active:scale-[0.98] transition-all flex items-center justify-center gap-2 disabled:opacity-50 cursor-pointer"
      >
        {loading ? (
          <div className="w-5 h-5 border-2 border-white/30 border-t-white rounded-full animate-spin" />
        ) : (
          <>
            <span>Create ShopAI Account</span>
            <ArrowRight className="w-4 h-4" />
          </>
        )}
      </button>

      {/* Switch to Login */}
      <div className="mt-5 text-center text-xs text-slate-400">
        Already have an account?{' '}
        <Link 
          to="/login" 
          className="text-indigo-400 hover:text-indigo-300 font-semibold underline underline-offset-2 ml-1"
        >
          Sign In here
        </Link>
      </div>
    </form>
  );
}
