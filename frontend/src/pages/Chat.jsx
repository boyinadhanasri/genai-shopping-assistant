import React, { useState, useEffect, useRef } from 'react';
import { Link } from 'react-router-dom';
import { 
  Sparkles, 
  Send, 
  Bot, 
  User, 
  ArrowLeft, 
  Scale, 
  ExternalLink,
  RotateCcw,
  ShoppingBag,
  Cpu
} from 'lucide-react';
import Navbar from '../components/Navbar';
import api from '../services/api';

export default function Chat({ compareSet, onToggleCompare }) {
  const [messages, setMessages] = useState([
    {
      id: 'welcome',
      role: 'assistant',
      content: `Welcome to **ShopAI Conversational Assistant**! Describe any product you need, state your budget (e.g., "laptop under ₹50,000 for programming"), or specify features like long battery life.`,
      slots: null,
      products: [],
      timestamp: new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' }),
    }
  ]);
  const [inputValue, setInputValue] = useState('');
  const [category, setCategory] = useState('Electronics');
  const [isLoading, setIsLoading] = useState(false);
  const messagesEndRef = useRef(null);

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  };

  useEffect(() => {
    scrollToBottom();
  }, [messages, isLoading]);

  const handleSend = async (textToSend) => {
    const text = textToSend || inputValue.trim();
    if (!text || isLoading) return;

    const userMsg = {
      id: `user-${Date.now()}`,
      role: 'user',
      content: text,
      timestamp: new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' }),
    };

    setMessages(prev => [...prev, userMsg]);
    setInputValue('');
    setIsLoading(true);

    try {
      const history = messages.map(m => ({ role: m.role, content: m.content }));
      const response = await api.chatAssistant(text, category, history);
      
      if (response.slots?.category || response.extracted?.category) {
        setCategory(response.slots?.category || response.extracted?.category);
      }

      setMessages(prev => [
        ...prev,
        {
          id: `ai-${Date.now()}`,
          role: 'assistant',
          content: response.answer || response.reply || response.message,
          suggestion: response.suggestion || null,
          alternatives: response.alternatives || [],
          options: response.options || [],
          needs_clarification: response.needs_clarification || false,
          comparison: response.comparison || null,
          slots: response.slots,
          extracted: response.extracted || null,
          products: response.products || [],
          timestamp: new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' }),
        }
      ]);
    } catch (err) {
      console.error('Chat error:', err);
      // Fallback
      try {
        const queryRes = await api.searchProducts(text, category);
        setMessages(prev => [
          ...prev,
          {
            id: `ai-${Date.now()}`,
            role: 'assistant',
            content: `Here are candidate products matching your query:`,
            slots: queryRes.slots,
            products: queryRes.products || [],
            timestamp: new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' }),
          }
        ]);
      } catch (innerErr) {
        setMessages(prev => [
          ...prev,
          {
            id: `ai-${Date.now()}`,
            role: 'assistant',
            content: `I had trouble retrieving products. Please try again!`,
            products: [],
            timestamp: new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' }),
          }
        ]);
      }
    } finally {
      setIsLoading(false);
    }
  };

  const samplePrompts = [
    'Python books under ₹500',
    'Cookware fry pan under ₹1,000',
    'Cricket bat under ₹1,500',
    'Laptop under ₹50,000 for coding',
    'Camera phone under ₹20,000',
    'Running shoes under ₹2,000',
  ];

  return (
    <div className="min-h-screen bg-[#F8FAFC] flex flex-col">
      <Navbar compareCount={compareSet?.size || 0} />

      <div className="flex-1 max-w-5xl w-full mx-auto p-4 sm:p-6 flex flex-col">
        
        {/* Top Control Bar */}
        <div className="bg-white p-4 rounded-2xl border border-slate-200 shadow-xs flex items-center justify-between mb-4">
          <div className="flex items-center gap-3">
            <Link to="/dashboard" className="p-2 rounded-xl hover:bg-slate-100 text-slate-500 transition-colors">
              <ArrowLeft className="w-4 h-4" />
            </Link>
            <div>
              <h2 className="font-bold text-slate-900 text-sm">Full-Screen AI Shopping Chat</h2>
              <p className="text-[11px] text-slate-400">Powered by hybrid retrieval & composite ranking</p>
            </div>
          </div>

          <div className="flex items-center gap-2">
            <label className="text-xs text-slate-500 font-medium">Category:</label>
            <select
              value={category}
              onChange={(e) => setCategory(e.target.value)}
              className="text-xs font-bold text-slate-800 bg-slate-100 px-3 py-1.5 rounded-xl border-none outline-hidden"
            >
              <option value="Home & Kitchen">Home & Kitchen</option>
              <option value="Books">Books</option>
              <option value="Sports">Sports</option>
              <option value="Smartphones">Smartphones</option>
              <option value="Laptops">Laptops</option>
              <option value="Fashion">Fashion & Shoes</option>
              <option value="Beauty">Beauty</option>
              <option value="Audio">Audio</option>
              <option value="Toys">Toys & Games</option>
              <option value="Electronics">Electronics</option>
            </select>
          </div>
        </div>

        {/* Chat Thread */}
        <div className="flex-1 bg-white rounded-3xl border border-slate-200 shadow-xs p-4 sm:p-6 overflow-y-auto space-y-4 max-h-[68vh]">
          {messages.map((msg) => {
            const isUser = msg.role === 'user';
            return (
              <div key={msg.id} className={`flex gap-3 ${isUser ? 'justify-end' : 'justify-start'}`}>
                {!isUser && (
                  <div className="w-8 h-8 rounded-xl ai-gradient-bg text-white flex items-center justify-center shrink-0 shadow-xs">
                    <Sparkles className="w-4 h-4" />
                  </div>
                )}

                  <div className={`max-w-[85%] ${isUser ? 'items-end' : 'items-start'} flex flex-col`}>
                    <div
                      className={`p-4 rounded-2xl text-xs sm:text-sm leading-relaxed ${
                        isUser
                          ? 'bg-indigo-600 text-white rounded-tr-xs font-medium shadow-xs'
                          : 'bg-slate-50 border border-slate-200/80 text-slate-800 rounded-tl-xs'
                      }`}
                    >
                      <p className="whitespace-pre-wrap">{msg.content}</p>

                      {(msg.extracted || msg.slots) && (
                        <div className="mt-2.5 pt-2 border-t border-slate-200/60 flex flex-wrap gap-1 text-[11px]">
                          {(msg.extracted?.category || msg.slots?.category) && (
                            <span className="font-bold text-indigo-600">
                              Category: {msg.extracted?.category || msg.slots?.category}
                            </span>
                          )}
                          {(msg.extracted?.budget || msg.slots?.budget_max) && (
                            <span className="text-emerald-700 bg-emerald-100/60 px-1.5 py-0.5 rounded font-semibold">
                              Budget: ≤ ₹{Number(msg.extracted?.budget || msg.slots?.budget_max).toLocaleString('en-IN')}
                            </span>
                          )}
                          {(msg.extracted?.brand || msg.slots?.brand) && (
                            <span className="text-purple-700 bg-purple-100/60 px-1.5 py-0.5 rounded font-semibold">
                              Brand: {msg.extracted?.brand || msg.slots?.brand}
                            </span>
                          )}
                        </div>
                      )}

                      {/* Side-by-Side Comparison Box */}
                      {msg.comparison && (
                        <div className="mt-3 pt-2.5 border-t border-slate-200 w-full space-y-3">
                          <div className="flex items-center gap-1.5 text-xs font-bold text-indigo-700">
                            <Scale className="w-4 h-4 text-indigo-600" />
                            <span>Detailed Spec Comparison</span>
                          </div>

                          <div className="overflow-x-auto rounded-xl border border-slate-200 bg-white">
                            <table className="w-full text-xs text-left">
                              <thead>
                                <tr className="border-b border-slate-200 bg-slate-100/80 text-slate-700 font-bold">
                                  <th className="p-2.5">Feature</th>
                                  <th className="p-2.5 truncate max-w-[140px]">{msg.comparison.product_a?.title?.slice(0, 22)}...</th>
                                  <th className="p-2.5 truncate max-w-[140px]">{msg.comparison.product_b?.title?.slice(0, 22)}...</th>
                                </tr>
                              </thead>
                              <tbody className="divide-y divide-slate-200/60">
                                <tr>
                                  <td className="p-2.5 font-semibold text-slate-500">Price</td>
                                  <td className="p-2.5 font-extrabold text-slate-900">₹{Number(msg.comparison.product_a?.price || 0).toLocaleString('en-IN')}</td>
                                  <td className="p-2.5 font-extrabold text-slate-900">₹{Number(msg.comparison.product_b?.price || 0).toLocaleString('en-IN')}</td>
                                </tr>
                                {msg.comparison.feature_comparison && Object.entries(msg.comparison.feature_comparison).map(([dim, data]) => (
                                  <tr key={dim}>
                                    <td className="p-2.5 font-medium text-slate-500 capitalize">{dim}</td>
                                    <td className="p-2.5 text-slate-700">{data.a || '—'}</td>
                                    <td className="p-2.5 text-slate-700">{data.b || '—'}</td>
                                  </tr>
                                ))}
                              </tbody>
                            </table>
                          </div>

                          {/* Verdicts */}
                          {msg.comparison.verdicts && (
                            <div className="p-3 bg-indigo-50/90 rounded-xl border border-indigo-100 text-xs space-y-1.5">
                              <div className="font-bold text-indigo-900 flex items-center gap-1.5">
                                <Sparkles className="w-4 h-4 text-indigo-600" />
                                <span>Expert Buying Recommendations:</span>
                              </div>
                              {msg.comparison.verdicts.best_for_photography && (
                                <p className="text-slate-700">📷 <strong>Best for Photography:</strong> {msg.comparison.verdicts.best_for_photography}</p>
                              )}
                              {msg.comparison.verdicts.best_for_gaming && (
                                <p className="text-slate-700">🎮 <strong>Best for Gaming / Performance:</strong> {msg.comparison.verdicts.best_for_gaming}</p>
                              )}
                              {msg.comparison.verdicts.best_for_value && (
                                <p className="text-slate-700">💎 <strong>Best Value for Money:</strong> {msg.comparison.verdicts.best_for_value}</p>
                              )}
                            </div>
                          )}
                        </div>
                      )}
                    </div>

                    {/* Clarification options chips */}
                    {msg.options && msg.options.length > 0 && (
                      <div className="mt-3 pt-2.5 border-t border-slate-100 w-full">
                        <p className="text-[11px] font-semibold text-slate-600 mb-2 flex items-center gap-1.5">
                          <Sparkles className="w-3.5 h-3.5 text-indigo-600" />
                          <span>Quick Selection:</span>
                        </p>
                        <div className="flex flex-wrap gap-1.5">
                          {msg.options.map((opt, idx) => (
                            <button
                              key={idx}
                              type="button"
                              onClick={() => handleSend(opt)}
                              className="px-3.5 py-2 bg-indigo-50 hover:bg-indigo-600 text-indigo-700 hover:text-white rounded-xl text-xs font-semibold border border-indigo-200/80 shadow-2xs hover:shadow-md transition-all duration-200 cursor-pointer active:scale-95"
                            >
                              {opt} →
                            </button>
                          ))}
                        </div>
                      </div>
                    )}

                    {/* Alternatives suggestion chips */}
                    {msg.alternatives && msg.alternatives.length > 0 && (
                      <div className="mt-2.5 flex flex-wrap gap-1.5 w-full">
                        {msg.alternatives.map((alt, idx) => (
                          <button
                            key={idx}
                            type="button"
                            onClick={() => handleSend(alt)}
                            className="text-xs bg-white hover:bg-indigo-600 hover:text-white text-indigo-700 font-semibold px-3 py-1.5 rounded-full border border-indigo-200 transition-all shadow-2xs hover:border-indigo-300 cursor-pointer active:scale-95"
                          >
                            {alt} →
                          </button>
                        ))}
                      </div>
                    )}

                    {/* Embedded Top 2 product cards in chat */}
                    {msg.products && msg.products.length > 0 && (
                      <div className="mt-3 grid grid-cols-1 sm:grid-cols-2 gap-3.5 w-full">
                        {msg.products.slice(0, 2).map((p, pIdx) => {
                          const rankNum = p.rank || (pIdx === 0 ? 1 : 2);
                          const isTop = rankNum === 1;
                          const scoreVal = p.score || p.match_score;
                          const rankBadge = isTop ? '#1 TOP RECOMMENDATION' : '#2 RUNNER UP';

                          return (
                            <div 
                              key={p.id} 
                              className={`p-3.5 bg-white rounded-2xl border transition-all shadow-xs flex flex-col gap-2.5 ${
                                isTop 
                                  ? 'border-amber-300 ring-1 ring-amber-200/50 shadow-amber-500/5' 
                                  : 'border-indigo-200 shadow-indigo-500/5'
                              }`}
                            >
                              <div className="flex items-start gap-3">
                                <img
                                  src={p.image_url || 'https://images.unsplash.com/photo-1523275335684-37898b6baf30?auto=format&fit=crop&w=150&q=80'}
                                  alt={p.title}
                                  className="w-14 h-14 rounded-xl object-cover bg-slate-50 shrink-0 border border-slate-100"
                                />
                                <div className="min-w-0 flex-1">
                                  <div className="flex items-center gap-1.5 mb-1 flex-wrap">
                                    <span className={`text-[9px] font-black uppercase px-2 py-0.5 rounded-md flex items-center gap-1 ${
                                      isTop
                                        ? 'bg-amber-500 text-white'
                                        : 'bg-indigo-600 text-white'
                                    }`}>
                                      <span>{rankBadge}</span>
                                    </span>
                                    {scoreVal && (
                                      <span className="text-[9px] font-extrabold bg-slate-100 text-slate-800 px-1.5 py-0.5 rounded border border-slate-200">
                                        Score: {scoreVal}/100
                                      </span>
                                    )}
                                    <span className="text-[10px] font-bold uppercase text-indigo-600 bg-indigo-50 px-1.5 py-0.5 rounded">
                                      {p.brand}
                                    </span>
                                  </div>
                                  <h4 className="text-xs font-bold text-slate-800 line-clamp-1">{p.title}</h4>
                                  <div className="flex items-center gap-2 text-xs font-extrabold text-slate-900 mt-0.5">
                                    <span>₹{Number(p.price).toLocaleString('en-IN')}</span>
                                    {p.discount_percent && p.discount_percent > 0 && (
                                      <span className="text-[10px] text-rose-600 font-bold bg-rose-50 px-1 rounded">
                                        {p.discount_percent}% OFF
                                      </span>
                                    )}
                                    <span className="text-[10px] text-amber-500 font-semibold">★ {p.rating || '4.5'}</span>
                                  </div>
                                </div>
                                <div className="flex items-center gap-1">
                                  <button
                                    onClick={() => onToggleCompare && onToggleCompare(p)}
                                    className={`p-2 rounded-xl text-xs transition-colors cursor-pointer ${
                                      compareSet?.has(p.id) ? 'bg-pink-600 text-white' : 'bg-slate-100 text-slate-600 hover:bg-slate-200'
                                    }`}
                                    title="Compare"
                                  >
                                    <Scale className="w-3.5 h-3.5" />
                                  </button>
                                  <Link
                                    to={`/product/${p.id}`}
                                    className="p-2 rounded-xl bg-slate-900 hover:bg-indigo-600 text-white text-xs transition-colors cursor-pointer"
                                    title="View Details"
                                  >
                                    <ExternalLink className="w-3.5 h-3.5" />
                                  </Link>
                                </div>
                              </div>

                              {/* Why recommended bullets */}
                              {p.why_recommended && p.why_recommended.length > 0 && (
                                <div className="p-2.5 bg-slate-50 rounded-xl text-[10px] text-slate-800 space-y-0.5 border border-slate-200/80">
                                  <span className="font-bold text-indigo-900 flex items-center gap-1">
                                    <Sparkles className="w-3 h-3 text-indigo-600" />
                                    Why:
                                  </span>
                                  {p.why_recommended.slice(0, 4).map((reason, rIdx) => (
                                    <p key={rIdx} className="text-slate-700 font-medium">
                                      {reason.startsWith('✓') ? reason : `✓ ${reason}`}
                                    </p>
                                  ))}
                                </div>
                              )}
                            </div>
                          );
                        })}
                      </div>
                    )}

                    <span className="text-[10px] text-slate-400 mt-1 px-1">{msg.timestamp}</span>
                  </div>

                {isUser && (
                  <div className="w-8 h-8 rounded-xl bg-slate-200 text-slate-700 flex items-center justify-center shrink-0">
                    <User className="w-4 h-4" />
                  </div>
                )}
              </div>
            );
          })}

          {isLoading && (
            <div className="flex items-center gap-2 text-slate-500 text-xs pl-2">
              <Sparkles className="w-4 h-4 text-indigo-600 animate-spin" />
              <span>Analyzing constraints and ranking candidates...</span>
            </div>
          )}

          <div ref={messagesEndRef} />
        </div>

        {/* Quick Prompts */}
        <div className="flex items-center gap-2 my-2 overflow-x-auto no-scrollbar py-1">
          {samplePrompts.map((p, i) => (
            <button
              key={i}
              onClick={() => handleSend(p)}
              className="text-xs bg-slate-200/70 hover:bg-indigo-50 hover:text-indigo-600 text-slate-700 px-3 py-1.5 rounded-xl font-medium whitespace-nowrap transition-colors"
            >
              {p}
            </button>
          ))}
        </div>

        {/* Composer Form */}
        <form
          onSubmit={(e) => {
            e.preventDefault();
            handleSend();
          }}
          className="flex items-center gap-2 bg-white p-2 rounded-2xl border border-slate-200 shadow-sm"
        >
          <input
            type="text"
            value={inputValue}
            onChange={(e) => setInputValue(e.target.value)}
            placeholder="Type your shopping request (e.g., 'wireless mouse under ₹1,500')..."
            className="flex-1 px-4 py-2.5 text-sm bg-transparent outline-hidden text-slate-800 placeholder-slate-400"
          />
          <button
            type="submit"
            disabled={!inputValue.trim() || isLoading}
            className="px-5 py-2.5 rounded-xl ai-gradient-bg text-white font-bold text-xs flex items-center gap-1.5 shadow-md disabled:opacity-40"
          >
            <span>Send</span>
            <Send className="w-3.5 h-3.5" />
          </button>
        </form>

      </div>
    </div>
  );
}
