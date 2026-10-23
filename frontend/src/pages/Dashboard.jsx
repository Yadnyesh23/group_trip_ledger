import { useState } from 'react';
import { Link, useNavigate } from 'react-router-dom';
import { Calendar, MapPin, Plus, Plane } from 'lucide-react';
import { Badge, Button, Empty, ErrorBox, Modal, PageHeader, Spinner } from '../components/ui';
import TripForm from '../components/TripForm';
import { createTrip, listTrips } from '../api/trips';
import { useAsync } from '../hooks/useAsync';
import { formatDateRange, tripStatus } from '../utils/format';

export default function Dashboard() {
  const navigate = useNavigate();
  const { data: trips, loading, error, reload } = useAsync(listTrips);
  const [creating, setCreating] = useState(false);

  const onCreate = async (payload) => {
    const trip = await createTrip(payload);
    navigate(`/trips/${trip.id}`);
  };

  return (
    <div className="mx-auto max-w-5xl">
      <PageHeader title="My Trips" action={<Button onClick={() => setCreating(true)}><Plus className="h-4 w-4" /> Create Trip</Button>} />
      {loading && <Spinner />}
      <ErrorBox message={error} onRetry={reload} />
      {trips && trips.length === 0 && (
        <Empty icon={Plane} title="No trips yet" text="Create your first trip to start adding members and expenses.">
          <Button onClick={() => setCreating(true)}><Plus className="h-4 w-4" /> Create Trip</Button>
        </Empty>
      )}
      {trips && trips.length > 0 && (
        <div className="grid gap-4 sm:grid-cols-2">
          {trips.map((t) => {
            const status = tripStatus(t);
            return (
              <Link key={t.id} to={`/trips/${t.id}`} className="rounded-2xl border border-slate-200 bg-white p-4 shadow-sm transition hover:shadow-md focus:outline-none focus-visible:ring-2 focus-visible:ring-blue-500">
                <div className="flex items-start justify-between gap-2">
                  <h2 className="font-semibold text-slate-900">{t.name}</h2>
                  <Badge tone={status.tone}>{status.label}</Badge>
                </div>
                <p className="mt-2 flex items-center gap-1.5 text-xs text-slate-500"><MapPin className="h-3.5 w-3.5" /> {t.location || 'No location'}</p>
                <p className="mt-1 flex items-center gap-1.5 text-xs text-slate-500"><Calendar className="h-3.5 w-3.5" /> {formatDateRange(t.start_date, t.end_date)}</p>
              </Link>
            );
          })}
        </div>
      )}
      {creating && (
        <Modal title="Create Trip" onClose={() => setCreating(false)}>
          <TripForm submitLabel="Create Trip" onSubmit={onCreate} onCancel={() => setCreating(false)} />
        </Modal>
      )}
    </div>
  );
}
