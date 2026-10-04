import React, { useState } from 'react';
import { Link, useNavigate, useLocation } from 'react-router-dom';
import {
  Sparkles,
  Search,
  Scale,
  User,
  LogOut,
  ChevronDown,
  ShoppingBag,
  UserPlus,
  LogIn
} from 'lucide-react';
import api from '../services/api';

export default function Navbar({ compareCount = 0, onSearchSubmit }) {
  const navigate = useNavigate();
  const location = useLocation();
  const [searchInput, setSearchInput] = useState('');
  const [isProfileOpen, setIsProfileOpen] = useState(false);

  const token = localStorage.getItem('shopai_token');
  const currentUser = api.getCurrentUser();
  const isLoggedIn = !!(token && currentUser && currentUser.id);

  const handleSearch = (e) => {
    e.preventDefault();
    if (searchInput.trim()) {
      if (onSearchSubmit) {
        onSearchSubmit(searchInput.trim());
      } else {
        navigate(`/dashboard?q=${encodeURIComponent(searchInput.trim())}`);
      }
    }
  };

  const handleLogout = () => {
    api.logout();
    navigate('/login', { replace: true });
  };

  return (
    <header className="sticky top-0 z-40 w-full glass-panel border-b border-slate-200/80 shadow-xs">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="flex items-center justify-between h-16 gap-4">

          {/* Brand Logo */}
          <Link to="/dashboard" className="flex items-center gap-2.5 group shrink-0">
            <div className="w-10 h-10 rounded-xl ai-gradient-bg flex items-center justify-center text-white shadow-md shadow-indigo-500/25 group-hover:scale-105 transition-transform">
              <Sparkles className="w-5 h-5 animate-pulse" />
            </div>
            <div>
              <span className="font-extrabold text-xl tracking-tight bg-gradient-to-r from-indigo-600 via-purple-600 to-pink-600 bg-clip-text text-transparent">
                ShopAI
              </span>
              <span className="hidden sm:inline-block ml-1.5 text-[10px] font-bold tracking-wider uppercase px-1.5 py-0.5 rounded-full bg-indigo-50 text-indigo-600 border border-indigo-100">
                GenAI 2.0
              </span>
            </div>
          </Link>

          {/* Central AI Search Bar */}
          <form onSubmit={handleSearch} className="flex-1 max-w-xl mx-2">
            <div className="relative group">
              <div className="absolute inset-y-0 left-0 pl-3.5 flex items-center pointer-events-none text-slate-400 group-focus-within:text-indigo-600 transition-colors">
                <Search className="w-4 h-4" />
              </div>
              <input
                type="text"
                value={searchInput}
                onChange={(e) => setSearchInput(e.target.value)}
                placeholder="Ask ShopAI: 'MacBook under ₹80k for coding' or 'Wireless earbuds'..."
                className="w-full pl-10 pr-24 py-2 text-sm bg-slate-100/80 hover:bg-slate-100 focus:bg-white text-slate-800 placeholder-slate-400 rounded-xl border border-transparent focus:border-indigo-500 focus:ring-4 focus:ring-indigo-500/10 transition-all outline-hidden"
              />
              <div className="absolute inset-y-0 right-1.5 flex items-center gap-1">
                <button
                  type="submit"
                  className="px-3 py-1 bg-indigo-600 hover:bg-indigo-700 text-white text-xs font-semibold rounded-lg shadow-sm transition-colors flex items-center gap-1 cursor-pointer"
                >
                  <span>Ask AI</span>
                  <Sparkles className="w-3 h-3 text-indigo-200" />
                </button>
              </div>
            </div>
          </form>

          {/* Navigation & Actions */}
          <div className="flex items-center gap-3 shrink-0">

            {/* Compare Tray Button */}
            <Link
              to={isLoggedIn ? "/compare" : "/login?from=/compare"}
              className={`relative flex items-center gap-1.5 px-3 py-2 rounded-xl text-xs font-semibold transition-all ${location.pathname === '/compare'
                  ? 'bg-indigo-600 text-white shadow-md shadow-indigo-500/20'
                  : 'bg-white hover:bg-slate-100 text-slate-700 border border-slate-200'
                }`}
            >
              <Scale className="w-4 h-4" />
              <span className="hidden md:inline">Compare</span>
              {compareCount > 0 && (
                <span className="inline-flex items-center justify-center min-w-5 h-5 px-1.5 text-[11px] font-bold rounded-full bg-pink-500 text-white shadow-xs animate-bounce">
                  {compareCount}
                </span>
              )}
            </Link>

            {isLoggedIn ? (
              /* Profile Dropdown */
              <div className="relative">
                <button
                  onClick={() => setIsProfileOpen(!isProfileOpen)}
                  className="flex items-center gap-2 p-1.5 rounded-xl hover:bg-slate-100 transition-colors border border-transparent focus:border-slate-300 cursor-pointer"
                >
                  <img
                    src={currentUser?.avatar || `https://api.dicebear.com/7.x/avataaars/svg?seed=${currentUser?.name || 'User'}`}
                    alt="User Avatar"
                    className="w-8 h-8 rounded-full ring-2 ring-indigo-500/20 bg-slate-100 object-cover"
                  />
                  <span className="hidden lg:block text-xs font-semibold text-slate-700 max-w-[100px] truncate">
                    {currentUser?.name || 'My Account'}
                  </span>
                  <ChevronDown className="w-3.5 h-3.5 text-slate-400" />
                </button>

                {/* Profile Menu Popup */}
                {isProfileOpen && (
                  <div
                    className="absolute right-0 mt-2 w-56 glass-panel rounded-2xl shadow-xl py-2 z-50 animate-in fade-in slide-in-from-top-2 duration-150"
                    onClick={() => setIsProfileOpen(false)}
                  >
                    <div className="px-4 py-2 border-b border-slate-100">
                      <p className="text-xs font-bold text-slate-800">{currentUser?.name || 'Authenticated User'}</p>
                      <p className="text-[11px] text-slate-500 truncate">{currentUser?.email}</p>
                    </div>

                    <Link
                      to="/dashboard"
                      className="flex items-center gap-2.5 px-4 py-2 text-xs font-medium text-slate-700 hover:bg-indigo-50 hover:text-indigo-600 transition-colors"
                    >
                      <ShoppingBag className="w-4 h-4 text-slate-400" />
                      <span>Dashboard Home</span>
                    </Link>

                    <Link
                      to="/profile"
                      className="flex items-center gap-2.5 px-4 py-2 text-xs font-medium text-slate-700 hover:bg-indigo-50 hover:text-indigo-600 transition-colors"
                    >
                      <User className="w-4 h-4 text-slate-400" />
                      <span>My Profile</span>
                    </Link>

                    <Link
                      to="/compare"
                      className="flex items-center gap-2.5 px-4 py-2 text-xs font-medium text-slate-700 hover:bg-indigo-50 hover:text-indigo-600 transition-colors"
                    >
                      <Scale className="w-4 h-4 text-slate-400" />
                      <span>Comparison Deck ({compareCount})</span>
                    </Link>

                    <div className="my-1 border-t border-slate-100" />

                    <button
                      onClick={handleLogout}
                      className="w-full flex items-center gap-2.5 px-4 py-2 text-xs font-medium text-rose-600 hover:bg-rose-50 transition-colors text-left cursor-pointer"
                    >
                      <LogOut className="w-4 h-4 text-rose-500" />
                      <span>Sign Out</span>
                    </button>
                  </div>
                )}
              </div>
            ) : (
              <div className="flex items-center gap-2">
                <Link
                  to="/login"
                  className="inline-flex items-center gap-1.5 px-3.5 py-1.5 rounded-xl text-xs font-semibold text-slate-700 hover:text-indigo-600 hover:bg-slate-100 transition-colors"
                >
                  <LogIn className="w-3.5 h-3.5" />
                  <span>Log In</span>
                </Link>
                <Link
                  to="/register"
                  className="inline-flex items-center gap-1.5 px-3.5 py-1.5 rounded-xl text-xs font-bold text-white ai-gradient-bg shadow-sm hover:shadow-md transition-all"
                >
                  <UserPlus className="w-3.5 h-3.5" />
                  <span>Register</span>
                </Link>
              </div>
            )}

          </div>
        </div>
      </div>
    </header>
  );
}
