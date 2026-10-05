/**
 * ShopAI API Service Layer
 * Connects to FastAPI backend on http://127.0.0.1:8000
 */

const rawApiUrl = import.meta.env.VITE_API_URL || 'https://genai-shopping-assistant-3.onrender.com';
const API_BASE_URL = rawApiUrl.replace(/\/+$/, '');

class ApiService {
  constructor() {
    this.token = localStorage.getItem('shopai_token') || null;
    this.user = JSON.parse(localStorage.getItem('shopai_user') || 'null');
  }

  getHeaders() {
    const headers = {
      'Content-Type': 'application/json',
    };
    const currentToken = this.token || localStorage.getItem('shopai_token');
    if (currentToken) {
      headers['Authorization'] = `Bearer ${currentToken}`;
    }
    return headers;
  }

  async handleResponse(response) {
    if (response.status === 401) {
      this.logout();
      const errorData = await response.json().catch(() => ({}));
      const message = errorData.detail || errorData.message || 'Session expired. Please login again.';
      throw new Error(message);
    }
    if (!response.ok) {
      const errorData = await response.json().catch(() => ({}));
      const message = errorData.detail || errorData.message || `Request failed with status ${response.status}`;
      throw new Error(message);
    }
    const data = await response.json();
    if (data && data.success === false) {
      throw new Error(data.message || 'Request failed.');
    }
    return data;
  }

  // 1. Authentication
  async checkEmail(email) {
    const res = await fetch(`${API_BASE_URL}/api/auth/check-email`, {
      method: 'POST',
      headers: this.getHeaders(),
      body: JSON.stringify({ email }),
    });
    return this.handleResponse(res);
  }

  async register(formData) {
    const res = await fetch(`${API_BASE_URL}/api/auth/register`, {
      method: 'POST',
      headers: this.getHeaders(),
      body: JSON.stringify(formData),
    });
    return this.handleResponse(res);
  }

  async verifyOtp({ email, otp }) {
    const res = await fetch(`${API_BASE_URL}/api/auth/verify-otp`, {
      method: 'POST',
      headers: this.getHeaders(),
      body: JSON.stringify({ email, otp }),
    });
    return this.handleResponse(res);
  }

  async resendOtp(email) {
    const res = await fetch(`${API_BASE_URL}/api/auth/resend-otp`, {
      method: 'POST',
      headers: this.getHeaders(),
      body: JSON.stringify({ email }),
    });
    return this.handleResponse(res);
  }

  async login(credentials) {
    const res = await fetch(`${API_BASE_URL}/api/auth/login`, {
      method: 'POST',
      headers: this.getHeaders(),
      body: JSON.stringify(credentials),
    });
    const data = await this.handleResponse(res);
    if (data.token && data.user) {
      this.token = data.token;
      this.user = data.user;
      localStorage.setItem('shopai_token', data.token);
      localStorage.setItem('shopai_user', JSON.stringify(data.user));
    }
    return data;
  }

  async forgotPassword(email) {
    const res = await fetch(`${API_BASE_URL}/api/auth/forgot-password`, {
      method: 'POST',
      headers: this.getHeaders(),
      body: JSON.stringify({ email }),
    });
    return this.handleResponse(res);
  }

  async verifyResetOtp({ email, otp }) {
    const res = await fetch(`${API_BASE_URL}/api/auth/verify-reset-otp`, {
      method: 'POST',
      headers: this.getHeaders(),
      body: JSON.stringify({ email, otp }),
    });
    return this.handleResponse(res);
  }

  async resetPassword({ email, otp, new_password, confirm_password }) {
    const res = await fetch(`${API_BASE_URL}/api/auth/reset-password`, {
      method: 'POST',
      headers: this.getHeaders(),
      body: JSON.stringify({ email, otp, new_password, confirm_password }),
    });
    return this.handleResponse(res);
  }

  async getProfile() {
    const res = await fetch(`${API_BASE_URL}/api/auth/me`, {
      headers: this.getHeaders(),
    });
    const data = await this.handleResponse(res);
    if (data.user) {
      this.user = data.user;
      localStorage.setItem('shopai_user', JSON.stringify(data.user));
    }
    return data;
  }

  async updateProfile(name) {
    const res = await fetch(`${API_BASE_URL}/api/auth/profile`, {
      method: 'PUT',
      headers: this.getHeaders(),
      body: JSON.stringify({ name }),
    });
    const data = await this.handleResponse(res);
    if (this.user) {
      this.user = { ...this.user, name };
      localStorage.setItem('shopai_user', JSON.stringify(this.user));
    }
    return data;
  }

  async changePassword({ current_password, new_password, confirm_password }) {
    const res = await fetch(`${API_BASE_URL}/api/auth/change-password`, {
      method: 'PUT',
      headers: this.getHeaders(),
      body: JSON.stringify({ current_password, new_password, confirm_password }),
    });
    return this.handleResponse(res);
  }

