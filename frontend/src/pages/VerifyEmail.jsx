import React, { useState, useEffect } from 'react';
import { useParams, useNavigate, Link } from 'react-router-dom';
import { 
  Sparkles, 
  CheckCircle2, 
  XCircle, 
  ArrowRight, 
  ShieldCheck,
  MailCheck 
} from 'lucide-react';
import api from '../services/api';

export default function VerifyEmail() {
  const { token } = useParams();
  const navigate = useNavigate();

  const [status, setStatus] = useState('verifying'); // verifying | success | error
  const [message, setMessage] = useState('');

  useEffect(() => {
    async function verify() {
      if (!token) {
        setStatus('error');
        setMessage('Missing verification token in link.');
        return;
      }

      try {
        const res = await api.verifyEmail(token);
        setStatus('success');
        setMessage(res.message || 'Email verified successfully! You can now log in.');
      } catch (err) {
        setStatus('error');
        setMessage(err.message || 'Verification link is invalid or has expired.');
      }
    }

    verify();
  }, [token]);

  return (
    <div className="min-h-screen relative flex items-center justify-center p-4 bg-slate-900 overflow-hidden">
      {/* Ambient Glows */}
      <div className="absolute top-1/4 -left-32 w-96 h-96 bg-indigo-600/30 rounded-full blur-[128px] pointer-events-none" />
      <div className="absolute bottom-1/4 -right-32 w-96 h-96 bg-purple-600/30 rounded-full blur-[128px] pointer-events-none" />

      <div className="relative z-10 w-full max-w-md my-8">
        
        {/* Brand Header */}
        <div className="text-center mb-6">
          <Link to="/" className="inline-flex items-center justify-center w-14 h-14 rounded-2xl ai-gradient-bg text-white shadow-xl shadow-indigo-500/30 mb-3 transform hover:scale-105 transition-transform">
            <Sparkles className="w-8 h-8 animate-pulse" />
          </Link>
          <h1 className="text-3xl font-extrabold text-white tracking-tight">
            Email Verification
          </h1>
          <p className="text-slate-400 text-xs sm:text-sm mt-1">
            ShopAI Production Account Security
          </p>
        </div>

        {/* Verification Status Card */}
        <div className="glass-panel-dark rounded-3xl p-6 sm:p-8 shadow-2xl border border-white/10 backdrop-blur-2xl text-center">
          
          {status === 'verifying' && (
            <div className="py-6 space-y-4">
              <div className="w-12 h-12 border-4 border-indigo-500/30 border-t-indigo-500 rounded-full animate-spin mx-auto" />
              <p className="text-sm font-semibold text-slate-300">Verifying your email address...</p>
            </div>
          )}

          {status === 'success' && (
            <div className="space-y-4 animate-in fade-in zoom-in-95 duration-200">
              <div className="w-16 h-16 rounded-2xl bg-emerald-500/20 border border-emerald-500/40 text-emerald-400 flex items-center justify-center mx-auto">
                <CheckCircle2 className="w-8 h-8" />
              </div>
              <h2 className="text-xl font-bold text-white">Email Verified!</h2>
              <p className="text-xs sm:text-sm text-slate-300 leading-relaxed">
                {message}
              </p>
              <Link
                to="/login"
                className="w-full mt-4 py-3 px-4 rounded-xl ai-gradient-bg text-white font-bold text-sm shadow-lg shadow-indigo-600/30 hover:shadow-indigo-600/50 transition-all flex items-center justify-center gap-2"
              >
                <span>Proceed to Sign In</span>
                <ArrowRight className="w-4 h-4" />
              </Link>
            </div>
          )}

          {status === 'error' && (
            <div className="space-y-4 animate-in fade-in zoom-in-95 duration-200">
              <div className="w-16 h-16 rounded-2xl bg-rose-500/20 border border-rose-500/40 text-rose-400 flex items-center justify-center mx-auto">
                <XCircle className="w-8 h-8" />
              </div>
              <h2 className="text-xl font-bold text-white">Verification Failed</h2>
              <p className="text-xs sm:text-sm text-rose-300 leading-relaxed">
                {message}
              </p>
              <div className="pt-2 flex flex-col gap-2">
                <Link
                  to="/register"
                  className="w-full py-2.5 px-4 rounded-xl bg-slate-800/80 hover:bg-slate-800 text-white font-semibold text-xs border border-slate-700 transition-all"
                >
                  Register New Account
                </Link>
                <Link
                  to="/login"
                  className="text-xs font-semibold text-indigo-400 hover:text-indigo-300 mt-2"
                >
                  Back to Sign In
                </Link>
              </div>
            </div>
          )}

        </div>

      </div>
    </div>
  );
}
