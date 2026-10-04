import React, { useState, useEffect } from 'react';
import { useParams, Link, useNavigate } from 'react-router-dom';
import { 
  ArrowLeft, 
  Star, 
  Scale, 
  Check, 
  ShieldCheck, 
  Truck, 
  RotateCcw, 
  Sparkles,
  ShoppingBag,
  Share2,
  Info
} from 'lucide-react';
import Navbar from '../components/Navbar';
import ChatWidget from '../components/ChatWidget';
import api from '../services/api';

export default function ProductDetails({ compareSet, onToggleCompare }) {
  const { id } = useParams();
  const navigate = useNavigate();
  const [product, setProduct] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [activeTab, setActiveTab] = useState('specs');
  const [copied, setCopied] = useState(false);

  useEffect(() => {
    async function loadProduct() {
      setLoading(true);
      setError(null);
      try {
        const data = await api.getProductDetails(id);
        setProduct(data);
      } catch (err) {
        console.error('Failed to load product details:', err);
        setError(err.message || 'Product not found');
      } finally {
        setLoading(false);
      }
    }
    loadProduct();
  }, [id]);

  const isCompared = compareSet?.has(product?.id);

  const handleShare = () => {
    navigator.clipboard?.writeText(window.location.href);
    setCopied(true);
    setTimeout(() => setCopied(false), 2000);
  };

  if (loading) {
    return (
      <div className="min-h-screen bg-[#F8FAFC]">
        <Navbar compareCount={compareSet?.size || 0} />
        <div className="max-w-7xl mx-auto px-4 py-20 flex flex-col items-center justify-center">
          <div className="w-10 h-10 border-4 border-indigo-200 border-t-indigo-600 rounded-full animate-spin mb-4" />
          <p className="text-sm font-semibold text-slate-600">Retrieving catalog specifications...</p>
        </div>
      </div>
    );
  }

  if (error || !product) {
    return (
      <div className="min-h-screen bg-[#F8FAFC]">
        <Navbar compareCount={compareSet?.size || 0} />
        <div className="max-w-2xl mx-auto px-4 py-20 text-center">
          <div className="w-16 h-16 rounded-2xl bg-rose-50 text-rose-500 flex items-center justify-center mx-auto mb-4">
            <Info className="w-8 h-8" />
          </div>
          <h2 className="text-xl font-bold text-slate-800">Product Not Found</h2>
          <p className="text-sm text-slate-500 mt-2 mb-6">
            We couldn't locate product ID "{id}" across our active catalogs.
          </p>
          <Link
            to="/dashboard"
            className="inline-flex items-center gap-2 px-5 py-2.5 rounded-xl ai-gradient-bg text-white font-semibold text-xs shadow-md"
          >
            <ArrowLeft className="w-4 h-4" />
            <span>Back to Dashboard</span>
          </Link>
        </div>
      </div>
    );
  }

  const formattedPrice = new Intl.NumberFormat('en-IN', {
    style: 'currency',
    currency: 'INR',
    maximumFractionDigits: 0,
  }).format(product.price);

  const isInStock = product.availability?.toLowerCase().includes('in stock') || product.availability === 'Available';

  return (
    <div className="min-h-screen bg-[#F8FAFC] pb-24">
      
      <Navbar compareCount={compareSet?.size || 0} />

      <main className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 pt-6 space-y-8">
        
        {/* Breadcrumb Navigation */}
        <div className="flex items-center justify-between text-xs text-slate-500">
          <div className="flex items-center gap-2">
            <Link to="/dashboard" className="hover:text-indigo-600 flex items-center gap-1 font-medium transition-colors">
              <ArrowLeft className="w-3.5 h-3.5" />
              <span>Products</span>
            </Link>
            <span>/</span>
            <span className="font-medium text-slate-600">{product.category}</span>
            <span>/</span>
            <span className="font-bold text-slate-800 truncate max-w-[200px]">{product.brand}</span>
          </div>

          <button
            onClick={handleShare}
            className="flex items-center gap-1 px-3 py-1.5 rounded-xl bg-white border border-slate-200 text-slate-600 hover:bg-slate-50 text-xs font-semibold shadow-2xs transition-colors"
          >
            <Share2 className="w-3.5 h-3.5" />
            <span>{copied ? 'Link Copied!' : 'Share'}</span>
          </button>
        </div>

        {/* Product Showcase Hero */}
        <div className="bg-white rounded-3xl border border-slate-200/90 shadow-sm p-6 sm:p-10 grid grid-cols-1 lg:grid-cols-12 gap-10">
          
          {/* Left Column: Image with Glass Badge */}
          <div className="lg:col-span-6 space-y-4">
            <div className="relative aspect-4/3 w-full rounded-2xl bg-slate-50 border border-slate-100 overflow-hidden shadow-inner flex items-center justify-center">
              <img
                src={product.image_url || 'https://images.unsplash.com/photo-1523275335684-37898b6baf30?auto=format&fit=crop&w=800&q=80'}
                alt={product.title}
                className="w-full h-full object-cover"
                onError={(e) => {
                  e.target.src = 'https://images.unsplash.com/photo-1526170375885-4d8ecf77b99f?auto=format&fit=crop&w=800&q=80';
                }}
              />
              <div className="absolute top-4 left-4 flex gap-2">
                <span className={`px-3 py-1 text-xs font-bold rounded-lg uppercase tracking-wider backdrop-blur-md shadow-xs ${
                  isInStock 
                    ? 'bg-emerald-500/90 text-white' 
                    : 'bg-amber-500/90 text-white'
                }`}>
                  {product.availability || 'In Stock'}
                </span>
                <span className="px-3 py-1 text-xs font-bold rounded-lg bg-indigo-600/90 text-white backdrop-blur-md shadow-xs flex items-center gap-1">
                  <Sparkles className="w-3.5 h-3.5 text-amber-300" />
                  <span>Verified Spec</span>
                </span>
              </div>
            </div>

            {/* Trust Highlights */}
            <div className="grid grid-cols-3 gap-3 pt-2 text-center text-slate-600">
              <div className="p-3 bg-slate-50 rounded-2xl border border-slate-100">
                <Truck className="w-5 h-5 mx-auto text-indigo-600 mb-1" />
                <p className="text-[11px] font-bold text-slate-800">
                  {product.specs?.delivery_days ? `${product.specs.delivery_days} Days Delivery` : 'Fast Delivery'}
                </p>
                <p className="text-[10px] text-slate-400">Direct from seller</p>
              </div>

              <div className="p-3 bg-slate-50 rounded-2xl border border-slate-100">
                <ShieldCheck className="w-5 h-5 mx-auto text-emerald-600 mb-1" />
                <p className="text-[11px] font-bold text-slate-800">
                  {product.specs?.warranty_months ? `${product.specs.warranty_months} Mos. Warranty` : 'Standard Warranty'}
                </p>
                <p className="text-[10px] text-slate-400">Genuine guarantee</p>
              </div>

              <div className="p-3 bg-slate-50 rounded-2xl border border-slate-100">
                <RotateCcw className="w-5 h-5 mx-auto text-purple-600 mb-1" />
                <p className="text-[11px] font-bold text-slate-800">
                  {product.specs?.return_policy_days ? `${product.specs.return_policy_days} Days Return` : 'Easy Returns'}
                </p>
                <p className="text-[10px] text-slate-400">No hassle policy</p>
              </div>
            </div>
          </div>

          {/* Right Column: Key Details & Purchasing Actions */}
          <div className="lg:col-span-6 flex flex-col justify-between space-y-6">
            
            <div className="space-y-3">
              <div className="flex items-center gap-2">
                <span className="text-xs font-black uppercase tracking-wider text-indigo-600 bg-indigo-50 px-2.5 py-1 rounded-full">
                  {product.brand}
                </span>
                <span className="text-xs font-semibold text-slate-400">
                  Category: {product.category}
                </span>
              </div>

              <h1 className="text-2xl sm:text-3xl font-black text-slate-900 tracking-tight leading-snug">
                {product.title}
              </h1>

              {/* Rating and Reviews */}
              <div className="flex items-center gap-3 pt-1">
                <div className="flex items-center gap-1.5 bg-amber-50 border border-amber-200/80 px-3 py-1 rounded-xl text-amber-700 font-bold text-xs">
                  <Star className="w-4 h-4 fill-amber-400 text-amber-400" />
                  <span>{product.rating || '4.8'} out of 5.0</span>
                </div>
                {product.specs?.review_count && (
                  <span className="text-xs font-semibold text-slate-500">
                    ({product.specs.review_count} ratings)
                  </span>
                )}
                {product.specs?.units_sold && (
                  <span className="text-xs text-emerald-600 font-semibold bg-emerald-50 px-2 py-0.5 rounded-md">
                    {product.specs.units_sold}+ bought recently
                  </span>
                )}
              </div>

              {/* Price Banner */}
              <div className="py-4 border-y border-slate-100 flex items-baseline gap-3">
                <span className="text-3xl sm:text-4xl font-black text-slate-900 tracking-tight">
                  {formattedPrice}
                </span>
                <span className="text-xs text-slate-500 font-medium">Inclusive of all taxes</span>
              </div>

              {/* Description */}
              <div className="space-y-1.5">
                <h3 className="text-xs font-bold uppercase tracking-wider text-slate-400">
                  Overview
                </h3>
                <p className="text-sm text-slate-600 leading-relaxed">
                  The {product.brand} {product.title} offers top-tier engineering in the {product.category} space. Crafted for users requiring high performance, balanced specifications, and solid reliability verified directly from official marketplace catalog benchmarks.
                </p>
              </div>

              {/* Quick Spec Highlights */}
              <div className="pt-2">
                <h3 className="text-xs font-bold uppercase tracking-wider text-slate-400 mb-2">
                  Key Specifications
                </h3>
                <div className="grid grid-cols-2 gap-2">
                  {Object.entries(product.specs || {}).slice(0, 6).map(([key, val]) => (
                    <div key={key} className="p-2.5 bg-slate-50 rounded-xl border border-slate-100 text-xs">
                      <span className="text-slate-400 block capitalize">{key.replace(/_/g, ' ')}</span>
                      <span className="font-bold text-slate-800 mt-0.5 block">{String(val)}</span>
                    </div>
                  ))}
                </div>
              </div>

            </div>

            {/* Action Buttons */}
            <div className="pt-4 border-t border-slate-100 flex flex-col sm:flex-row items-center gap-3">
              <button
                type="button"
                onClick={() => onToggleCompare && onToggleCompare(product)}
                className={`w-full sm:flex-1 py-3.5 px-5 rounded-2xl font-bold text-sm flex items-center justify-center gap-2 transition-all shadow-md ${
                  isCompared
                    ? 'bg-pink-600 text-white ring-4 ring-pink-500/20'
                    : 'bg-indigo-600 hover:bg-indigo-700 text-white shadow-indigo-500/20'
                }`}
              >
                {isCompared ? (
                  <>
                    <Check className="w-4 h-4" />
                    <span>Added to Compare Tray</span>
                  </>
                ) : (
                  <>
                    <Scale className="w-4 h-4" />
                    <span>Add to Compare</span>
                  </>
                )}
              </button>

              <Link
                to="/compare"
                className="w-full sm:w-auto py-3.5 px-6 rounded-2xl bg-slate-900 hover:bg-slate-800 text-white font-bold text-sm flex items-center justify-center gap-2 transition-colors shadow-xs"
              >
                <Scale className="w-4 h-4" />
                <span>Go to Comparison ({compareSet?.size || 0})</span>
              </Link>
            </div>

          </div>

        </div>

        {/* Detailed Specs Table */}
        <div className="bg-white rounded-3xl border border-slate-200/90 shadow-sm p-6 sm:p-8">
          <div className="flex items-center gap-3 pb-4 border-b border-slate-100">
            <div className="w-8 h-8 rounded-xl bg-indigo-50 text-indigo-600 flex items-center justify-center font-bold">
              <Info className="w-4 h-4" />
            </div>
            <div>
              <h2 className="text-lg font-bold text-slate-900">Comprehensive Technical Specifications</h2>
              <p className="text-xs text-slate-500">Official product specifications & verified customer ratings</p>
            </div>
          </div>

          <div className="mt-6 grid grid-cols-1 md:grid-cols-2 gap-x-8 gap-y-3">
            {Object.entries(product.specs || {}).map(([key, val]) => (
              <div key={key} className="flex items-center justify-between py-2.5 border-b border-slate-100 text-xs sm:text-sm">
                <span className="font-semibold text-slate-500 capitalize">{key.replace(/_/g, ' ')}</span>
                <span className="font-bold text-slate-800">{String(val)}</span>
              </div>
            ))}
          </div>
        </div>

      </main>

      <ChatWidget
        activeCategory={product.category}
        onToggleCompare={onToggleCompare}
        compareSet={compareSet}
      />

    </div>
  );
}
