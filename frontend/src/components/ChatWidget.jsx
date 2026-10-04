import React, { useState, useEffect, useRef } from 'react';
import { 
  Sparkles, 
  Send, 
  X, 
  Bot, 
  User, 
  Scale, 
  ExternalLink, 
  RotateCcw,
  Minimize2,
  Maximize2,
  ChevronDown,
  ArrowRight
} from 'lucide-react';
import api from '../services/api';
import { Link } from 'react-router-dom';
import { getCategoryBudgetRule } from '../config/categoryBudgetRules';

export default function ChatWidget({ 
  activeCategory = 'Electronics', 
  onToggleCompare, 
  compareSet = new Set(),
  isOpenDefault = false 
}) {
  const [isOpen, setIsOpen] = useState(isOpenDefault);
  const [messages, setMessages] = useState([
    {
      id: 'msg-welcome',
      role: 'assistant',
      content: `Hello! I'm **ShopAI**, your personal shopping assistant. Tell me what you're looking for, your budget, or compare two products!`,
      slots: null,
      products: [],
      timestamp: new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' }),
    }
  ]);
  const [inputValue, setInputValue] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const [selectedCategory, setSelectedCategory] = useState(activeCategory);
  const messagesEndRef = useRef(null);
  const inputRef = useRef(null);

  // Sync category if parent changes
  useEffect(() => {
    if (activeCategory) {
      setSelectedCategory(activeCategory);
    }
  }, [activeCategory]);

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  };

  useEffect(() => {
    if (isOpen) {
      scrollToBottom();
      inputRef.current?.focus();
    }
  }, [isOpen, messages, isLoading]);

  const handleSendMessage = async (textToSend) => {
    const text = textToSend || inputValue.trim();
    if (!text || isLoading) return;

    const token = localStorage.getItem('shopai_token');
    const user = api.getCurrentUser();

    if (!token || !user || !user.id) {
      const userMessageId = `user-${Date.now()}`;
      const newUserMsg = {
        id: userMessageId,
        role: 'user',
        content: text,
        timestamp: new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' }),
      };
      const authRequiredMsg = {
        id: `ai-${Date.now()}`,
        role: 'assistant',
        content: '🔒 **Sign in required**\n\nPlease log in to chat with ShopAI Assistant and receive real-time personalized recommendations.',
        isAuthPrompt: true,
        timestamp: new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' }),
      };
      setMessages((prev) => [...prev, newUserMsg, authRequiredMsg]);
      setInputValue('');
      return;
    }

    const userMessageId = `user-${Date.now()}`;
    const newUserMsg = {
      id: userMessageId,
      role: 'user',
      content: text,
      timestamp: new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' }),
    };

    setMessages((prev) => [...prev, newUserMsg]);
    setInputValue('');
    setIsLoading(true);

    try {
      // Connect to backend /api/chat or /api/query
      const historyPayload = messages.map(m => ({ role: m.role, content: m.content }));
      const response = await api.chatAssistant(text, selectedCategory || null, historyPayload);

      if (response.slots?.category || response.extracted?.category) {
        setSelectedCategory(response.slots?.category || response.extracted?.category);
      }

      const assistantMsg = {
        id: `ai-${Date.now()}`,
        role: 'assistant',
        content: response.message || response.answer || response.reply,
        suggestion: response.suggestion || null,
        alternatives: response.alternatives || [],
        needs_clarification: response.needs_clarification || false,
        options: response.options || [],
        comparison: response.comparison || null,
        slots: response.slots,
        extracted: response.extracted || null,
        products: response.products || [],
        suggestedQueries: response.suggested_queries || [],
        timestamp: new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' }),
      };

      setMessages((prev) => [...prev, assistantMsg]);
    } catch (err) {
      console.error('Chat error:', err);
      // Fallback response with live catalog query
      try {
        const queryRes = await api.searchProducts(text, selectedCategory);
        const assistantMsg = {
          id: `ai-${Date.now()}`,
          role: 'assistant',
          content: `Here are the top matches in **${queryRes.slots?.category || selectedCategory}** for "${text}":`,
          slots: queryRes.slots,
          products: queryRes.products || [],
          timestamp: new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' }),
        };
        setMessages((prev) => [...prev, assistantMsg]);
      } catch (innerErr) {
        setMessages((prev) => [
          ...prev,
          {
            id: `ai-${Date.now()}`,
            role: 'assistant',
            content: `I'm having a slight trouble reaching the catalog service right now. Please try again or rephrase your request!`,
            products: [],
            timestamp: new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' }),
          }
        ]);
      }
    } finally {
      setIsLoading(false);
    }
  };

  const handleClearHistory = () => {
    setMessages([
      {
        id: 'msg-welcome-reset',
        role: 'assistant',
        content: `Conversation reset. How can I help you shop today?`,
        slots: null,
        products: [],
        timestamp: new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' }),
      }
    ]);
  };

  const categoryRule = getCategoryBudgetRule(selectedCategory);
  const quickPrompts = categoryRule?.prompts || [
    `Top rated in ${selectedCategory || 'store'}`,
    `Compare top products`,
    `Budget recommendations`,
  ];

  return (
    <>
      {/* Floating Trigger Launcher */}
      {!isOpen && (
        <button
          onClick={() => setIsOpen(true)}
          className="fixed bottom-6 right-6 z-50 flex items-center gap-2.5 px-4 py-3 rounded-full ai-gradient-bg text-white font-bold text-sm shadow-2xl hover:shadow-indigo-500/50 hover:scale-105 active:scale-95 transition-all group"
          aria-label="Open AI Shopping Assistant"
        >
          <div className="relative">
            <Sparkles className="w-5 h-5 animate-pulse" />
            <span className="absolute -top-1 -right-1 w-2.5 h-2.5 bg-emerald-400 rounded-full ring-2 ring-indigo-600 animate-ping" />
          </div>
          <span>Ask ShopAI</span>
          <span className="text-[11px] bg-white/20 px-2 py-0.5 rounded-full font-semibold">
            Chat
          </span>
        </button>
      )}

      {/* Expanded Floating Chat Panel */}
      {isOpen && (
        <div className="fixed bottom-6 right-6 z-50 w-full sm:w-[440px] h-[640px] max-h-[85vh] flex flex-col bg-white rounded-3xl border border-slate-200/90 shadow-2xl shadow-indigo-900/15 overflow-hidden animate-in fade-in slide-in-from-bottom-5 duration-200">
          
          {/* Header */}
          <div className="p-4 ai-gradient-bg text-white flex items-center justify-between shrink-0 shadow-xs">
            <div className="flex items-center gap-3">
              <div className="w-9 h-9 rounded-xl bg-white/15 backdrop-blur-md flex items-center justify-center ring-1 ring-white/30">
                <Bot className="w-5 h-5 text-white" />
              </div>
              <div>
                <div className="flex items-center gap-1.5">
                  <h3 className="font-extrabold text-sm tracking-tight">ShopAI Assistant</h3>
                  <span className="text-[9px] font-bold px-1.5 py-0.5 rounded bg-white/25 uppercase tracking-wider">
                    Online
                  </span>
                </div>
                <p className="text-[11px] text-indigo-100 flex items-center gap-1">
                  <span>Category:</span>
                  <select
                    value={selectedCategory || ''}
                    onChange={(e) => setSelectedCategory(e.target.value)}
                    className="bg-transparent text-white font-semibold underline cursor-pointer outline-hidden text-[11px]"
                  >
                    <option value="" className="text-slate-800">Auto (Smart AI Detect)</option>
                    <option value="Home & Kitchen" className="text-slate-800">Home & Kitchen</option>
                    <option value="Books" className="text-slate-800">Books</option>
                    <option value="Sports" className="text-slate-800">Sports</option>
                    <option value="Smartphones" className="text-slate-800">Smartphones</option>
                    <option value="Laptops" className="text-slate-800">Laptops</option>
                    <option value="Fashion" className="text-slate-800">Fashion & Shoes</option>
                    <option value="Beauty" className="text-slate-800">Beauty</option>
                    <option value="Audio" className="text-slate-800">Audio</option>
                    <option value="Toys" className="text-slate-800">Toys & Games</option>
                    <option value="Electronics" className="text-slate-800">Electronics</option>
                  </select>
                </p>
              </div>
            </div>

            <div className="flex items-center gap-1">
              <button
                onClick={handleClearHistory}
                className="p-1.5 rounded-lg hover:bg-white/15 text-white/80 hover:text-white transition-colors"
                title="Reset conversation"
              >
                <RotateCcw className="w-4 h-4" />
              </button>
              <button
                onClick={() => setIsOpen(false)}
                className="p-1.5 rounded-lg hover:bg-white/15 text-white/80 hover:text-white transition-colors"
                title="Close chat"
              >
                <X className="w-4 h-4" />
              </button>
            </div>
          </div>

          {/* Messages List Area */}
          <div className="flex-1 p-4 overflow-y-auto space-y-4 bg-slate-50/70">
            {messages.map((msg) => {
              const isUser = msg.role === 'user';
              return (
                <div
                  key={msg.id}
                  className={`flex gap-2.5 ${isUser ? 'justify-end' : 'justify-start'}`}
                >
                  {!isUser && (
                    <div className="w-7 h-7 rounded-lg ai-gradient-bg text-white flex items-center justify-center shrink-0 text-xs shadow-xs mt-0.5">
                      <Sparkles className="w-3.5 h-3.5" />
                    </div>
                  )}

                  <div className={`max-w-[90%] flex flex-col ${isUser ? 'items-end' : 'items-start'}`}>
                    <div
                      className={`px-4 py-3 rounded-2xl text-xs sm:text-sm leading-relaxed shadow-xs ${
                        isUser
                          ? 'bg-indigo-600 text-white rounded-tr-xs font-medium'
                          : 'bg-white border border-slate-200/80 text-slate-800 rounded-tl-xs'
                      }`}
                    >
                      <p className="whitespace-pre-wrap">{msg.content}</p>

                      {msg.isAuthPrompt && (
                        <div className="mt-3">
                          <Link
                            to="/login?from=/dashboard"
                            className="inline-flex items-center gap-1.5 px-4 py-2 rounded-xl ai-gradient-bg text-white font-bold text-xs shadow-md shadow-indigo-600/20 hover:shadow-indigo-600/40 hover:scale-102 transition-all"
                          >
                            <span>Sign In to Continue</span>
                            <ArrowRight className="w-3.5 h-3.5" />
                          </Link>
                        </div>
                      )}

                      {/* Display extracted slots or filters if present */}
                      {(msg.extracted || msg.slots) && (
                        <div className="mt-2.5 pt-2 border-t border-slate-100 flex flex-wrap gap-1 text-[10px] text-slate-500">
                          <span className="font-semibold text-indigo-600">Filters:</span>
                          {(msg.extracted?.category || msg.slots?.category) && (
                            <span className="bg-indigo-50 text-indigo-700 px-2 py-0.5 rounded-full font-medium">
                              Category: {msg.extracted?.category || msg.slots?.category}
                            </span>
                          )}
                          {(msg.extracted?.budget || msg.slots?.budget_max) && (
                            <span className="bg-emerald-50 text-emerald-700 px-2 py-0.5 rounded-full font-medium">
                              Max Budget: ₹{Number(msg.extracted?.budget || msg.slots?.budget_max).toLocaleString('en-IN')}
                            </span>
                          )}
                          {(msg.extracted?.brand || msg.slots?.brand) && (
                            <span className="bg-purple-50 text-purple-700 px-2 py-0.5 rounded-full font-medium">
                              Brand: {msg.extracted?.brand || msg.slots?.brand}
                            </span>
                          )}
                        </div>
                      )}

                      {/* Side-by-Side Comparison Box */}
                      {msg.comparison && (
                        <div className="mt-3 pt-2.5 border-t border-slate-100 w-full space-y-2.5">
                          <div className="flex items-center gap-1.5 text-xs font-bold text-indigo-700">
                            <Scale className="w-4 h-4 text-indigo-600" />
                            <span>Feature Comparison</span>
                          </div>

                          {/* Comparison Table */}
                          <div className="overflow-x-auto rounded-xl border border-slate-200 bg-slate-50/50">
                            <table className="w-full text-[11px] text-left">
                              <thead>
                                <tr className="border-b border-slate-200 bg-slate-100/70 text-slate-600 font-bold">
                                  <th className="p-2">Feature</th>
                                  <th className="p-2 truncate max-w-[100px]">{msg.comparison.product_a?.title?.slice(0, 18)}...</th>
                                  <th className="p-2 truncate max-w-[100px]">{msg.comparison.product_b?.title?.slice(0, 18)}...</th>
                                </tr>
                              </thead>
                              <tbody className="divide-y divide-slate-200/60">
                                <tr>
                                  <td className="p-2 font-semibold text-slate-500">Price</td>
                                  <td className="p-2 font-extrabold text-slate-900">₹{Number(msg.comparison.product_a?.price || 0).toLocaleString('en-IN')}</td>
                                  <td className="p-2 font-extrabold text-slate-900">₹{Number(msg.comparison.product_b?.price || 0).toLocaleString('en-IN')}</td>
                                </tr>
                                {msg.comparison.feature_comparison && Object.entries(msg.comparison.feature_comparison).map(([dim, data]) => (
                                  <tr key={dim}>
                                    <td className="p-2 font-medium text-slate-500 capitalize">{dim}</td>
                                    <td className="p-2 text-slate-700">{data.a || '—'}</td>
                                    <td className="p-2 text-slate-700">{data.b || '—'}</td>
                                  </tr>
                                ))}
                              </tbody>
                            </table>
                          </div>

                          {/* Verdicts */}
                          {msg.comparison.verdicts && (
                            <div className="p-2.5 bg-indigo-50/80 rounded-xl border border-indigo-100 text-[11px] space-y-1">
                              <div className="font-bold text-indigo-900 flex items-center gap-1 mb-1">
                                <Sparkles className="w-3.5 h-3.5 text-indigo-600" />
                                <span>Expert Verdicts:</span>
                              </div>
                              {msg.comparison.verdicts.best_for_photography && (
                                <p className="text-slate-700">📷 <strong>Best for Photography:</strong> {msg.comparison.verdicts.best_for_photography}</p>
                              )}
                              {msg.comparison.verdicts.best_for_gaming && (
                                <p className="text-slate-700">🎮 <strong>Best for Gaming:</strong> {msg.comparison.verdicts.best_for_gaming}</p>
                              )}
                              {msg.comparison.verdicts.best_for_value && (
                                <p className="text-slate-700">💎 <strong>Best for Value:</strong> {msg.comparison.verdicts.best_for_value}</p>
                              )}
                            </div>
                          )}
                        </div>
                      )}

                      {/* Selectable Clarification / Flow Chips */}
                      {msg.options && msg.options.length > 0 && (
                        <div className="mt-3 pt-2.5 border-t border-slate-100">
                          <p className="text-[11px] font-semibold text-slate-600 mb-2 flex items-center gap-1.5">
                            <Sparkles className="w-3.5 h-3.5 text-indigo-600" />
                            <span>Quick Selection:</span>
                          </p>
                          <div className="flex flex-wrap gap-1.5">
                            {msg.options.map((opt) => (
                              <button
                                key={opt}
                                type="button"
                                onClick={() => handleSendMessage(opt)}
                                className="px-3 py-1.5 bg-indigo-50 hover:bg-indigo-600 text-indigo-700 hover:text-white rounded-xl text-xs font-semibold border border-indigo-200/80 shadow-2xs hover:shadow-md transition-all duration-200 cursor-pointer active:scale-95 flex items-center gap-1.5"
                              >
                                <span>{opt}</span>
                                <ArrowRight className="w-3 h-3 opacity-60" />
                              </button>
                            ))}
                          </div>
                        </div>
                      )}

                      {/* Selectable Alternative Query Chips/Buttons */}
                      {msg.alternatives && msg.alternatives.length > 0 && (
                        <div className="mt-3 pt-2.5 border-t border-slate-100">
                          <p className="text-[11px] font-semibold text-slate-600 mb-2 flex items-center gap-1.5">
                            <Sparkles className="w-3.5 h-3.5 text-indigo-600" />
                            <span>Suggested alternatives:</span>
                          </p>
                          <div className="flex flex-wrap gap-1.5">
                            {msg.alternatives.map((alt) => (
                              <button
                                key={alt}
                                type="button"
                                onClick={() => handleSendMessage(alt)}
                                className="px-3 py-1.5 bg-indigo-50 hover:bg-indigo-600 text-indigo-700 hover:text-white rounded-xl text-xs font-semibold border border-indigo-200/80 shadow-2xs hover:shadow-md transition-all duration-200 cursor-pointer active:scale-95 flex items-center gap-1.5"
                              >
                                <span>{alt}</span>
                                <ArrowRight className="w-3 h-3 opacity-60" />
                              </button>
                            ))}
                          </div>
                        </div>
                      )}
                    </div>

                    {/* Inline Top 2 Products Grid inside assistant turn */}
                    {msg.products && msg.products.length > 0 && (
                      <div className="mt-2.5 w-full space-y-2">
                        <div className="flex items-center justify-between px-1">
                          <span className="text-[10px] font-bold uppercase tracking-wider text-slate-500 flex items-center gap-1">
                            <Sparkles className="w-3 h-3 text-indigo-600" />
                            Top Ranked Recommendations ({Math.min(msg.products.length, 2)})
                          </span>
                        </div>
                        <div className="space-y-2.5">
                          {msg.products.slice(0, 2).map((p, pIdx) => {
                            const isAddedToCompare = compareSet?.has(p.id);
                            const rankNum = p.rank || (pIdx === 0 ? 1 : 2);
                            const isTop = rankNum === 1;
                            const scoreVal = p.score || p.match_score;
                            const rankBadge = isTop ? '#1 TOP RECOMMENDATION' : '#2 RUNNER UP';

                            return (
                              <div
                                key={p.id}
                                className={`p-3 bg-white rounded-2xl border transition-all shadow-xs flex flex-col gap-2 ${
                                  isTop
                                    ? 'border-amber-300 ring-1 ring-amber-200/50 shadow-amber-500/5'
                                    : 'border-indigo-200 shadow-indigo-500/5'
                                }`}
                              >
                                <div className="flex items-start justify-between gap-3">
                                  <div className="flex items-start gap-2.5 min-w-0">
                                    <img
                                      src={p.image_url || 'https://images.unsplash.com/photo-1523275335684-37898b6baf30?auto=format&fit=crop&w=150&q=80'}
                                      alt={p.title}
                                      className="w-14 h-14 rounded-xl object-cover bg-slate-100 shrink-0 border border-slate-100"
                                      onError={(e) => {
                                        e.target.src = 'https://images.unsplash.com/photo-1526170375885-4d8ecf77b99f?auto=format&fit=crop&w=150&q=80';
                                      }}
                                    />
                                    <div className="min-w-0">
                                      <div className="flex items-center gap-1.5 mb-1 flex-wrap">
                                        <span className={`text-[9px] font-black uppercase px-2 py-0.5 rounded-md flex items-center gap-1 ${
                                          isTop
                                            ? 'bg-amber-500 text-white shadow-2xs'
                                            : 'bg-indigo-600 text-white shadow-2xs'
                                        }`}>
                                          <span>{rankBadge}</span>
                                        </span>
                                        {scoreVal && (
                                          <span className="text-[9px] font-extrabold bg-slate-100 text-slate-800 px-1.5 py-0.5 rounded border border-slate-200">
                                            Score: {scoreVal}/100
                                          </span>
                                        )}
                                        <span className="text-[9px] font-bold uppercase tracking-wider text-indigo-600 bg-indigo-50 px-1.5 py-0.5 rounded">
                                          {p.brand}
                                        </span>
                                      </div>
                                      <p className="text-[11px] font-bold text-slate-800 line-clamp-1" title={p.title}>
                                        {p.title}
                                      </p>
                                      <div className="flex items-center gap-2 text-[10px] text-slate-500 mt-0.5">
                                        <span className="font-extrabold text-slate-900 text-xs">
                                          ₹{Number(p.price).toLocaleString('en-IN')}
                                        </span>
                                        {p.discount_percent && p.discount_percent > 0 && (
                                          <span className="text-rose-600 font-bold bg-rose-50 px-1 py-0.2 rounded">
                                            {p.discount_percent}% OFF
                                          </span>
                                        )}
                                        <span>·</span>
                                        <span className="text-amber-500 font-semibold flex items-center gap-0.5">
                                          ★ {p.rating || '4.5'}
                                        </span>
                                      </div>
                                    </div>
                                  </div>

                                  <div className="flex items-center gap-1.5 shrink-0">
                                    <button
                                      type="button"
                                      onClick={() => onToggleCompare && onToggleCompare(p)}
                                      className={`p-1.5 rounded-lg text-[10px] font-semibold transition-all cursor-pointer ${
                                        isAddedToCompare
                                          ? 'bg-pink-600 text-white'
                                          : 'bg-slate-100 hover:bg-slate-200 text-slate-700'
                                      }`}
                                      title={isAddedToCompare ? 'Remove from compare' : 'Compare'}
                                    >
                                      <Scale className="w-3.5 h-3.5" />
                                    </button>
                                    <Link
                                      to={`/product/${p.id}`}
                                      className="p-1.5 rounded-lg bg-slate-900 hover:bg-indigo-600 text-white text-[10px] transition-colors cursor-pointer"
                                      title="View product details"
                                    >
                                      <ExternalLink className="w-3.5 h-3.5" />
                                    </Link>
                                  </div>
                                </div>

                                {/* Why Recommended bullets */}
                                {p.why_recommended && p.why_recommended.length > 0 && (
                                  <div className="p-2 bg-slate-50 rounded-xl text-[10px] text-slate-800 space-y-0.5 border border-slate-200/80">
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
                      </div>
                    )}

                    <span className="text-[10px] text-slate-400 mt-1 px-1">
                      {msg.timestamp}
                    </span>
                  </div>

                  {isUser && (
                    <div className="w-7 h-7 rounded-lg bg-slate-200 text-slate-700 flex items-center justify-center shrink-0 text-xs shadow-xs mt-0.5">
                      <User className="w-3.5 h-3.5" />
                    </div>
                  )}
                </div>
              );
            })}

            {/* Typing Indicator */}
            {isLoading && (
              <div className="flex items-center gap-2 text-slate-500 text-xs pl-2 animate-pulse">
                <div className="w-6 h-6 rounded-lg ai-gradient-bg text-white flex items-center justify-center">
                  <Sparkles className="w-3 h-3 animate-spin" />
                </div>
                <div className="flex items-center gap-1 bg-white border border-slate-200 px-3 py-2 rounded-2xl">
                  <span className="w-1.5 h-1.5 rounded-full bg-indigo-500 animate-bounce" style={{ animationDelay: '0ms' }} />
                  <span className="w-1.5 h-1.5 rounded-full bg-indigo-500 animate-bounce" style={{ animationDelay: '150ms' }} />
                  <span className="w-1.5 h-1.5 rounded-full bg-indigo-500 animate-bounce" style={{ animationDelay: '300ms' }} />
                  <span className="ml-1 text-[11px] text-slate-400">ShopAI is thinking...</span>
                </div>
              </div>
            )}

            <div ref={messagesEndRef} />
          </div>

          {/* Quick Prompts Bar */}
          <div className="px-3 py-2 bg-white border-t border-slate-100 flex items-center gap-1.5 overflow-x-auto no-scrollbar shrink-0">
            {quickPrompts.map((prompt, i) => (
              <button
                key={i}
                onClick={() => handleSendMessage(prompt)}
                className="text-[11px] bg-slate-100 hover:bg-indigo-50 hover:text-indigo-600 text-slate-600 font-medium px-2.5 py-1 rounded-full whitespace-nowrap transition-colors shrink-0"
              >
                {prompt}
              </button>
            ))}
          </div>

          {/* Input Composer */}
          <form
            onSubmit={(e) => {
              e.preventDefault();
              handleSendMessage();
            }}
            className="p-3 bg-white border-t border-slate-200/80 flex items-center gap-2 shrink-0"
          >
            <input
              ref={inputRef}
              type="text"
              value={inputValue}
              onChange={(e) => setInputValue(e.target.value)}
              placeholder={`Ask ShopAI in ${selectedCategory}...`}
              disabled={isLoading}
              className="flex-1 py-2 px-3.5 text-xs bg-slate-100 focus:bg-white text-slate-800 placeholder-slate-400 rounded-xl border border-transparent focus:border-indigo-500 focus:ring-4 focus:ring-indigo-500/10 transition-all outline-hidden"
            />
            <button
              type="submit"
              disabled={!inputValue.trim() || isLoading}
              className="p-2.5 rounded-xl ai-gradient-bg text-white disabled:opacity-40 disabled:cursor-not-allowed hover:shadow-md hover:shadow-indigo-500/25 active:scale-95 transition-all"
            >
              <Send className="w-4 h-4" />
            </button>
          </form>

        </div>
      )}
    </>
  );
}
