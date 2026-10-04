import React from 'react';
import { Link } from 'react-router-dom';
import { Star, Scale, Check, ArrowRight, Sparkles, Award, Zap, ThumbsUp } from 'lucide-react';

export default function ProductCard({ 
  product, 
  isCompared = false, 
  onToggleCompare, 
  horizontal = false 
}) {
  if (!product) return null;

  const formattedPrice = new Intl.NumberFormat('en-IN', {
    style: 'currency',
    currency: 'INR',
    maximumFractionDigits: 0,
  }).format(product.price);

  const isInStock = product.availability?.toLowerCase().includes('in stock') || product.availability === 'Available';
  
  // Extract key specs for pills
  const specEntries = Object.entries(product.specs || {}).slice(0, 3);

  // Rank and Score details
  const rankNumber = product.rank || (product.badge?.includes('#1') ? 1 : product.badge?.includes('#2') ? 2 : null);
  const scoreValue = product.score || product.match_score || null;
  const isTopRank = rankNumber === 1 || product.badge?.toLowerCase().includes('top recommendation') || product.badge?.includes('#1');
  const isRunnerUp = rankNumber === 2 || product.badge?.toLowerCase().includes('runner up') || product.badge?.includes('#2');

  const rankBadgeText = isTopRank 
    ? '#1 TOP RECOMMENDATION' 
    : isRunnerUp 
    ? '#2 RUNNER UP' 
    : product.badge;

  if (horizontal) {
    return (
      <div className={`group relative flex flex-col sm:flex-row bg-white rounded-2xl border transition-all duration-300 overflow-hidden min-w-[320px] sm:min-w-[420px] max-w-[480px] ${
        isTopRank 
          ? 'border-amber-300 shadow-md shadow-amber-500/10 hover:shadow-xl hover:border-amber-400 ring-1 ring-amber-200/50' 
          : isRunnerUp
          ? 'border-indigo-300 shadow-md shadow-indigo-500/10 hover:shadow-xl hover:border-indigo-400'
          : 'border-slate-200/90 shadow-xs hover:shadow-xl hover:border-indigo-200'
      }`}>
        {/* Product Image */}
        <div className="relative w-full sm:w-44 h-48 sm:h-auto bg-slate-50 shrink-0 overflow-hidden">
          <img
            src={product.image_url || 'https://images.unsplash.com/photo-1523275335684-37898b6baf30?auto=format&fit=crop&w=600&q=80'}
            alt={product.title}
            className="w-full h-full object-cover group-hover:scale-105 transition-transform duration-500"
            onError={(e) => {
              e.target.src = 'https://images.unsplash.com/photo-1526170375885-4d8ecf77b99f?auto=format&fit=crop&w=600&q=80';
            }}
          />
          <div className="absolute top-2.5 left-2.5 flex flex-col gap-1">
            {rankBadgeText && (
              <span className={`px-2 py-0.5 text-[9px] font-extrabold rounded-md tracking-wider uppercase backdrop-blur-md shadow-xs flex items-center gap-1 ${
                isTopRank 
                  ? 'bg-amber-500 text-white ring-1 ring-amber-300' 
                  : isRunnerUp
                  ? 'bg-indigo-600 text-white'
                  : 'bg-slate-800 text-white'
              }`}>
                {isTopRank && <Award className="w-3 h-3 text-amber-100" />}
                {isRunnerUp && <Zap className="w-3 h-3 text-indigo-100" />}
                <span>{rankBadgeText}</span>
              </span>
            )}
            <span className={`px-2 py-0.5 text-[9px] font-bold rounded-md tracking-wider uppercase backdrop-blur-md ${
              isInStock 
                ? 'bg-emerald-500/90 text-white shadow-xs' 
                : 'bg-amber-500/90 text-white'
            }`}>
              {product.availability || 'In Stock'}
            </span>
          </div>
        </div>

        {/* Info */}
        <div className="p-4 flex flex-col justify-between flex-1">
          <div>
            <div className="flex items-center justify-between gap-1 mb-1.5">
              <div className="flex items-center gap-1.5 flex-wrap">
                <span className="text-[11px] font-bold tracking-wider uppercase text-indigo-600 bg-indigo-50 px-2 py-0.5 rounded-full">
                  {product.brand}
                </span>
                {product.category && (
                  <span className="text-[10px] font-semibold text-slate-600 bg-slate-100 px-2 py-0.5 rounded-full">
                    {product.category}
                  </span>
                )}
              </div>

              {/* Score pill */}
              {scoreValue && (
                <div className={`px-2 py-0.5 rounded-full text-[11px] font-extrabold flex items-center gap-1 ${
                  isTopRank 
                    ? 'bg-amber-50 text-amber-800 border border-amber-300' 
                    : 'bg-indigo-50 text-indigo-800 border border-indigo-200'
                }`}>
                  <Sparkles className="w-3 h-3" />
                  <span>Score: {scoreValue}/100</span>
                </div>
              )}
            </div>

            <Link 
              to={`/product/${product.id}`}
              className="font-bold text-slate-800 text-sm hover:text-indigo-600 transition-colors line-clamp-2 mt-1"
            >
              {product.title}
            </Link>

            <div className="flex items-center gap-2 mt-1.5 text-xs text-slate-500">
              <span className="flex items-center gap-0.5 font-bold text-amber-500">
                <Star className="w-3.5 h-3.5 fill-amber-400 text-amber-400" />
                <span>{product.rating || '4.5'}</span>
              </span>
              <span>·</span>
              <span className="font-extrabold text-slate-900 text-sm">
                {formattedPrice}
              </span>
            </div>

            {/* Why Recommended Bullets */}
            {product.why_recommended && product.why_recommended.length > 0 && (
              <div className="mt-2.5 p-2 bg-slate-50 border border-slate-200/80 rounded-xl text-[10px] space-y-1">
                <span className="font-extrabold text-indigo-900 block uppercase tracking-wider text-[9px]">
                  Why Recommended:
                </span>
                {product.why_recommended.slice(0, 3).map((reason, idx) => (
                  <p key={idx} className="text-slate-700 font-medium leading-tight">
                    {reason.startsWith('✓') ? reason : `✓ ${reason}`}
                  </p>
                ))}
              </div>
            )}
          </div>

          <div className="mt-3 pt-2.5 border-t border-slate-100 flex items-center justify-between gap-2">
            <div className="flex items-center gap-1.5">
              <button
                type="button"
                onClick={() => onToggleCompare && onToggleCompare(product)}
                className={`p-2 rounded-xl text-xs font-semibold flex items-center gap-1 transition-all ${
                  isCompared
                    ? 'bg-pink-600 text-white shadow-sm ring-2 ring-pink-400/30'
                    : 'bg-slate-100 hover:bg-slate-200 text-slate-700'
                }`}
                title={isCompared ? 'Remove from compare' : 'Add to compare'}
              >
                {isCompared ? <Check className="w-3.5 h-3.5" /> : <Scale className="w-3.5 h-3.5" />}
              </button>

              <Link
                to={`/product/${product.id}`}
                className="px-3.5 py-1.5 bg-indigo-600 hover:bg-indigo-700 text-white text-xs font-semibold rounded-xl shadow-xs transition-colors flex items-center gap-1"
              >
                <span>View Details</span>
                <ArrowRight className="w-3.5 h-3.5" />
              </Link>
            </div>
          </div>
        </div>
      </div>
    );
  }

  // Standard Vertical Grid Card
  return (
    <div className={`group relative flex flex-col bg-white rounded-2xl border transition-all duration-300 overflow-hidden ${
      isTopRank 
        ? 'border-amber-400 shadow-lg shadow-amber-500/10 hover:shadow-2xl ring-2 ring-amber-300/60' 
        : isRunnerUp
        ? 'border-indigo-300 shadow-md shadow-indigo-500/10 hover:shadow-xl ring-1 ring-indigo-200'
        : 'border-slate-200/90 shadow-xs hover:shadow-xl hover:border-indigo-300'
    }`}>
      
      {/* Top Banner Tag */}
      <div className="relative aspect-4/3 bg-slate-50 overflow-hidden">
        <img
          src={product.image_url || 'https://images.unsplash.com/photo-1523275335684-37898b6baf30?auto=format&fit=crop&w=600&q=80'}
          alt={product.title}
          className="w-full h-full object-cover group-hover:scale-105 transition-transform duration-500"
          onError={(e) => {
            e.target.src = 'https://images.unsplash.com/photo-1526170375885-4d8ecf77b99f?auto=format&fit=crop&w=600&q=80';
          }}
        />

        {/* Floating Rank & Score Badges */}
        <div className="absolute top-3 left-3 flex flex-col gap-1.5 items-start">
          {rankBadgeText && (
            <span className={`px-2.5 py-1 text-[10px] font-black rounded-lg tracking-wide uppercase backdrop-blur-md shadow-md flex items-center gap-1.5 ${
              isTopRank
                ? 'bg-amber-500 text-white ring-2 ring-amber-300'
                : isRunnerUp
                ? 'bg-indigo-600 text-white ring-1 ring-indigo-300'
                : 'bg-slate-900 text-white'
            }`}>
              {isTopRank && <Award className="w-3.5 h-3.5 text-amber-200" />}
              {isRunnerUp && <Zap className="w-3.5 h-3.5 text-indigo-200" />}
              <span>{rankBadgeText}</span>
            </span>
          )}

          <div className="flex items-center gap-1">
            {scoreValue && (
              <span className={`px-2 py-0.5 text-[9px] font-extrabold rounded-md shadow-xs backdrop-blur-md flex items-center gap-1 ${
                isTopRank 
                  ? 'bg-amber-900/90 text-amber-100 border border-amber-400' 
                  : 'bg-slate-900/80 text-white'
              }`}>
                <Sparkles className="w-2.5 h-2.5 text-amber-300" />
                <span>Score: {scoreValue}/100</span>
              </span>
            )}

            <span className={`px-2 py-0.5 text-[9px] font-bold rounded-md tracking-wider uppercase backdrop-blur-md ${
              isInStock 
                ? 'bg-emerald-600/90 text-white shadow-2xs' 
                : 'bg-amber-600/90 text-white'
            }`}>
              {product.availability || 'In Stock'}
            </span>
            {product.discount_percent && product.discount_percent > 0 && (
              <span className="px-1.5 py-0.5 text-[9px] font-extrabold rounded-md bg-rose-600 text-white shadow-2xs">
                {product.discount_percent}% OFF
              </span>
            )}
          </div>
        </div>

        {/* Quick Compare Button in Top Right */}
        <button
          type="button"
          onClick={() => onToggleCompare && onToggleCompare(product)}
          className={`absolute top-3 right-3 p-2 rounded-xl backdrop-blur-md transition-all shadow-md cursor-pointer ${
            isCompared
              ? 'bg-pink-600 text-white ring-2 ring-white'
              : 'bg-white/90 hover:bg-white text-slate-700 hover:text-indigo-600'
          }`}
          title={isCompared ? 'Remove from comparison' : 'Add to side-by-side compare'}
        >
          {isCompared ? <Check className="w-4 h-4" /> : <Scale className="w-4 h-4" />}
        </button>
      </div>

      {/* Content */}
      <div className="p-4 flex flex-col justify-between flex-1">
        <div>
          <div className="flex items-center justify-between mb-1.5">
            <div className="flex items-center gap-1.5 flex-wrap">
              <span className="text-[11px] font-bold tracking-wider uppercase text-indigo-600 bg-indigo-50 px-2 py-0.5 rounded-full">
                {product.brand}
              </span>
              {product.category && (
                <span className="text-[10px] font-semibold text-slate-600 bg-slate-100 px-2 py-0.5 rounded-full">
                  {product.category}
                </span>
              )}
            </div>
            <div className="flex items-center gap-1 text-amber-500 text-xs font-semibold bg-amber-50 px-2 py-0.5 rounded-full">
              <Star className="w-3.5 h-3.5 fill-amber-400 text-amber-400" />
              <span>{product.rating || '4.8'}</span>
            </div>
          </div>

          <Link 
            to={`/product/${product.id}`}
            className="font-bold text-slate-800 text-sm hover:text-indigo-600 transition-colors line-clamp-2"
          >
            {product.title}
          </Link>

          {/* Why Recommended Explanation Checklist */}
          {product.why_recommended && product.why_recommended.length > 0 && (
            <div className="mt-3 p-2.5 bg-slate-50 border border-slate-200/90 rounded-xl text-[11px] text-slate-800 space-y-1 shadow-2xs">
              <div className="font-extrabold text-indigo-900 text-[10px] uppercase tracking-wider flex items-center gap-1 mb-1">
                <Sparkles className="w-3 h-3 text-indigo-600" />
                <span>Why Recommended:</span>
              </div>
              {product.why_recommended.slice(0, 4).map((reason, idx) => (
                <p key={idx} className="text-slate-700 font-medium leading-snug">
                  {reason.startsWith('✓') ? reason : `✓ ${reason}`}
                </p>
              ))}
            </div>
          )}

          {/* Quick Specs Snippets */}
          {specEntries.length > 0 && (!product.why_recommended || product.why_recommended.length === 0) && (
            <div className="flex flex-wrap gap-1 mt-2.5">
              {specEntries.map(([key, val]) => (
                <span key={key} className="text-[10px] bg-slate-100 text-slate-600 px-2 py-0.5 rounded-md font-medium">
                  {key}: {String(val)}
                </span>
              ))}
            </div>
          )}
        </div>

        {/* Price & Action */}
        <div className="mt-4 pt-3 border-t border-slate-100 flex items-center justify-between">
          <div>
            <span className="text-[11px] text-slate-400 block -mb-0.5">Price</span>
            <span className="text-lg font-extrabold text-slate-900 tracking-tight">
              {formattedPrice}
            </span>
          </div>

          <Link
            to={`/product/${product.id}`}
            className="px-3.5 py-1.5 bg-slate-900 hover:bg-indigo-600 text-white text-xs font-semibold rounded-xl shadow-xs transition-colors flex items-center gap-1 cursor-pointer"
          >
            <span>Details</span>
            <ArrowRight className="w-3.5 h-3.5" />
          </Link>
        </div>

      </div>
    </div>
  );
}
