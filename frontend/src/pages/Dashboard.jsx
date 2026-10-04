import React, { useState, useEffect } from 'react';
import { useSearchParams, Link } from 'react-router-dom';
import { 
  Sparkles, 
  Flame, 
  ArrowRight, 
  SlidersHorizontal, 
  TrendingUp, 
  CheckCircle,
  Scale,
  RefreshCw,
  ShoppingBag,
  Zap,
  Tag
} from 'lucide-react';
import Navbar from '../components/Navbar';
import CategoryCard from '../components/CategoryCard';
import ProductCard from '../components/ProductCard';
import ChatWidget from '../components/ChatWidget';
import api from '../services/api';
import { getCategoryBudgetRule, CATEGORY_BUDGET_RULES } from '../config/categoryBudgetRules';

export default function Dashboard({ compareSet, setCompareSet, onToggleCompare }) {
  const [searchParams, setSearchParams] = useSearchParams();
  const queryParam = searchParams.get('q') || '';
  
  const [activeCategory, setActiveCategory] = useState('Beauty');
  const [categories, setCategories] = useState([]);
  const [trendingProducts, setTrendingProducts] = useState([]);
  const [recommendedProducts, setRecommendedProducts] = useState([]);
  const [searchResults, setSearchResults] = useState(null);
  const [loading, setLoading] = useState(true);
  const [isSearching, setIsSearching] = useState(false);
  const [activeBudgetFilter, setActiveBudgetFilter] = useState(null);

  const [authRequiredQuery, setAuthRequiredQuery] = useState(null);

  const currentUser = api.getCurrentUser();
  const currentBudgetRule = getCategoryBudgetRule(activeCategory);

  // Helper to ensure strict category filtering
  const isCategoryMatch = (p, cat) => {
    if (!cat || cat.toLowerCase() === 'all' || cat.toLowerCase() === 'general') return true;
    const pCat = (p.category || '').toLowerCase().trim();
    const pSub = (p.subcategory || '').toLowerCase().trim();
    const target = cat.toLowerCase().trim();
    if (pCat === target) return true;
    if (pCat.replace('&', 'and').replace(/\s+/g, '_') === target.replace('&', 'and').replace(/\s+/g, '_')) return true;
    if (pSub === target || target.includes(pSub) || pSub.includes(target)) return true;
    return false;
  };

  // Load initial categories
  useEffect(() => {
    async function loadCategories() {
      try {
        const cats = await api.getCategories();
        setCategories(cats);
      } catch (err) {
        console.error('Error loading categories:', err);
      }
    }
    loadCategories();
  }, []);

  // Update trending and recommended products whenever activeCategory changes
  useEffect(() => {
    async function updateCategoryData() {
      setLoading(true);
      setActiveBudgetFilter(null);
      try {
        const [trending, recommended] = await Promise.all([
          api.getTrendingProducts(activeCategory, 8),
          api.getRecommendedProducts(activeCategory, 12),
        ]);
        
        // Strict category filter before setting state
        const strictlyFilteredTrending = trending.filter(p => isCategoryMatch(p, activeCategory));
        const strictlyFilteredRecommended = recommended.filter(p => isCategoryMatch(p, activeCategory));
        
        setTrendingProducts(strictlyFilteredTrending);
        setRecommendedProducts(strictlyFilteredRecommended);
      } catch (err) {
        console.error('Error updating category products:', err);
      } finally {
        setLoading(false);
      }
    }
    updateCategoryData();
  }, [activeCategory]);

  // Handle URL query search
  useEffect(() => {
    if (queryParam) {
      handleSearchSubmit(queryParam);
    } else {
      setSearchResults(null);
      setAuthRequiredQuery(null);
    }
  }, [queryParam]);

  const handleSearchSubmit = async (queryText) => {
    const token = localStorage.getItem('shopai_token');
    const user = api.getCurrentUser();
    
    if (!token || !user || !user.id) {
      setAuthRequiredQuery(queryText);
      setSearchResults(null);
      return;
    }

    setAuthRequiredQuery(null);
    setIsSearching(true);
    try {
      const res = await api.searchProducts(queryText, activeCategory);
      setSearchResults({
        query: queryText,
        slots: res.slots,
        products: res.products || [],
      });
      // Scroll to results
      window.scrollTo({ top: 400, behavior: 'smooth' });
    } catch (err) {
      console.error('Search failed:', err);
      if (err.message?.toLowerCase().includes('session') || err.message?.toLowerCase().includes('auth') || err.message?.toLowerCase().includes('token')) {
        setAuthRequiredQuery(queryText);
        setSearchResults(null);
      }
    } finally {
      setIsSearching(false);
    }
  };

  const handleClearSearch = () => {
    setSearchResults(null);
    setAuthRequiredQuery(null);
    setSearchParams({});
  };

  return (
    <div className="min-h-screen bg-[#F8FAFC] pb-24">
      
      {/* Top Navbar */}
      <Navbar
        compareCount={compareSet?.size || 0}
        onSearchSubmit={handleSearchSubmit}
        activeCategory={activeCategory}
        onCategoryChange={setActiveCategory}
      />

      {/* Main Container */}
      <main className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 pt-8 space-y-12">
        
        {/* HERO SECTION */}
        <section className="relative rounded-3xl overflow-hidden shadow-2xl shadow-indigo-500/10 border border-indigo-100/80 bg-white">
          {/* Subtle Ambient Gradient Mesh Background */}
          <div className="absolute top-0 right-0 w-full lg:w-2/3 h-full bg-gradient-to-bl from-indigo-100/50 via-purple-50/40 to-transparent pointer-events-none" />
          <div className="absolute -bottom-24 -left-24 w-72 h-72 bg-pink-100/40 rounded-full blur-3xl pointer-events-none" />
          
          <div className="relative z-10 px-6 py-10 sm:px-12 sm:py-16 flex flex-col lg:flex-row items-center justify-between gap-10">
            <div className="max-w-2xl space-y-5 text-center lg:text-left">
              
              <div className="inline-flex items-center gap-2 px-3.5 py-1.5 rounded-full bg-gradient-to-r from-indigo-50/90 via-purple-50/80 to-pink-50/90 border border-indigo-200/70 text-indigo-800 text-xs font-bold shadow-xs">
                <Sparkles className="w-3.5 h-3.5 text-indigo-600 animate-pulse" />
                <span>AI Shopping Assistant · Find the Best Products & Deals</span>
              </div>

              <h1 className="text-3xl sm:text-5xl font-black text-slate-900 tracking-tight leading-tight">
                Ask for what you <br className="hidden sm:inline" />
                <span className="ai-gradient-text">actually want to buy.</span>
              </h1>

              <p className="text-sm sm:text-base text-slate-600 leading-relaxed max-w-xl">
                Welcome back, <strong className="text-slate-900">{currentUser?.name || 'Shopper'}</strong>! Simply speak in plain words—state your budget, preferences, or dealbreakers. ShopAI filters, scores, and compares real products side-by-side.
              </p>

              {/* Hero Call-to-action buttons */}
              <div className="pt-2 flex flex-wrap items-center justify-center lg:justify-start gap-3">
                <button
                  type="button"
                  onClick={() => handleSearchSubmit(currentBudgetRule?.heroQuery || `Best ${activeCategory}`)}
                  className="px-6 py-3.5 rounded-2xl ai-gradient-bg text-white font-bold text-sm shadow-lg shadow-indigo-500/25 hover:shadow-indigo-500/40 hover:scale-[1.02] active:scale-[0.98] transition-all flex items-center gap-2 cursor-pointer"
                >
                  <Sparkles className="w-4 h-4 text-amber-200" />
                  <span>Try: "{currentBudgetRule?.heroPrompt || `Best in ${activeCategory}`}"</span>
                </button>

                <a
                  href="#categories"
                  className="px-5 py-3.5 rounded-2xl bg-slate-100 hover:bg-slate-200/90 text-slate-700 font-bold text-sm transition-all flex items-center gap-1.5"
                >
                  <span>Explore Categories</span>
                  <ArrowRight className="w-4 h-4 text-slate-500" />
                </a>
              </div>

              {/* Quick Inspiration Prompts */}
              <div className="pt-1 flex flex-wrap items-center justify-center lg:justify-start gap-2">
                <span className="text-xs font-semibold text-slate-400">Popular:</span>
                {[
                  { label: '🧴 Face Wash < ₹500', query: 'Best Face Wash under ₹500', cat: 'Beauty' },
                  { label: '💧 Moisturizer < ₹1k', query: 'Hydrating Moisturizer under ₹1,000', cat: 'Beauty' },
                  { label: '💻 Coding Laptop < ₹50k', query: 'Coding Laptop under ₹50,000', cat: 'Laptops' },
                  { label: '🎧 ANC Earbuds', query: 'Wireless Earbuds with ANC', cat: 'Audio' },
                ].map((item, idx) => (
                  <button
                    key={idx}
                    type="button"
                    onClick={() => {
                      if (item.cat) setActiveCategory(item.cat);
                      handleSearchSubmit(item.query);
                    }}
                    className="px-3 py-1.5 rounded-xl bg-slate-50/80 hover:bg-indigo-50 border border-slate-200 hover:border-indigo-300 text-slate-600 hover:text-indigo-700 text-xs font-medium transition-all cursor-pointer shadow-2xs hover:scale-102"
                  >
                    {item.label}
                  </button>
                ))}
              </div>

            </div>

            {/* Hero AI Interactive Preview Card */}
            <div className="w-full lg:w-96 glass-panel rounded-3xl p-5 border border-indigo-100 shadow-xl shadow-indigo-500/5 relative overflow-hidden group">
              <div className="absolute top-0 right-0 w-32 h-32 bg-indigo-500/10 rounded-full blur-2xl pointer-events-none" />
              
              <div className="flex items-center justify-between pb-3 border-b border-slate-100/90 relative z-10">
                <div className="flex items-center gap-2.5">
                  <div className="w-8 h-8 rounded-xl ai-gradient-bg text-white flex items-center justify-center shadow-xs">
                    <Sparkles className="w-4 h-4" />
                  </div>
                  <div>
                    <h4 className="font-extrabold text-xs text-slate-900">Live AI Assistant</h4>
                    <span className="text-[10px] text-emerald-600 font-semibold flex items-center gap-1">
                      <span className="w-2 h-2 rounded-full bg-emerald-500 animate-pulse" />
                      Online & Ready
                    </span>
                  </div>
                </div>
                <span className="text-[10px] text-indigo-600 font-mono font-bold bg-indigo-50 px-2 py-0.5 rounded-md">ShopAI Pro</span>
              </div>

              <div className="mt-3.5 space-y-2.5 text-xs relative z-10">
                <div className="bg-slate-50/90 border border-slate-100 p-3 rounded-2xl text-slate-700">
                  <p className="font-bold text-slate-400 text-[10px] uppercase tracking-wider">Trending Inspiration</p>
                  <p className="mt-0.5 font-medium text-slate-800">"{currentBudgetRule?.prompts?.[0] || `Best ${activeCategory} with high rating`}"</p>
                </div>
                <div className="bg-indigo-50/70 border border-indigo-100/80 p-3 rounded-2xl text-indigo-950">
                  <p className="font-bold text-indigo-600 text-[10px] uppercase tracking-wider">Smart Concierge</p>
                  <p className="mt-0.5 text-slate-700">Personalized for <strong>{activeCategory}</strong>: Instant top picks ranked by value, verified reviews & your exact budget.</p>
                </div>
              </div>

              <div className="mt-4 pt-3 border-t border-slate-100 flex flex-col gap-2 relative z-10">
                <button
                  type="button"
                  onClick={() => handleSearchSubmit(currentBudgetRule?.heroQuery || `Best in ${activeCategory}`)}
                  className="w-full py-2.5 px-4 rounded-xl ai-gradient-bg text-white font-bold text-xs flex items-center justify-center gap-2 hover:opacity-95 shadow-md shadow-indigo-500/20 transition-all cursor-pointer"
                >
                  <Sparkles className="w-3.5 h-3.5" />
                  <span>Ask ShopAI in {activeCategory}</span>
                </button>
              </div>
            </div>

          </div>
        </section>

        {/* AUTHENTICATION REQUIRED GATING FOR AI ENGINE */}
        {authRequiredQuery && (
          <section className="relative rounded-3xl overflow-hidden shadow-2xl border border-indigo-500/30 bg-gradient-to-r from-slate-900 via-indigo-950 to-slate-900 text-white p-8 animate-in fade-in zoom-in-95 duration-200">
            <div className="absolute top-0 right-0 w-96 h-96 bg-indigo-500/10 rounded-full blur-3xl pointer-events-none" />
            <div className="relative z-10 max-w-2xl mx-auto text-center space-y-4">
              <div className="inline-flex items-center justify-center w-14 h-14 rounded-2xl ai-gradient-bg text-white shadow-lg shadow-indigo-500/30 mb-1">
                <Sparkles className="w-7 h-7 animate-pulse" />
              </div>
              <h3 className="text-2xl sm:text-3xl font-black tracking-tight">
                Sign In to Unlock <span className="ai-gradient-text">ShopAI Ranking Engine</span>
              </h3>
              <p className="text-slate-300 text-xs sm:text-sm max-w-lg mx-auto leading-relaxed">
                You searched for <strong className="text-white bg-slate-800 px-2 py-0.5 rounded">"{authRequiredQuery}"</strong>. Please sign in or create an account to activate weighted budget scoring, review analysis, and receive the top 2 ranked recommendations.
              </p>
              <div className="pt-3 flex flex-wrap items-center justify-center gap-3">
                <Link
                  to={`/login?from=${encodeURIComponent(`/dashboard?q=${authRequiredQuery}`)}`}
                  className="px-6 py-3 rounded-xl ai-gradient-bg text-white font-bold text-xs shadow-lg shadow-indigo-600/30 hover:shadow-indigo-600/50 hover:scale-102 transition-all flex items-center gap-2"
                >
                  <span>Sign In to Continue</span>
                  <ArrowRight className="w-4 h-4" />
                </Link>
                <Link
                  to="/register"
                  className="px-5 py-3 rounded-xl bg-slate-800 hover:bg-slate-700 text-slate-200 font-semibold text-xs border border-slate-700 hover:border-slate-600 transition-all"
                >
                  Create Free Account
                </Link>
                <button
                  type="button"
                  onClick={handleClearSearch}
                  className="px-4 py-3 rounded-xl text-xs text-slate-400 hover:text-slate-200 transition-colors"
                >
                  Dismiss
                </button>
              </div>
            </div>
          </section>
        )}

        {/* SEARCH RESULTS (IF ACTIVE) */}
        {searchResults && (
          <section className="space-y-4">
            <div className="flex items-center justify-between bg-white p-4 rounded-2xl border border-slate-200 shadow-xs">
              <div>
                <h2 className="text-lg font-bold text-slate-900 flex items-center gap-2">
                  <Sparkles className="w-4 h-4 text-indigo-600" />
                  <span>Top 2 Ranked Recommendations for "{searchResults.query}"</span>
                </h2>
                <div className="flex items-center gap-2 text-xs text-slate-500 mt-1">
                  <span>Intelligent Ranking · <strong>{searchResults.slots?.category || activeCategory}</strong></span>
                  {searchResults.slots?.budget_max && (
                    <span className="px-2 py-0.5 rounded-full bg-emerald-50 text-emerald-700 font-semibold">
                      Budget: ≤ ₹{Number(searchResults.slots.budget_max).toLocaleString('en-IN')}
                    </span>
                  )}
                </div>
              </div>

              <button
                onClick={handleClearSearch}
                className="px-3.5 py-1.5 rounded-xl bg-slate-100 hover:bg-slate-200 text-xs font-semibold text-slate-700 transition-colors cursor-pointer"
              >
                Clear Search Results
              </button>
            </div>

            {searchResults.products?.length === 0 ? (
              <div className="text-center py-12 bg-white rounded-2xl border border-slate-200">
                <p className="text-slate-500 text-sm">No products found matching your budget in {activeCategory}. Try adjusting your budget or query!</p>
              </div>
            ) : (
              <div className="grid grid-cols-1 md:grid-cols-2 gap-6 max-w-4xl mx-auto">
                {searchResults.products.slice(0, 2).map((p) => (
                  <ProductCard
                    key={p.id}
                    product={p}
                    isCompared={compareSet?.has(p.id)}
                    onToggleCompare={onToggleCompare}
                  />
                ))}
              </div>
            )}
          </section>
        )}

        {/* CATEGORY SECTION */}
        <section id="categories" className="space-y-4">
          <div className="flex items-center justify-between">
            <div>
              <h2 className="text-xl font-black text-slate-900 tracking-tight">
                Shop by Category
              </h2>
              <p className="text-xs text-slate-500">
                Select a category to update recommendations and search focus
              </p>
            </div>
            <span className="text-xs font-bold text-indigo-600 bg-indigo-50 px-3 py-1 rounded-full border border-indigo-100">
              Active Category: {activeCategory}
            </span>
          </div>

          <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-4">
            {categories.map((cat) => (
              <CategoryCard
                key={cat.id}
                category={cat}
                isActive={activeCategory.toLowerCase() === cat.name.toLowerCase()}
                onClick={(name) => {
                  setActiveCategory(name);
                  setActiveBudgetFilter(null);
                }}
              />
            ))}
          </div>
        </section>

        {/* TRENDING PRODUCTS (HORIZONTAL CARDS) */}
        {(() => {
          const displayedTrending = trendingProducts
            .filter(p => isCategoryMatch(p, activeCategory))
            .filter(p => activeBudgetFilter === null || p.price <= (activeBudgetFilter + 0.99));

          return (
            <section className="space-y-4">
              <div className="flex items-center justify-between">
                <div className="flex items-center gap-2">
                  <div className="w-7 h-7 rounded-lg bg-rose-100 text-rose-600 flex items-center justify-center">
                    <Flame className="w-4 h-4" />
                  </div>
                  <h2 className="text-xl font-black text-slate-900 tracking-tight">
                    Trending in {activeCategory}
                  </h2>
                </div>
                <span className="text-xs text-slate-400 font-medium">Scroll to explore →</span>
              </div>

              {displayedTrending.length === 0 ? (
                <div className="p-8 bg-white rounded-2xl border border-slate-200 text-center text-slate-500 text-sm">
                  No trending items found for {activeCategory} in this filter.
                </div>
              ) : (
                <div className="flex gap-5 overflow-x-auto pb-4 pt-1 no-scrollbar">
                  {displayedTrending.map((product) => (
                    <ProductCard
                      key={product.id}
                      product={product}
                      horizontal={true}
                      isCompared={compareSet?.has(product.id)}
                      onToggleCompare={onToggleCompare}
                    />
                  ))}
                </div>
              )}
            </section>
          );
        })()}

        {/* RECOMMENDED PRODUCTS (GRID LAYOUT WITH DYNAMIC BUDGET CHIPS) */}
        {(() => {
          const displayedRecommended = recommendedProducts
            .filter(p => isCategoryMatch(p, activeCategory))
            .filter(p => activeBudgetFilter === null || p.price <= (activeBudgetFilter + 0.99));

          return (
            <section className="space-y-4">
              <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-3">
                <div className="flex items-center gap-2">
                  <div className="w-7 h-7 rounded-lg bg-indigo-100 text-indigo-600 flex items-center justify-center">
                    <Sparkles className="w-4 h-4" />
                  </div>
                  <div>
                    <h2 className="text-xl font-black text-slate-900 tracking-tight">
                      Recommended for You
                    </h2>
                    <p className="text-xs text-slate-500">
                      Curated picks strictly in <strong>{activeCategory}</strong>
                    </p>
                  </div>
                </div>

                <div className="flex items-center gap-2">
                  <span className="text-xs font-semibold text-slate-500 bg-white px-2.5 py-1 rounded-full border border-slate-200">
                    {displayedRecommended.length} items
                  </span>
                </div>
              </div>

              {/* DYNAMIC CATEGORY-SPECIFIC BUDGET CHIPS */}
              {currentBudgetRule && (
                <div className="flex items-center gap-2 overflow-x-auto pb-1 pt-1 no-scrollbar">
                  <span className="text-xs font-semibold text-slate-500 flex items-center gap-1 shrink-0">
                    <Tag className="w-3.5 h-3.5 text-indigo-500" />
                    <span>Budget:</span>
                  </span>
                  <button
                    type="button"
                    onClick={() => setActiveBudgetFilter(null)}
                    className={`px-3 py-1 rounded-full text-xs font-bold transition-all shrink-0 cursor-pointer ${
                      activeBudgetFilter === null
                        ? 'bg-indigo-600 text-white shadow-xs'
                        : 'bg-white text-slate-600 border border-slate-200 hover:bg-slate-100'
                    }`}
                  >
                    All {activeCategory}
                  </button>
                  {currentBudgetRule.chips.map((val, idx) => {
                    const label = currentBudgetRule.labels[idx];
                    const isSelected = activeBudgetFilter === val;
                    return (
                      <button
                        key={val}
                        type="button"
                        onClick={() => setActiveBudgetFilter(isSelected ? null : val)}
                        className={`px-3 py-1 rounded-full text-xs font-bold transition-all shrink-0 cursor-pointer ${
                          isSelected
                            ? 'bg-indigo-600 text-white shadow-xs'
                            : 'bg-white text-slate-600 border border-slate-200 hover:bg-indigo-50 hover:text-indigo-600 hover:border-indigo-200'
                        }`}
                      >
                        {label}
                      </button>
                    );
                  })}
                </div>
              )}

              {displayedRecommended.length === 0 ? (
                <div className="text-center py-12 bg-white rounded-2xl border border-slate-200">
                  <p className="text-slate-500 text-sm">
                    No {activeCategory} products found under ₹{activeBudgetFilter?.toLocaleString('en-IN')}.
                  </p>
                  <button
                    type="button"
                    onClick={() => setActiveBudgetFilter(null)}
                    className="mt-3 px-4 py-1.5 rounded-xl bg-indigo-50 text-indigo-600 text-xs font-bold hover:bg-indigo-100 cursor-pointer"
                  >
                    Clear Budget Filter
                  </button>
                </div>
              ) : (
                <div className="grid grid-cols-1 sm:grid-cols-2 md:grid-cols-3 lg:grid-cols-4 gap-5">
                  {displayedRecommended.map((product) => (
                    <ProductCard
                      key={product.id}
                      product={product}
                      isCompared={compareSet?.has(product.id)}
                      onToggleCompare={onToggleCompare}
                    />
                  ))}
                </div>
              )}
            </section>
          );
        })()}

      </main>

      {/* Floating AI Shopping Assistant Chat Widget */}
      <ChatWidget
        activeCategory={activeCategory}
        onToggleCompare={onToggleCompare}
        compareSet={compareSet}
      />

    </div>
  );
}
