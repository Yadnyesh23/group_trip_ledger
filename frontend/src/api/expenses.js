import api from './client';

// GET /api/v1/trips/{id}/expenses -> { total_expenses (count), expenses: [...] }
export const listExpenses = (tripId) => api.get(`/api/v1/trips/${tripId}/expenses`).then((r) => r.data);
// POST /api/v1/trips/{id}/expenses -> created expense
export const createExpense = (tripId, payload) =>
  api.post(`/api/v1/trips/${tripId}/expenses`, payload).then((r) => r.data);
