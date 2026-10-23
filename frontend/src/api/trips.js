import api from './client';

// GET /api/v1/trips -> array of trips owned by the user
export const listTrips = () => api.get('/api/v1/trips').then((r) => r.data);
// GET /api/v1/trips/{id} -> trip object (not wrapped)
export const getTrip = (id) => api.get(`/api/v1/trips/${id}`).then((r) => r.data);
// POST /api/v1/trips -> { data: trip }
export const createTrip = (payload) => api.post('/api/v1/trips', payload).then((r) => r.data.data);
// PATCH /api/v1/trips/{id} -> { data: trip }
export const updateTrip = (id, payload) => api.patch(`/api/v1/trips/${id}`, payload).then((r) => r.data.data);
// DELETE /api/v1/trips/{id}
export const deleteTrip = (id) => api.delete(`/api/v1/trips/${id}`).then((r) => r.data);
