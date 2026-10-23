import api from './client';

// POST /api/v1/auth/register -> { statuscode, message, data }
export const registerUser = (payload) => api.post('/api/v1/auth/register', payload).then((r) => r.data);
// POST /api/v1/auth/login -> { statuscode, message, tokens: { access_token, refresh_token, token_type } }
export const loginUser = (payload) => api.post('/api/v1/auth/login', payload).then((r) => r.data);
// GET /api/v1/auth/me -> { status_code, message, data: user }
export const getMe = () => api.get('/api/v1/auth/me').then((r) => r.data.data);
// POST /api/v1/auth/logout
export const logoutUser = () => api.post('/api/v1/auth/logout').then((r) => r.data);
