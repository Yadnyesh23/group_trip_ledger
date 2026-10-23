import axios from 'axios';

export const BASE_URL = import.meta.env.VITE_API_BASE_URL || 'http://127.0.0.1:8000';
const KEY = 'gtl_tokens';

// "Remember me" -> localStorage (survives browser restarts), otherwise sessionStorage.
export const tokenStore = {
  get() {
    const raw = localStorage.getItem(KEY) ?? sessionStorage.getItem(KEY);
    try {
      return raw ? JSON.parse(raw) : null;
    } catch {
      return null;
    }
  },
  isPersistent: () => localStorage.getItem(KEY) !== null,
  set(tokens, remember = tokenStore.isPersistent()) {
    tokenStore.clear();
    (remember ? localStorage : sessionStorage).setItem(KEY, JSON.stringify(tokens));
  },
  clear() {
    localStorage.removeItem(KEY);
    sessionStorage.removeItem(KEY);
  },
};

const api = axios.create({ baseURL: BASE_URL, timeout: 20000 });

api.interceptors.request.use((config) => {
  const tokens = tokenStore.get();
  if (tokens?.access_token && !config.headers.Authorization) {
    config.headers.Authorization = `Bearer ${tokens.access_token}`;
  }
  return config;
});

function onAuthFailure() {
  tokenStore.clear();
  window.dispatchEvent(new Event('gtl:logout'));
}

// One shared refresh request at a time; every request is retried at most once.
let refreshing = null;
const isAuthUrl = (url = '') => /\/auth\/(login|register|refresh)/.test(url);

api.interceptors.response.use(
  (response) => response,
  async (error) => {
    const { config, response } = error;
    if (response?.status !== 401 || !config || config._retry || isAuthUrl(config.url)) {
      return Promise.reject(error);
    }
    const tokens = tokenStore.get();
    if (!tokens?.refresh_token) {
      onAuthFailure();
      return Promise.reject(error);
    }
    config._retry = true;
    try {
      if (!refreshing) {
        // Plain axios (not `api`) so this call can never trigger the interceptor again.
        refreshing = axios
          .post(`${BASE_URL}/api/v1/auth/refresh`, null, {
            headers: { Authorization: `Bearer ${tokens.refresh_token}` },
          })
          .finally(() => {
            refreshing = null;
          });
      }
      const { data } = await refreshing;
      tokenStore.set({ ...tokens, access_token: data.access_token });
      config.headers.Authorization = `Bearer ${data.access_token}`;
      return api(config);
    } catch {
      onAuthFailure();
      return Promise.reject(error);
    }
  },
);

export default api;
