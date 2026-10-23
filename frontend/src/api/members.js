import api from './client';

// GET /api/v1/trips/{id}/members -> { members: [...] }
export const listMembers = (tripId) => api.get(`/api/v1/trips/${tripId}/members`).then((r) => r.data.members);
// POST /api/v1/trips/{id}/members  body: { display_name } -> { data: member }
export const addMember = (tripId, payload) =>
  api.post(`/api/v1/trips/${tripId}/members`, payload).then((r) => r.data.data);
// DELETE /api/v1/trips/{id}/members/{member_id} -> member with status "LEFT"
export const removeMember = (tripId, memberId) =>
  api.delete(`/api/v1/trips/${tripId}/members/${memberId}`).then((r) => r.data);
