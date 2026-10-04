import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { 
  User, 
  Mail, 
  Calendar, 
  ShieldCheck, 
  KeyRound, 
  Save, 
  CheckCircle2, 
  AlertCircle,
  Eye,
  EyeOff,
  LogOut,
  XCircle,
  Sparkles
} from 'lucide-react';
import Navbar from '../components/Navbar';
import api from '../services/api';

export default function Profile() {
  const navigate = useNavigate();
  const [profile, setProfile] = useState(null);
  const [loading, setLoading] = useState(true);

  // Name Edit State
  const [nameInput, setNameInput] = useState('');
  const [nameLoading, setNameLoading] = useState(false);
  const [nameSuccess, setNameSuccess] = useState('');
  const [nameError, setNameError] = useState('');

  // Password Edit State
  const [currentPassword, setCurrentPassword] = useState('');
  const [newPassword, setNewPassword] = useState('');
  const [confirmPassword, setConfirmPassword] = useState('');
  const [showCurrentPassword, setShowCurrentPassword] = useState(false);
  const [showNewPassword, setShowNewPassword] = useState(false);
  const [showConfirmPassword, setShowConfirmPassword] = useState(false);
  
  const [passwordLoading, setPasswordLoading] = useState(false);
  const [passwordSuccess, setPasswordSuccess] = useState('');
  const [passwordError, setPasswordError] = useState('');

  // Password rules validation for new password
  const passCriteria = {
    length: newPassword.length >= 8,
    upper: /[A-Z]/.test(newPassword),
    lower: /[a-z]/.test(newPassword),
    number: /[0-9]/.test(newPassword),
    special: /[!@#$%^&*(),.?":{}|<>\-_+=[\]\\/`~;']/.test(newPassword),
  };
  const isPasswordValid = Object.values(passCriteria).every(Boolean);

  useEffect(() => {
    async function loadProfile() {
      try {
        const res = await api.getProfile();
        if (res && res.user) {
          setProfile(res.user);
          setNameInput(res.user.name);
        }
      } catch (e) {
        console.warn('Profile fetch error:', e);
        const local = api.getCurrentUser();
        if (local) {
          setProfile(local);
          setNameInput(local.name || '');
        }
      } finally {
        setLoading(false);
      }
    }
    loadProfile();
  }, []);

  const handleUpdateName = async (e) => {
    e.preventDefault();
    setNameError('');
    setNameSuccess('');

    if (!nameInput.trim()) {
      setNameError('Full Name cannot be empty.');
      return;
    }

    setNameLoading(true);
    try {
      await api.updateProfile(nameInput.trim());
      setNameSuccess('Name updated successfully!');
      setProfile((prev) => ({ ...prev, name: nameInput.trim() }));
      setTimeout(() => setNameSuccess(''), 4000);
    } catch (err) {
      setNameError(err.message || 'Failed to update name.');
    } finally {
      setNameLoading(false);
    }
  };

  const handleChangePassword = async (e) => {
    e.preventDefault();
    setPasswordError('');
    setPasswordSuccess('');

    if (!currentPassword) {
      setPasswordError('Please enter your current password.');
      return;
    }
    if (!newPassword) {
      setPasswordError('Please enter a new password.');
      return;
    }
    if (newPassword !== confirmPassword) {
      setPasswordError('New passwords do not match.');
      return;
    }
    if (!isPasswordValid) {
      setPasswordError('New password must be at least 8 characters and meet complexity rules.');
      return;
    }

    setPasswordLoading(true);
    try {
      await api.changePassword({
        current_password: currentPassword,
        new_password: newPassword,
        confirm_password: confirmPassword,
      });

      setPasswordSuccess('Password changed successfully!');
      setCurrentPassword('');
      setNewPassword('');
      setConfirmPassword('');
      setTimeout(() => setPasswordSuccess(''), 4000);
    } catch (err) {
      setPasswordError(err.message || 'Failed to change password.');
    } finally {
      setPasswordLoading(false);
    }
  };

  const handleLogout = () => {
    api.logout();
    navigate('/login');
  };

  if (loading) {
    return (
      <div className="min-h-screen bg-slate-900 flex items-center justify-center">
        <div className="w-10 h-10 border-4 border-indigo-500/30 border-t-indigo-500 rounded-full animate-spin" />
      </div>
    );
  }

  const joinDateFormatted = profile?.created_at
    ? new Date(profile.created_at).toLocaleDateString('en-US', {
        year: 'numeric',
        month: 'long',
        day: 'numeric',
      })
    : 'Recently';

  return (
    <div className="min-h-screen bg-slate-950 text-slate-100 flex flex-col selection:bg-indigo-500 selection:text-white">
      <Navbar />

      <main className="flex-1 max-w-4xl w-full mx-auto px-4 py-8 sm:px-6 lg:px-8">
        
        {/* Profile Header Card */}
        <div className="glass-panel-dark rounded-3xl p-6 sm:p-8 mb-8 border border-white/10 shadow-xl relative overflow-hidden">
          <div className="absolute top-0 right-0 -mt-8 -mr-8 w-64 h-64 bg-indigo-600/20 rounded-full blur-3xl pointer-events-none" />
          
          <div className="flex flex-col sm:flex-row items-center sm:items-start gap-6 relative z-10">
            <img
              src={profile?.avatar || `https://api.dicebear.com/7.x/avataaars/svg?seed=${profile?.name || 'User'}`}
              alt="User Avatar"
              className="w-24 h-24 rounded-2xl ring-4 ring-indigo-500/30 bg-slate-800 object-cover shadow-lg shadow-indigo-500/10"
            />

            <div className="flex-1 text-center sm:text-left">
              <div className="flex flex-wrap items-center justify-center sm:justify-start gap-3 mb-1">
                <h1 className="text-2xl sm:text-3xl font-extrabold text-white tracking-tight">
                  {profile?.name || 'ShopAI User'}
                </h1>
                {profile?.is_verified ? (
                  <span className="inline-flex items-center gap-1 text-[11px] font-bold px-2.5 py-0.5 rounded-full bg-emerald-500/20 border border-emerald-500/40 text-emerald-300">
                    <ShieldCheck className="w-3.5 h-3.5" />
                    <span>Verified Account</span>
                  </span>
                ) : (
                  <span className="inline-flex items-center gap-1 text-[11px] font-bold px-2.5 py-0.5 rounded-full bg-amber-500/20 border border-amber-500/40 text-amber-300">
                    <span>Unverified</span>
                  </span>
                )}
              </div>

              <p className="text-slate-400 text-sm mb-4">{profile?.email || 'user@shopai.com'}</p>

              <div className="flex flex-wrap items-center justify-center sm:justify-start gap-6 text-xs text-slate-400 border-t border-slate-800/80 pt-4">
                <div className="flex items-center gap-1.5">
                  <Calendar className="w-4 h-4 text-indigo-400" />
                  <span>Member since {joinDateFormatted}</span>
                </div>
                <div className="flex items-center gap-1.5">
                  <Sparkles className="w-4 h-4 text-pink-400" />
                  <span>ShopAI GenAI 2.0 Active</span>
                </div>
              </div>
            </div>

            <button
              onClick={handleLogout}
              className="self-center sm:self-start px-4 py-2 rounded-xl bg-rose-500/10 hover:bg-rose-500/20 border border-rose-500/30 text-rose-300 text-xs font-semibold transition-all flex items-center gap-2 cursor-pointer"
            >
              <LogOut className="w-4 h-4" />
              <span>Sign Out</span>
            </button>
          </div>
        </div>

        <div className="grid grid-cols-1 md:grid-cols-2 gap-8">
          
          {/* Card 1: Change Name */}
          <div className="glass-panel-dark rounded-3xl p-6 sm:p-7 border border-white/10 shadow-xl flex flex-col justify-between">
            <div>
              <div className="flex items-center gap-2.5 mb-4">
                <div className="w-9 h-9 rounded-xl bg-indigo-500/20 text-indigo-400 flex items-center justify-center">
                  <User className="w-5 h-5" />
                </div>
                <div>
                  <h2 className="text-base font-bold text-white">Personal Information</h2>
                  <p className="text-slate-400 text-xs">Update your display name across ShopAI</p>
                </div>
              </div>

              {nameSuccess && (
                <div className="mb-4 p-3 rounded-xl bg-emerald-500/10 border border-emerald-500/30 text-emerald-300 text-xs flex items-center gap-2">
                  <CheckCircle2 className="w-4 h-4 text-emerald-400 shrink-0" />
                  <span>{nameSuccess}</span>
                </div>
              )}

              {nameError && (
                <div className="mb-4 p-3 rounded-xl bg-rose-500/10 border border-rose-500/30 text-rose-300 text-xs flex items-center gap-2">
                  <AlertCircle className="w-4 h-4 text-rose-400 shrink-0" />
                  <span>{nameError}</span>
                </div>
              )}

              <form onSubmit={handleUpdateName} className="space-y-4">
                <div>
                  <label className="block text-xs font-semibold text-slate-300 mb-1.5">
                    Full Name
                  </label>
                  <input
                    type="text"
                    required
                    value={nameInput}
                    onChange={(e) => setNameInput(e.target.value)}
                    className="w-full px-3.5 py-2.5 bg-slate-800/80 hover:bg-slate-800 text-white placeholder-slate-500 text-sm rounded-xl border border-slate-700/80 focus:border-indigo-500 focus:ring-4 focus:ring-indigo-500/20 transition-all outline-hidden"
                  />
                </div>

                <div>
                  <label className="block text-xs font-semibold text-slate-400 mb-1.5">
                    Email Address (Read-only)
                  </label>
                  <input
                    type="email"
                    disabled
                    value={profile?.email || ''}
                    className="w-full px-3.5 py-2.5 bg-slate-900/60 text-slate-500 text-sm rounded-xl border border-slate-800 cursor-not-allowed outline-hidden"
                  />
                </div>

                <button
                  type="submit"
                  disabled={nameLoading}
                  className="w-full py-2.5 px-4 rounded-xl ai-gradient-bg text-white font-bold text-xs shadow-md shadow-indigo-600/30 hover:shadow-indigo-600/50 transition-all flex items-center justify-center gap-2 disabled:opacity-50 cursor-pointer"
                >
                  {nameLoading ? (
                    <div className="w-4 h-4 border-2 border-white/30 border-t-white rounded-full animate-spin" />
                  ) : (
                    <>
                      <Save className="w-3.5 h-3.5" />
                      <span>Save Name</span>
                    </>
                  )}
                </button>
              </form>
            </div>
          </div>

          {/* Card 2: Change Password */}
          <div className="glass-panel-dark rounded-3xl p-6 sm:p-7 border border-white/10 shadow-xl">
            <div className="flex items-center gap-2.5 mb-4">
              <div className="w-9 h-9 rounded-xl bg-purple-500/20 text-purple-400 flex items-center justify-center">
                <KeyRound className="w-5 h-5" />
              </div>
              <div>
                <h2 className="text-base font-bold text-white">Security & Password</h2>
                <p className="text-slate-400 text-xs">Update your credentials with bcrypt encryption</p>
              </div>
            </div>

            {passwordSuccess && (
              <div className="mb-4 p-3 rounded-xl bg-emerald-500/10 border border-emerald-500/30 text-emerald-300 text-xs flex items-center gap-2">
                <CheckCircle2 className="w-4 h-4 text-emerald-400 shrink-0" />
                <span>{passwordSuccess}</span>
              </div>
            )}

            {passwordError && (
              <div className="mb-4 p-3 rounded-xl bg-rose-500/10 border border-rose-500/30 text-rose-300 text-xs flex items-center gap-2">
                <AlertCircle className="w-4 h-4 text-rose-400 shrink-0" />
                <span>{passwordError}</span>
              </div>
            )}

            <form onSubmit={handleChangePassword} className="space-y-3.5">
              {/* Current Password */}
              <div>
                <label className="block text-xs font-semibold text-slate-300 mb-1">
                  Current Password
                </label>
                <div className="relative">
                  <input
                    type={showCurrentPassword ? 'text' : 'password'}
                    required
                    value={currentPassword}
                    onChange={(e) => setCurrentPassword(e.target.value)}
                    placeholder="••••••••"
                    className="w-full px-3.5 pr-10 py-2 bg-slate-800/80 hover:bg-slate-800 text-white placeholder-slate-500 text-sm rounded-xl border border-slate-700/80 focus:border-indigo-500 focus:ring-4 focus:ring-indigo-500/20 transition-all outline-hidden"
                  />
                  <button
                    type="button"
                    onClick={() => setShowCurrentPassword(!showCurrentPassword)}
                    className="absolute inset-y-0 right-0 pr-3 flex items-center text-slate-500 hover:text-slate-300 cursor-pointer"
                  >
                    {showCurrentPassword ? <EyeOff className="w-3.5 h-3.5" /> : <Eye className="w-3.5 h-3.5" />}
                  </button>
                </div>
              </div>

              {/* New Password */}
              <div>
                <label className="block text-xs font-semibold text-slate-300 mb-1">
                  New Password
                </label>
                <div className="relative">
                  <input
                    type={showNewPassword ? 'text' : 'password'}
                    required
                    value={newPassword}
                    onChange={(e) => setNewPassword(e.target.value)}
                    placeholder="e.g. Divya@123"
                    className="w-full px-3.5 pr-10 py-2 bg-slate-800/80 hover:bg-slate-800 text-white placeholder-slate-500 text-sm rounded-xl border border-slate-700/80 focus:border-indigo-500 focus:ring-4 focus:ring-indigo-500/20 transition-all outline-hidden"
                  />
                  <button
                    type="button"
                    onClick={() => setShowNewPassword(!showNewPassword)}
                    className="absolute inset-y-0 right-0 pr-3 flex items-center text-slate-500 hover:text-slate-300 cursor-pointer"
                  >
                    {showNewPassword ? <EyeOff className="w-3.5 h-3.5" /> : <Eye className="w-3.5 h-3.5" />}
                  </button>
                </div>
              </div>

              {/* Real-time criteria for new password */}
              {newPassword.length > 0 && (
                <div className="p-2.5 rounded-xl bg-slate-800/60 border border-slate-700/70 space-y-1 text-[10px]">
                  <div className="grid grid-cols-2 gap-1">
                    <span className={passCriteria.length ? 'text-emerald-400' : 'text-slate-500'}>✓ 8+ Chars</span>
                    <span className={passCriteria.upper ? 'text-emerald-400' : 'text-slate-500'}>✓ Uppercase</span>
                    <span className={passCriteria.lower ? 'text-emerald-400' : 'text-slate-500'}>✓ Lowercase</span>
                    <span className={passCriteria.number ? 'text-emerald-400' : 'text-slate-500'}>✓ Number</span>
                    <span className={`col-span-2 ${passCriteria.special ? 'text-emerald-400' : 'text-slate-500'}`}>✓ Special char (!@#$%...)</span>
                  </div>
                </div>
              )}

              {/* Confirm New Password */}
              <div>
                <label className="block text-xs font-semibold text-slate-300 mb-1">
                  Confirm New Password
                </label>
                <div className="relative">
                  <input
                    type={showConfirmPassword ? 'text' : 'password'}
                    required
                    value={confirmPassword}
                    onChange={(e) => setConfirmPassword(e.target.value)}
                    placeholder="••••••••"
                    className="w-full px-3.5 pr-10 py-2 bg-slate-800/80 hover:bg-slate-800 text-white placeholder-slate-500 text-sm rounded-xl border border-slate-700/80 focus:border-indigo-500 focus:ring-4 focus:ring-indigo-500/20 transition-all outline-hidden"
                  />
                  <button
                    type="button"
                    onClick={() => setShowConfirmPassword(!showConfirmPassword)}
                    className="absolute inset-y-0 right-0 pr-3 flex items-center text-slate-500 hover:text-slate-300 cursor-pointer"
                  >
                    {showConfirmPassword ? <EyeOff className="w-3.5 h-3.5" /> : <Eye className="w-3.5 h-3.5" />}
                  </button>
                </div>
              </div>

              <button
                type="submit"
                disabled={passwordLoading}
                className="w-full mt-2 py-2.5 px-4 rounded-xl bg-purple-600 hover:bg-purple-500 text-white font-bold text-xs shadow-md shadow-purple-600/30 transition-all flex items-center justify-center gap-2 disabled:opacity-50 cursor-pointer"
              >
                {passwordLoading ? (
                  <div className="w-4 h-4 border-2 border-white/30 border-t-white rounded-full animate-spin" />
                ) : (
                  <>
                    <KeyRound className="w-3.5 h-3.5" />
                    <span>Update Password</span>
                  </>
                )}
              </button>
            </form>
          </div>

        </div>

      </main>
    </div>
  );
}
