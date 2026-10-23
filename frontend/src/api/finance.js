import api from './client';

// NOTE: balances and settlements live WITHOUT the /api/v1 prefix (as documented),
// and the trailing slash is part of the documented path.
export const getBalances = (tripId) => api.get(`/trips/${tripId}/balances/`).then((r) => r.data.balances);
export const getSettlements = (tripId) => api.get(`/trips/${tripId}/settlements/`).then((r) => r.data.settlements);

// Reports use the singular "/trip/" path (as documented).
export const getReport = (tripId) => api.get(`/api/v1/trip/${tripId}/reports/`).then((r) => r.data);

export async function downloadReportPdf(tripId) {
  const res = await api.get(`/api/v1/trip/${tripId}/reports/pdf`, { responseType: 'blob' });
  const disposition = res.headers['content-disposition'] || '';
  const match = /filename="?([^";]+)"?/i.exec(disposition);
  const filename = match ? match[1] : `trip_report_${tripId}.pdf`;
  const url = URL.createObjectURL(new Blob([res.data], { type: 'application/pdf' }));
  const link = document.createElement('a');
  link.href = url;
  link.download = filename;
  document.body.appendChild(link);
  link.click();
  link.remove();
  URL.revokeObjectURL(url);
}
