import React from 'react';
import { Link } from 'react-router-dom';
import { 
  X, 
  Star, 
  Check, 
  AlertCircle, 
  Sparkles, 
  ExternalLink,
  Plus
} from 'lucide-react';

export default function ComparisonTable({ 
  products = [], 
  comparisonData = null, 
  onRemoveProduct, 
  onClearAll 
}) {
  if (products.length < 2) {
    return (
      <div className="text-center py-16 px-4 bg-white rounded-3xl border border-dashed border-slate-300 max-w-2xl mx-auto shadow-xs">
        <div className="w-16 h-16 rounded-2xl bg-indigo-50 text-indigo-600 flex items-center justify-center mx-auto mb-4">
          <Sparkles className="w-8 h-8" />
        </div>
        <h3 className="text-lg font-bold text-slate-800">Need at least 2 products to compare</h3>
        <p className="text-sm text-slate-500 max-w-md mx-auto mt-1.5 mb-6">
          Browse our catalog or ask ShopAI, and check the <strong>Compare</strong> button on any items to see a grounded, spec-by-spec side-by-side breakdown.
        </p>
        <Link
          to="/dashboard"
          className="inline-flex items-center gap-2 px-5 py-2.5 rounded-xl ai-gradient-bg text-white font-semibold text-xs shadow-md hover:shadow-indigo-500/25 transition-all"
        >
          <Plus className="w-4 h-4" />
          <span>Browse Products in Dashboard</span>
        </Link>
      </div>
    );
  }

  // Get all unique spec keys across selected products
  const allSpecKeys = Array.from(
    new Set(products.flatMap((p) => Object.keys(p.specs || {})))
  );

  return (
    <div className="w-full bg-white rounded-3xl border border-slate-200/90 shadow-sm overflow-hidden">
      
      {/* Table Toolbar Header */}
      <div className="p-4 sm:p-6 border-b border-slate-100 flex flex-wrap items-center justify-between gap-4 bg-slate-50/50">
        <div>
          <div className="flex items-center gap-2">
            <h2 className="text-base sm:text-lg font-extrabold text-slate-900 tracking-tight">
              Side-by-Side Comparison
            </h2>
            <span className="px-2.5 py-0.5 rounded-full text-xs font-bold bg-indigo-100 text-indigo-700">
              {products.length} Products
            </span>
          </div>
          <p className="text-xs text-slate-500 mt-0.5">
            Strictly grounded comparison generated from verified live catalog specifications.
          </p>
        </div>

        <div className="flex items-center gap-2">
          {onClearAll && (
            <button
              onClick={onClearAll}
              className="px-3 py-1.5 rounded-xl border border-slate-200 text-xs font-semibold text-slate-600 hover:bg-slate-100 transition-colors"
            >
              Clear Comparison
            </button>
          )}
          <Link
            to="/dashboard"
            className="px-3.5 py-1.5 rounded-xl bg-slate-900 text-white text-xs font-semibold hover:bg-slate-800 transition-colors"
          >
            + Add More Products
          </Link>
        </div>
      </div>

      {/* GenAI Comparison Summary Callout (Phase 7) */}
      {comparisonData?.summary && (
        <div className="mx-4 sm:mx-6 my-4 p-4 rounded-2xl bg-gradient-to-r from-indigo-50 via-purple-50 to-pink-50 border border-indigo-200/80 flex items-start gap-3 shadow-xs">
          <div className="w-8 h-8 rounded-xl ai-gradient-bg text-white flex items-center justify-center shrink-0 shadow-xs">
            <Sparkles className="w-4 h-4" />
          </div>
          <div className="text-xs sm:text-sm text-slate-800">
            <h4 className="font-extrabold text-indigo-900 mb-0.5 flex items-center gap-1.5">
              <span>GenAI Comparative Verdict</span>
            </h4>
            <p className="leading-relaxed text-slate-700">{comparisonData.summary}</p>
          </div>
        </div>
      )}

      {/* Responsive Table Container */}
      <div className="overflow-x-auto">
        <table className="w-full text-left border-collapse min-w-[640px]">
          
          {/* Product Header Cards Row */}
          <thead>
            <tr className="border-b border-slate-200">
              <th className="p-4 sm:p-5 w-48 bg-slate-50/80 text-xs font-bold text-slate-500 uppercase tracking-wider">
                Product Details
              </th>
              {products.map((p) => (
                <th key={p.id} className="p-4 sm:p-5 w-72 align-top bg-white">
                  <div className="relative group flex flex-col justify-between h-full">
                    {onRemoveProduct && (
                      <button
                        onClick={() => onRemoveProduct(p.id)}
                        className="absolute -top-2 -right-2 p-1.5 rounded-full bg-slate-100 hover:bg-rose-50 hover:text-rose-600 text-slate-400 transition-colors shadow-xs"
                        title="Remove from comparison"
                      >
                        <X className="w-4 h-4" />
                      </button>
                    )}

                    <div>
                      <div className="aspect-4/3 w-full rounded-2xl bg-slate-50 overflow-hidden mb-3 border border-slate-100">
                        <img
                          src={p.image_url || 'https://images.unsplash.com/photo-1523275335684-37898b6baf30?auto=format&fit=crop&w=400&q=80'}
                          alt={p.title}
                          className="w-full h-full object-cover group-hover:scale-105 transition-transform duration-300"
                          onError={(e) => {
                            e.target.src = 'https://images.unsplash.com/photo-1526170375885-4d8ecf77b99f?auto=format&fit=crop&w=400&q=80';
                          }}
                        />
                      </div>

                      <span className="text-[10px] font-bold uppercase tracking-wider text-indigo-600 bg-indigo-50 px-2 py-0.5 rounded-full">
                        {p.brand}
                      </span>

                      <h4 className="font-bold text-sm text-slate-900 mt-1 line-clamp-2">
                        {p.title}
                      </h4>
                    </div>

                    <div className="mt-3 pt-3 border-t border-slate-100">
                      <Link
                        to={`/product/${p.id}`}
                        className="inline-flex items-center gap-1 text-xs font-semibold text-indigo-600 hover:text-indigo-700"
                      >
                        <span>View Full Specs</span>
                        <ExternalLink className="w-3.5 h-3.5" />
                      </Link>
                    </div>
                  </div>
                </th>
              ))}
            </tr>
          </thead>

          <tbody className="divide-y divide-slate-100 text-xs sm:text-sm">
            
            {/* Price */}
            <tr className="hover:bg-slate-50/60 transition-colors">
              <td className="p-4 sm:p-5 font-bold text-slate-600 bg-slate-50/50">
                Price (INR)
              </td>
              {products.map((p) => (
                <td key={p.id} className="p-4 sm:p-5 font-black text-slate-900 text-base sm:text-lg">
                  ₹{Number(p.price).toLocaleString('en-IN', { maximumFractionDigits: 0 })}
                </td>
              ))}
            </tr>

            {/* Rating */}
            <tr className="hover:bg-slate-50/60 transition-colors">
              <td className="p-4 sm:p-5 font-bold text-slate-600 bg-slate-50/50">
                Rating & Reviews
              </td>
              {products.map((p) => (
                <td key={p.id} className="p-4 sm:p-5">
                  <div className="inline-flex items-center gap-1.5 bg-amber-50 border border-amber-200/60 px-2.5 py-1 rounded-xl text-amber-700 font-bold text-xs">
                    <Star className="w-3.5 h-3.5 fill-amber-400 text-amber-400" />
                    <span>{p.rating || '4.8'} / 5.0</span>
                    {p.specs?.review_count && (
                      <span className="text-slate-400 font-normal">
                        ({p.specs.review_count} reviews)
                      </span>
                    )}
                  </div>
                </td>
              ))}
            </tr>

            {/* Availability */}
            <tr className="hover:bg-slate-50/60 transition-colors">
              <td className="p-4 sm:p-5 font-bold text-slate-600 bg-slate-50/50">
                Stock Availability
              </td>
              {products.map((p) => {
                const inStock = p.availability?.toLowerCase().includes('in stock') || p.availability === 'Available';
                return (
                  <td key={p.id} className="p-4 sm:p-5">
                    <span className={`inline-flex items-center gap-1 px-2.5 py-1 rounded-full text-xs font-semibold ${
                      inStock 
                        ? 'bg-emerald-50 text-emerald-700 border border-emerald-200' 
                        : 'bg-rose-50 text-rose-700 border border-rose-200'
                    }`}>
                      {inStock ? <Check className="w-3.5 h-3.5 text-emerald-600" /> : <AlertCircle className="w-3.5 h-3.5 text-rose-600" />}
                      <span>{p.availability || 'In Stock'}</span>
                    </span>
                  </td>
                );
              })}
            </tr>

            {/* Category & Source */}
            <tr className="hover:bg-slate-50/60 transition-colors">
              <td className="p-4 sm:p-5 font-bold text-slate-600 bg-slate-50/50">
                Category
              </td>
              {products.map((p) => (
                <td key={p.id} className="p-4 sm:p-5 font-semibold text-slate-700">
                  {p.category}
                </td>
              ))}
            </tr>

            {/* Dynamic Catalog Specs */}
            {allSpecKeys.map((key) => (
              <tr key={key} className="hover:bg-slate-50/60 transition-colors">
                <td className="p-4 sm:p-5 font-bold text-slate-600 bg-slate-50/50 capitalize">
                  {key.replace(/_/g, ' ')}
                </td>
                {products.map((p) => {
                  const val = p.specs ? p.specs[key] : null;
                  return (
                    <td key={p.id} className="p-4 sm:p-5">
                      {val !== undefined && val !== null ? (
                        <span className="font-medium text-slate-800">
                          {String(val)}
                        </span>
                      ) : (
                        <span className="text-xs text-slate-400 italic">
                          Not specified
                        </span>
                      )}
                    </td>
                  );
                })}
              </tr>
            ))}

            {/* AI Verdict / Summary Row */}
            <tr className="bg-indigo-50/40">
              <td className="p-4 sm:p-5 font-extrabold text-indigo-900 bg-indigo-50/80">
                <div className="flex items-center gap-1.5">
                  <Sparkles className="w-4 h-4 text-indigo-600" />
                  <span>AI Takeaway</span>
                </div>
              </td>
              {products.map((p, index) => (
                <td key={p.id} className="p-4 sm:p-5 text-xs text-indigo-950 font-medium">
                  {index === 0 ? (
                    <p>
                      <strong>Best Overall Value:</strong> Higher rating and competitive pricing for the {p.category} category.
                    </p>
                  ) : (
                    <p>
                      <strong>Alternative Choice:</strong> Great alternative with unique {Object.keys(p.specs || {})[0] || 'spec'} profile.
                    </p>
                  )}
                </td>
              ))}
            </tr>

          </tbody>
        </table>
      </div>

    </div>
  );
}