  logout() {
    this.token = null;
    this.user = null;
    localStorage.removeItem('shopai_token');
    localStorage.removeItem('shopai_user');
  }

  getCurrentUser() {
    return this.user;
  }

  // 2. Categories
  async getCategories() {
    try {
      const res = await fetch(`${API_BASE_URL}/api/categories`, {
        headers: this.getHeaders(),
      });
      const data = await this.handleResponse(res);
      return data.categories || [];
    } catch (err) {
      console.warn('Using default categories:', err);
      return [
        { id: 'electronics', name: 'Electronics', icon: 'Cpu', count: 250, description: 'Laptops, Audio, Cameras & Wearables' },
        { id: 'fashion', name: 'Fashion', icon: 'Shirt', count: 220, description: 'Apparel, Footwear & Accessories' },
        { id: 'toys', name: 'Toys', icon: 'Gamepad2', count: 120, description: 'LEGO, STEM Kits, Board Games & Collectibles' },
        { id: 'beauty', name: 'Beauty', icon: 'Sparkles', count: 180, description: 'Skincare, Makeup & Fragrances' },
        { id: 'home_and_kitchen', name: 'Home & Kitchen', icon: 'Home', count: 310, description: 'Cookware, Decor & Furnishing' },
        { id: 'books', name: 'Books', icon: 'BookOpen', count: 140, description: 'Technology, Fiction & Self-Growth' },
        { id: 'sports', name: 'Sports', icon: 'Dumbbell', count: 190, description: 'Fitness Equipment, Gear & Apparel' },
      ];
    }
  }

  // 3. Trending Products
  async getTrendingProducts(category = '', limit = 8) {
    try {
      const url = category
        ? `${API_BASE_URL}/api/products/trending?category=${encodeURIComponent(category)}&limit=${limit}`
        : `${API_BASE_URL}/api/products/trending?limit=${limit}`;
      const res = await fetch(url, {
        headers: this.getHeaders(),
      });
      const data = await this.handleResponse(res);
      return data.products || [];
    } catch (err) {
      console.warn('Error fetching trending products:', err);
      return [];
    }
  }

  // 4. Recommended Products
  async getRecommendedProducts(category = '', limit = 12) {
    try {
      const url = category
        ? `${API_BASE_URL}/api/products/recommended?category=${encodeURIComponent(category)}&limit=${limit}`
        : `${API_BASE_URL}/api/products/recommended?limit=${limit}`;
      const res = await fetch(url, { headers: this.getHeaders() });
      const data = await this.handleResponse(res);
      return data.products || [];
    } catch (err) {
      console.warn('Error fetching recommended products:', err);
      return [];
    }
  }

  // 5. Search Products (/api/query)
  async searchProducts(query, category = 'Electronics') {
    const res = await fetch(`${API_BASE_URL}/api/query`, {
      method: 'POST',
      headers: this.getHeaders(),
      body: JSON.stringify({ query, category }),
    });
    return this.handleResponse(res);
  }

  // 6. Product Details
  async getProductDetails(productId) {
    const res = await fetch(`${API_BASE_URL}/api/products/${encodeURIComponent(productId)}`, {
      headers: this.getHeaders(),
    });
    return this.handleResponse(res);
  }

  // 7. Compare Products (/api/compare)
  async compareProducts(productIds, category = 'Electronics') {
    const res = await fetch(`${API_BASE_URL}/api/compare`, {
      method: 'POST',
      headers: this.getHeaders(),
      body: JSON.stringify({ product_ids: productIds, category }),
    });
    return this.handleResponse(res);
  }

  // 8. Chat Assistant (/api/chat)
  async chatAssistant(message, category = null, history = [], userId = null) {
    const user = this.getCurrentUser();
    const resolvedUserId = userId || (user ? user.id : 'default_shopper');
    const res = await fetch(`${API_BASE_URL}/api/chat`, {
      method: 'POST',
      headers: this.getHeaders(),
      body: JSON.stringify({ message, category, history, user_id: resolvedUserId }),
    });
    return this.handleResponse(res);
  }

  // 9. Analytics (/api/analytics)
  async getAnalytics() {
    const res = await fetch(`${API_BASE_URL}/api/analytics`, {
      headers: this.getHeaders(),
    });
    return this.handleResponse(res);
  }

  // 10. Click Tracking (/api/analytics/click)
  async logClick(query, productId) {
    try {
      await fetch(`${API_BASE_URL}/api/analytics/click`, {
        method: 'POST',
        headers: this.getHeaders(),
        body: JSON.stringify({ query, product_id: productId }),
      });
    } catch (e) {
      console.warn('Click logging error:', e);
    }
  }
}

export const api = new ApiService();
export default api;
