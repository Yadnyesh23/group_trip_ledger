import { useState } from 'react';
import { NavLink, Outlet, useNavigate, useOutletContext, useParams } from 'react-router-dom';
import { Calendar, MapPin, Pencil, Trash2 } from 'lucide-react';
import { Badge, Button, Card, ConfirmDialog, ErrorBox, Modal, Spinner } from '../components/ui';
import TripForm from '../components/TripForm';
import { deleteTrip, getTrip, updateTrip } from '../api/trips';
import { useAsync } from '../hooks/useAsync';
import { errorMessage, formatDate, formatDateRange, tripStatus } from '../utils/format';

const tabs = [
  { to: '', label: 'Overview', end: true },
  { to: 'members', label: 'Members' },
  { to: 'expenses', label: 'Expenses' },
  { to: 'balances', label: 'Balances' },
  { to: 'report', label: 'Report' },
];

export default function TripLayout() {
  const { tripId } = useParams();
  const navigate = useNavigate();
  const { data: trip, loading, error, reload } = useAsync(() => getTrip(tripId), [tripId]);
  const [editing, setEditing] = useState(false);
  const [deleting, setDeleting] = useState(false);

  if (loading && !trip) return <Spinner />;
  if (error) return <ErrorBox message={error} onRetry={reload} />;
  if (!trip) return null;

  const status = tripStatus(trip);
  const onEdit = async (payload) => {
    await updateTrip(trip.id, payload);
    setEditing(false);
    reload();
  };
  const onDelete = async () => {
    try {
      await deleteTrip(trip.id);
    } catch (e) {
      throw new Error(errorMessage(e));
    }
    navigate('/dashboard');
  };

  return (
    <div className="mx-auto max-w-5xl">
      <div className="rounded-2xl border border-slate-200 bg-white p-5 shadow-sm">
        <div className="flex items-start justify-between gap-3 mb-6">
          <Badge tone={status.tone}>{status.label}</Badge>
          <Button variant="secondary" onClick={() => setEditing(true)} className="!py-1.5"><Pencil className="h-3.5 w-3.5" /> Edit Trip</Button>
        </div>
        <div>
          <h1 className="text-2xl font-bold text-slate-900">{trip.name}</h1>
          <p className="mt-2 flex flex-wrap gap-x-4 gap-y-1 text-sm text-slate-500">
            <span className="flex items-center gap-1.5"><MapPin className="h-4 w-4" /> {trip.location || 'No location'}</span>
            <span className="flex items-center gap-1.5"><Calendar className="h-4 w-4" /> {formatDateRange(trip.start_date, trip.end_date)}</span>
          </p>
        </div>
      </div>

      <nav className="mt-4 flex gap-1 overflow-x-auto border-b border-slate-200" aria-label="Trip sections">
        {tabs.map((t) => (
          <NavLink key={t.label} to={t.to} end={t.end} className={({ isActive }) => `whitespace-nowrap border-b-2 px-4 py-2 text-sm font-medium ${isActive ? 'border-blue-600 text-blue-600' : 'border-transparent text-slate-500 hover:text-slate-800'}`}>
            {t.label}
          </NavLink>
        ))}
      </nav>

      <div className="mt-5">
        <Outlet context={{ trip, onEdit: () => setEditing(true), onDelete: () => setDeleting(true) }} />
      </div>

      {editing && (
        <Modal title="Edit Trip" onClose={() => setEditing(false)}>
          <TripForm showCompleted submitLabel="Save changes" onSubmit={onEdit} onCancel={() => setEditing(false)}
            defaults={{ name: trip.name, location: trip.location || '', description: trip.description || '', start_date: trip.start_date, end_date: trip.end_date, is_completed: trip.is_completed }} />
        </Modal>
      )}
      {deleting && (
        <ConfirmDialog title="Delete trip?" text={`"${trip.name}" and its members and expenses will be permanently deleted.`} confirmLabel="Delete trip" onConfirm={onDelete} onClose={() => setDeleting(false)} />
      )}
    </div>
  );
}

export function Overview() {
  const { trip, onEdit, onDelete } = useOutletContext();
  const rows = [
    ['Location', trip.location || '—'],
    ['Start Date', formatDate(trip.start_date)],
    ['End Date', formatDate(trip.end_date)],
    ['Owner', trip.owner_name],
    ['Description', trip.description || '—'],
  ];
  return (
    <Card>
      <div className="mb-3 flex items-center justify-between">
        <h2 className="font-semibold text-slate-900">Trip Information</h2>
        <Button variant="secondary" onClick={onEdit} className="!py-1.5"><Pencil className="h-3.5 w-3.5" /> Edit Trip</Button>
      </div>
      <dl className="divide-y divide-slate-100 text-sm">
        {rows.map(([k, v]) => (
          <div key={k} className="grid grid-cols-3 gap-2 py-2.5">
            <dt className="text-slate-500">{k}</dt>
            <dd className="col-span-2 text-slate-800">{v}</dd>
          </div>
        ))}
      </dl>
      <div className="mt-4 border-t border-slate-100 pt-4">
        <Button variant="danger" onClick={onDelete}><Trash2 className="h-4 w-4" /> Delete trip</Button>
      </div>
    </Card>
  );
}
