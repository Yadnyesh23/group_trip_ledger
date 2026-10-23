/* eslint-disable react-refresh/only-export-components */
import { createContext, useCallback, useContext, useEffect, useMemo, useState } from 'react';
import { tokenStore } from '../api/client';
import { getMe, loginUser, logoutUser } from '../api/auth';

const AuthContext = createContext(null);
export const useAuth = () => useContext(AuthContext);

export function AuthProvider({ children }) {
  const [user, setUser] = useState(null);
  const [loading, setLoading] = useState(Boolean(tokenStore.get()));

  // Restore the session on first load.
  useEffect(() => {
    if (!tokenStore.get()) return;
    getMe()
      .then(setUser)
      .catch(() => tokenStore.clear())
      .finally(() => setLoading(false));
  }, []);

  // The Axios client fires this when a token refresh fails.
  useEffect(() => {
    const onLogout = () => setUser(null);
    window.addEventListener('gtl:logout', onLogout);
    return () => window.removeEventListener('gtl:logout', onLogout);
  }, []);

  const login = useCallback(async ({ email, password, remember }) => {
    const res = await loginUser({ email, password });
    tokenStore.set(res.tokens, Boolean(remember));
    setUser(await getMe());
  }, []);

  const logout = useCallback(async () => {
    try {
      await logoutUser();
    } catch {
      /* clear local state even if the server call fails */
    }
    tokenStore.clear();
    setUser(null);
  }, []);

  const value = useMemo(() => ({ user, loading, login, logout }), [user, loading, login, logout]);
  return <AuthContext.Provider value={value}>{children}</AuthContext.Provider>;
}
