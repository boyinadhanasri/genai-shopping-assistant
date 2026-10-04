import React from 'react';
import { 
  Cpu, 
  Shirt, 
  Sparkles, 
  Home, 
  BookOpen, 
  Dumbbell, 
  Zap, 
  Smartphone,
  Gamepad2,
  ChevronRight
} from 'lucide-react';

const ICON_MAP = {
  Cpu,
  Shirt,
  Sparkles,
  Home,
  BookOpen,
  Dumbbell,
  Zap,
  Smartphone,
  Gamepad2,
  Toy: Gamepad2,
};

const CATEGORY_COLORS = {
  electronics: {
    bg: 'from-blue-500/10 to-indigo-500/20',
    iconBg: 'bg-indigo-600 text-white',
    border: 'hover:border-indigo-300',
    activeBg: 'bg-indigo-600 text-white',
  },
  fashion: {
    bg: 'from-pink-500/10 to-rose-500/20',
    iconBg: 'bg-rose-500 text-white',
    border: 'hover:border-rose-300',
    activeBg: 'bg-rose-600 text-white',
  },
  toys: {
    bg: 'from-amber-500/10 to-yellow-500/20',
    iconBg: 'bg-yellow-500 text-white',
    border: 'hover:border-yellow-300',
    activeBg: 'bg-yellow-600 text-white',
  },
  beauty: {
    bg: 'from-purple-500/10 to-fuchsia-500/20',
    iconBg: 'bg-purple-600 text-white',
    border: 'hover:border-purple-300',
    activeBg: 'bg-purple-600 text-white',
  },
  home_and_kitchen: {
    bg: 'from-amber-500/10 to-orange-500/20',
    iconBg: 'bg-amber-500 text-white',
    border: 'hover:border-amber-300',
    activeBg: 'bg-amber-600 text-white',
  },
  books: {
    bg: 'from-emerald-500/10 to-teal-500/20',
    iconBg: 'bg-teal-600 text-white',
    border: 'hover:border-teal-300',
    activeBg: 'bg-teal-600 text-white',
  },
  sports: {
    bg: 'from-cyan-500/10 to-sky-500/20',
    iconBg: 'bg-sky-600 text-white',
    border: 'hover:border-sky-300',
    activeBg: 'bg-sky-600 text-white',
  },
};

export default function CategoryCard({ 
  category, 
  isActive = false, 
  onClick 
}) {
  const IconComponent = ICON_MAP[category.icon] || Cpu;
  const colorScheme = CATEGORY_COLORS[category.id] || CATEGORY_COLORS.electronics;

  return (
    <button
      type="button"
      onClick={() => onClick && onClick(category.name)}
      className={`group relative text-left p-4 rounded-2xl border transition-all duration-300 w-full flex items-center justify-between gap-3 cursor-pointer ${
        isActive
          ? 'bg-gradient-to-r from-slate-900 via-indigo-950 to-slate-900 text-white border-indigo-500/50 shadow-xl shadow-indigo-500/15 ring-2 ring-indigo-500/40 scale-[1.02]'
          : 'bg-white hover:bg-slate-50/90 border-slate-200/90 text-slate-800 hover:shadow-lg hover:border-indigo-200/80 hover:-translate-y-0.5'
      }`}
    >
      <div className="flex items-center gap-3.5">
        <div className={`w-12 h-12 rounded-xl flex items-center justify-center shrink-0 transition-transform group-hover:scale-110 shadow-xs ${
          isActive ? 'ai-gradient-bg text-white shadow-indigo-500/30' : colorScheme.iconBg
        }`}>
          <IconComponent className="w-6 h-6" />
        </div>

        <div>
          <div className="flex items-center gap-2">
            <h3 className={`font-black text-sm tracking-tight ${isActive ? 'text-white' : 'text-slate-900'}`}>
              {category.name}
            </h3>
            {category.count && (
              <span className={`text-[10px] font-bold px-2 py-0.5 rounded-full ${
                isActive ? 'bg-indigo-900/80 text-indigo-200 border border-indigo-700/50' : 'bg-slate-100 text-slate-500'
              }`}>
                {category.count}+
              </span>
            )}
          </div>
          <p className={`text-xs mt-0.5 line-clamp-1 ${isActive ? 'text-indigo-200/80' : 'text-slate-500'}`}>
            {category.description || 'Explore trending items'}
          </p>
        </div>
      </div>

      <div className={`p-1.5 rounded-lg transition-all group-hover:translate-x-1 ${
        isActive ? 'text-indigo-300' : 'text-slate-300 group-hover:text-indigo-600'
      }`}>
        <ChevronRight className="w-4 h-4" />
      </div>
    </button>
  );
}
