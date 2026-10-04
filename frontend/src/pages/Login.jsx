import React, { useState, useEffect } from 'react';
import { useNavigate, useSearchParams, useLocation, Link } from 'react-router-dom';
import { 
  Sparkles, 
  Mail, 
  Lock, 
  Eye, 
  EyeOff, 
  ArrowRight, 
  ShieldCheck, 
  CheckCircle2, 
  AlertCircle,
  KeyRound
} from 'lucide-react';
import api from '../services/api';

export default function Login() {
  const navigate = useNavigate();
  const location = useLocation();
  const [searchParams] = useSearchParams();

  const emailParam = searchParams.get('email') || '';
  const verifiedParam = searchParams.get('verified') === '1';
  const from = location.state?.from?.pathname || '/dashboard';

  const [email, setEmail] = useState(emailParam);
  const [password, setPassword] = useState('');
  const [showPassword, setShowPassword] = useState(false);

  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(
    location.state?.sessionExpired ? 'Session expired. Please login again.' : ''
  );
  const [unverifiedEmail, setUnverifiedEmail] = useState('');
  const [success, setSuccess] = useState(verifiedParam ? 'Email verified! Please sign in with your credentials.' : '');

  // Auto-login check
  useEffect(() => {
    const token = localStorage.getItem('shopai_token');
    const user = api.getCurrentUser();
    if (token && user && user.id) {
      navigate('/dashboard', { replace: true });
    }
  }, [navigate]);

  const handleSubmit = async (e) => {
    e.preventDefault();
    setError('');
    setUnverifiedEmail('');

    const cleanEmail = email.trim().toLowerCase();
    if (!cleanEmail || !password) {
      setError('Invalid email or password.');
      return;
    }

    setLoading(true);
    try {
      await api.login({
        email: cleanEmail,
        password,
      });

      navigate(from, { replace: true });
    } catch (err) {
      const msg = err.message || 'Invalid email or password.';
      if (msg.toLowerCase().includes('verify your email')) {
        setError('Please verify your email before login.');
        setUnverifiedEmail(cleanEmail);
      } else {
        setError(msg);
      }
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="min-h-screen relative flex items-center justify-center p-4 bg-slate-900 overflow-hidden font-sans">
      {/* Dynamic Ambient Background Glows */}
      <div className="absolute top-1/4 -left-32 w-96 h-96 bg-indigo-600/30 rounded-full blur-[128px] pointer-events-none" />
      <div className="absolute bottom-1/4 -right-32 w-96 h-96 bg-purple-600/30 rounded-full blur-[128px] pointer-events-none" />
      <div className="absolute top-1/2 left-1/2 -translate-x-1/2 -translate-y-1/2 w-[600px] h-[600px] bg-pink-500/10 rounded-full blur-[150px] pointer-events-none" />

      <div className="relative z-10 w-full max-w-md my-8">
        
        {/* Brand Header */}
        <div className="text-center mb-6">
          <Link to="/" className="inline-flex items-center justify-center w-14 h-14 rounded-2xl ai-gradient-bg text-white shadow-xl shadow-indigo-500/30 mb-3 transform hover:scale-105 transition-transform">
            <Sparkles className="w-8 h-8 animate-pulse" />
          </Link>
          <h1 className="text-2xl sm:text-3xl font-extrabold text-white tracking-tight">
            Sign In to <span className="ai-gradient-text">ShopAI</span>
          </h1>
          <p className="text-slate-400 text-xs sm:text-sm mt-1">
            Access your personalized shopping deals and AI comparisons
          </p>
        </div>

        {/* Card */}
        <div className="glass-panel-dark rounded-3xl p-6 sm:p-8 shadow-2xl border border-white/10 backdrop-blur-2xl">
          
          {success && (
            <div className="mb-5 p-3.5 rounded-xl bg-emerald-500/10 border border-emerald-500/30 text-emerald-300 text-xs flex items-center gap-2.5 animate-in fade-in duration-200">
              <CheckCircle2 className="w-4 h-4 text-emerald-400 shrink-0" />
              <span>{success}</span>
            </div>
          )}

          {error && (
            <div className="mb-5 p-3.5 rounded-xl bg-rose-500/10 border border-rose-500/30 text-rose-300 text-xs flex items-start gap-2.5 animate-in fade-in duration-200">
              <AlertCircle className="w-4 h-4 text-rose-400 shrink-0 mt-0.5" />
              <div className="leading-relaxed font-medium">
                <span>{error}</span>
                {unverifiedEmail && (
                  <div className="mt-2">
                    <Link
                      to={`/verify-otp?email=${encodeURIComponent(unverifiedEmail)}`}
                      className="inline-flex items-center gap-1.5 px-3 py-1.5 rounded-lg bg-rose-500/20 hover:bg-rose-500/30 text-rose-200 font-semibold text-xs transition-colors"
                    >
                      <KeyRound className="w-3.5 h-3.5" />
                      <span>Verify OTP Now</span>
                    </Link>
                  </div>
                )}
              </div>
            </div>
          )}

          <form onSubmit={handleSubmit} className="space-y-4">
            
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
                  placeholder="name@example.com"
                  className="w-full pl-10 pr-4 py-2.5 bg-slate-800/80 hover:bg-slate-800 text-white placeholder-slate-500 text-sm rounded-xl border border-slate-700/80 focus:border-indigo-500 focus:ring-4 focus:ring-indigo-500/20 transition-all outline-hidden"
                />
              </div>
            </div>

            {/* Password Field */}
            <div>
              <div className="flex items-center justify-between mb-1.5">
                <label className="block text-xs font-semibold text-slate-300">
                  Password
                </label>
                <Link 
                  to={`/forgot-password${email ? `?email=${encodeURIComponent(email)}` : ''}`} 
                  className="text-xs text-indigo-400 hover:text-indigo-300 transition-colors font-medium"
                >
                  Forgot Password?
                </Link>
              </div>
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
                  className="absolute inset-y-0 right-0 pr-3.5 flex items-center text-slate-500 hover:text-slate-300 transition-colors cursor-pointer"
                >
                  {showPassword ? <EyeOff className="w-4 h-4" /> : <Eye className="w-4 h-4" />}
                </button>
              </div>
            </div>

            {/* Submit Button */}
            <button
              type="submit"
              disabled={loading}
              className="w-full mt-2 py-3 px-4 rounded-xl ai-gradient-bg text-white font-bold text-sm shadow-lg shadow-indigo-600/30 hover:shadow-indigo-600/50 hover:opacity-95 active:scale-[0.98] transition-all flex items-center justify-center gap-2 disabled:opacity-50 cursor-pointer"
            >
              {loading ? (
                <div className="w-5 h-5 border-2 border-white/30 border-t-white rounded-full animate-spin" />
              ) : (
                <>
                  <span>Sign In</span>
                  <ArrowRight className="w-4 h-4" />
                </>
              )}
            </button>

          </form>

          {/* Create Account Link */}
          <div className="mt-6 pt-5 border-t border-slate-700/60 text-center text-xs text-slate-400">
            Don't have an account yet?{' '}
            <Link 
              to="/register" 
              className="text-indigo-400 hover:text-indigo-300 font-semibold underline underline-offset-2 ml-1"
            >
              Create Account
            </Link>
          </div>

        </div>

        {/* Feature Badges Footer */}
        <div className="mt-6 flex items-center justify-center gap-6 text-slate-400 text-xs">
          <div className="flex items-center gap-1.5">
            <ShieldCheck className="w-4 h-4 text-emerald-400" />
            <span>JWT Authenticated</span>
          </div>
          <div className="flex items-center gap-1.5">
            <CheckCircle2 className="w-4 h-4 text-indigo-400" />
            <span>Verified Catalogs</span>
          </div>
        </div>

      </div>
    </div>
  );
}
