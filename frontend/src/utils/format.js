const money = new Intl.NumberFormat('en-IN', { style: 'currency', currency: 'INR', maximumFractionDigits: 2 });

export const formatMoney = (n) => money.format(Number(n) || 0);
export const initials = (name = '') =>
  name.split(' ').filter(Boolean).slice(0, 2).map((p) => p[0].toUpperCase()).join('') || '?';

// "2026-10-10" -> "10 Oct 2026" (parsed by hand so time zones can't shift the day)
export function formatDate(iso) {
  if (!iso) return '—';
  const [y, m, d] = iso.slice(0, 10).split('-').map(Number);
  return new Date(y, m - 1, d).toLocaleDateString('en-GB', { day: 'numeric', month: 'short', year: 'numeric' });
}
export const formatDateRange = (a, b) => `${formatDate(a)} - ${formatDate(b)}`;

export const todayISO = () => {
  const d = new Date();
  return `${d.getFullYear()}-${String(d.getMonth() + 1).padStart(2, '0')}-${String(d.getDate()).padStart(2, '0')}`;
};

export function tripStatus(trip) {
  const today = todayISO();
  if (trip.is_completed || trip.end_date < today) return { label: 'Completed', tone: 'green' };
  if (trip.start_date > today) return { label: 'Upcoming', tone: 'gray' };
  return { label: 'Ongoing', tone: 'blue' };
}

// --- Money helpers: work in integer paise to avoid floating-point drift ---
export const toCents = (v) => Math.round(Number(String(v ?? '').replace(/,/g, '')) * 100);

// Display-only preview of an equal split. The backend calculates the real allocation.
export function equalSplitCents(totalCents, count) {
  if (!count || !Number.isFinite(totalCents)) return [];
  const base = Math.floor(totalCents / count);
  const extra = totalCents - base * count;
  return Array.from({ length: count }, (_, i) => base + (i < extra ? 1 : 0));
}

// Turns axios / FastAPI errors into one readable sentence.
export function errorMessage(err) {
  if (err?.response) {
    const detail = err.response.data?.detail ?? err.response.data?.message;
    if (typeof detail === 'string') return detail;
    if (Array.isArray(detail)) {
      return detail.map((d) => `${(d.loc || []).slice(1).join('.') || 'Field'}: ${d.msg}`).join('; ');
    }
    return `Request failed (${err.response.status}).`;
  }
  if (err?.request) return 'Cannot reach the server. Check that the backend is running and CORS allows this site.';
  return err?.message || 'Something went wrong.';
}
