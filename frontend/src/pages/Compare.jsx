import React, { useState, useEffect } from 'react';
import { Link } from 'react-router-dom';
import { 
  Scale, 
  ArrowLeft, 
  Sparkles, 
  Plus, 
  Trash2, 
  Check, 
  AlertTriangle 
} from 'lucide-react';
import Navbar from '../components/Navbar';
import ComparisonTable from '../components/ComparisonTable';
import ChatWidget from '../components/ChatWidget';
import api from '../services/api';

export default function Compare({ compareSet, setCompareSet, onToggleCompare }) {
  const [comparisonResult, setComparisonResult] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);

  const productList = Array.from(compareSet?.values() || []);

  // When comparison items change, call backend /api/compare if at least 2 items
  useEffect(() => {
    async function fetchComparisonData() {
      if (productList.length < 2) {
        setComparisonResult(null);
        return;
      }

      setLoading(true);
      setError(null);
      try {
        const productIds = productList.map(p => p.id);
        const category = productList[0].category || 'Electronics';
        const data = await api.compareProducts(productIds, category);
        setComparisonResult(data);
      } catch (err) {
        console.warn('Backend compare endpoint warning:', err);
        // Table will still render based on productList
      } finally {
        setLoading(false);
      }
    }

    fetchComparisonData();
  }, [compareSet]);

  const handleRemoveProduct = (productId) => {
    setCompareSet((prev) => {
      const next = new Map(prev);
      next.delete(productId);
      return next;
    });
  };

  const handleClearAll = () => {
    setCompareSet(new Map());
  };

  return (
    <div className="min-h-screen bg-[#F8FAFC] pb-24">
      
      <Navbar compareCount={compareSet?.size || 0} />

      <main className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 pt-8 space-y-8">
        
        {/* Page Header */}
        <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4">
          <div>
            <div className="flex items-center gap-2 mb-1">
              <Link 
                to="/dashboard" 
                className="text-xs font-semibold text-slate-500 hover:text-indigo-600 flex items-center gap-1 transition-colors"
              >
                <ArrowLeft className="w-3.5 h-3.5" />
                <span>Back to Dashboard</span>
              </Link>
            </div>
            <div className="flex items-center gap-3">
              <div className="w-10 h-10 rounded-2xl ai-gradient-bg text-white flex items-center justify-center shadow-md shadow-indigo-500/20">
                <Scale className="w-5 h-5" />
              </div>
              <div>
                <h1 className="text-2xl sm:text-3xl font-black text-slate-900 tracking-tight">
                  Product Comparison Matrix
                </h1>
                <p className="text-xs text-slate-500">
                  Grounded comparison table with side-by-side specifications and verified catalog parameters.
                </p>
              </div>
            </div>
          </div>

          {productList.length > 0 && (
            <div className="flex items-center gap-2">
              <button
                onClick={handleClearAll}
                className="px-3.5 py-2 rounded-xl bg-white border border-slate-200 hover:bg-rose-50 hover:text-rose-600 text-xs font-semibold text-slate-600 transition-colors flex items-center gap-1.5 shadow-2xs"
              >
                <Trash2 className="w-3.5 h-3.5" />
                <span>Clear All ({productList.length})</span>
              </button>
              <Link
                to="/dashboard"
                className="px-4 py-2 rounded-xl ai-gradient-bg text-white text-xs font-bold shadow-md hover:shadow-indigo-500/30 transition-all flex items-center gap-1.5"
              >
                <Plus className="w-4 h-4" />
                <span>Add More Products</span>
              </Link>
            </div>
          )}
        </div>

        {/* Loading Indicator */}
        {loading && (
          <div className="bg-indigo-50 border border-indigo-100 p-4 rounded-2xl flex items-center gap-3 text-indigo-700 text-xs font-semibold animate-pulse">
            <Sparkles className="w-4 h-4 animate-spin text-indigo-600" />
            <span>Aligning spec matrices across candidate catalogs...</span>
          </div>
        )}

        {/* Comparison Table Component */}
        <ComparisonTable
          products={productList}
          comparisonData={comparisonResult}
          onRemoveProduct={handleRemoveProduct}
          onClearAll={handleClearAll}
        />

      </main>

      <ChatWidget
        activeCategory={productList[0]?.category || 'Electronics'}
        onToggleCompare={onToggleCompare}
        compareSet={compareSet}
      />

    </div>
  );
}
