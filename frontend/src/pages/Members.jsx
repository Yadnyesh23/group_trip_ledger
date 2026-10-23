import { useState } from 'react';
import { useForm } from 'react-hook-form';
import { zodResolver } from '@hookform/resolvers/zod';
import { useOutletContext } from 'react-router-dom';
import { Plus, UserMinus, Users } from 'lucide-react';
import { Avatar, Badge, Button, Card, ConfirmDialog, Empty, ErrorBox, Field, Input, Modal, PageHeader, Spinner } from '../components/ui';
import { addMember, listMembers, removeMember } from '../api/members';
import { useAsync } from '../hooks/useAsync';
import { memberSchema } from '../schemas';
import { errorMessage, formatDate } from '../utils/format';

function AddMemberModal({ tripId, onClose, onAdded }) {
  const [apiError, setApiError] = useState('');
  const { register, handleSubmit, formState: { errors, isSubmitting } } = useForm({
    resolver: zodResolver(memberSchema),
    defaultValues: { display_name: '' },
  });
  const submit = async (v) => {
    setApiError('');
    try {
      await addMember(tripId, { display_name: v.display_name.trim() });
      onAdded();
    } catch (e) {
      setApiError(errorMessage(e));
    }
  };
  return (
    <Modal title="Add Member" onClose={onClose}>
      <form onSubmit={handleSubmit(submit)} className="space-y-3" noValidate>
        <ErrorBox message={apiError} />
        <Field label="Name" htmlFor="m-name" required error={errors.display_name?.message}>
          <Input id="m-name" autoFocus placeholder="e.g. Alice Smith" {...register('display_name')} />
        </Field>
        <div className="flex justify-end gap-2 pt-2">
          <Button type="button" variant="secondary" onClick={onClose} disabled={isSubmitting}>Cancel</Button>
          <Button type="submit" loading={isSubmitting}>Add Member</Button>
        </div>
      </form>
    </Modal>
  );
}

export default function Members() {
  const { trip } = useOutletContext();
  const { data: members, loading, error, reload } = useAsync(() => listMembers(trip.id), [trip.id]);
  const [adding, setAdding] = useState(false);
  const [removing, setRemoving] = useState(null);

  const confirmRemove = async () => {
    try {
      await removeMember(trip.id, removing.id);
    } catch (e) {
      throw new Error(errorMessage(e));
    }
    setRemoving(null);
    reload();
  };

  return (
    <div>
      <PageHeader title="Trip Members" subtitle={trip.name} action={<Button onClick={() => setAdding(true)}><Plus className="h-4 w-4" /> Add Member</Button>} />
      {loading && <Spinner />}
      <ErrorBox message={error} onRetry={reload} />
      {members?.length === 0 && <Empty icon={Users} title="No members yet" text="Add the people who are travelling with you." />}
      {members?.length > 0 && (
        <Card className="overflow-x-auto !p-0">
          <table className="w-full min-w-[560px] text-left text-sm">
            <thead className="border-b border-slate-200 text-xs text-slate-500">
              <tr><th className="px-4 py-3 font-medium">Name</th><th className="px-4 py-3 font-medium">Type</th><th className="px-4 py-3 font-medium">Status</th><th className="px-4 py-3 font-medium">Joined</th><th className="px-4 py-3 text-right font-medium">Actions</th></tr>
            </thead>
            <tbody className="divide-y divide-slate-100">
              {members.map((m) => (
                <tr key={m.id}>
                  <td className="px-4 py-3"><span className="flex items-center gap-3"><Avatar name={m.user_name} /> {m.user_name}</span></td>
                  <td className="px-4 py-3"><Badge tone={m.user_id ? 'green' : 'orange'}>{m.user_id ? 'Registered' : 'Guest'}</Badge></td>
                  <td className="px-4 py-3"><Badge tone={m.status === 'ACTIVE' ? 'blue' : 'gray'}>{m.status === 'ACTIVE' ? 'Active' : 'Left'}</Badge></td>
                  <td className="px-4 py-3 text-slate-600">{formatDate(m.joined_at)}</td>
                  <td className="px-4 py-3 text-right">
                    {m.status === 'ACTIVE' && (
                      <button onClick={() => setRemoving(m)} aria-label={`Remove ${m.user_name}`} title="Remove from trip" className="rounded p-1.5 text-slate-400 hover:bg-red-50 hover:text-red-600 focus:outline-none focus-visible:ring-2 focus-visible:ring-blue-500">
                        <UserMinus className="h-4 w-4" />
                      </button>
                    )}
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </Card>
      )}
      {adding && <AddMemberModal tripId={trip.id} onClose={() => setAdding(false)} onAdded={() => { setAdding(false); reload(); }} />}
      {removing && <ConfirmDialog title="Remove member?" text={`${removing.user_name} will be marked as having left the trip. Their past expenses stay on record.`} confirmLabel="Remove" onConfirm={confirmRemove} onClose={() => setRemoving(null)} />}
    </div>
  );
}
