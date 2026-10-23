import { useForm } from 'react-hook-form';
import { zodResolver } from '@hookform/resolvers/zod';
import { useState } from 'react';
import { Button, ErrorBox, Field, Input } from './ui';
import { tripSchema } from '../schemas';
import { errorMessage } from '../utils/format';

// Used for both "Create trip" and "Edit trip". `onSubmit` receives the API payload.
export default function TripForm({ defaults, onSubmit, submitLabel, onCancel, showCompleted = false }) {
  const [apiError, setApiError] = useState('');
  const { register, handleSubmit, formState: { errors, isSubmitting } } = useForm({
    resolver: zodResolver(tripSchema),
    defaultValues: { name: '', location: '', description: '', start_date: '', end_date: '', is_completed: false, ...defaults },
  });

  const submit = async (v) => {
    setApiError('');
    const payload = {
      name: v.name.trim(),
      location: v.location?.trim() || null,
      description: v.description?.trim() || null,
      start_date: v.start_date,
      end_date: v.end_date,
    };
    if (showCompleted) payload.is_completed = Boolean(v.is_completed);
    try {
      await onSubmit(payload);
    } catch (e) {
      setApiError(errorMessage(e));
    }
  };

  return (
    <form onSubmit={handleSubmit(submit)} className="space-y-3" noValidate>
      <ErrorBox message={apiError} />
      <Field label="Trip name" htmlFor="t-name" required error={errors.name?.message}>
        <Input id="t-name" placeholder="e.g. Goa Trip" {...register('name')} />
      </Field>
      <Field label="Location" htmlFor="t-loc">
        <Input id="t-loc" placeholder="Goa, India" {...register('location')} />
      </Field>
      <div className="grid grid-cols-2 gap-3">
        <Field label="Start date" htmlFor="t-start" required error={errors.start_date?.message}>
          <Input id="t-start" type="date" {...register('start_date')} />
        </Field>
        <Field label="End date" htmlFor="t-end" required error={errors.end_date?.message}>
          <Input id="t-end" type="date" {...register('end_date')} />
        </Field>
      </div>
      <Field label="Description" htmlFor="t-desc">
        <textarea id="t-desc" rows={3} className="w-full rounded-lg border border-slate-300 px-3 py-2 text-sm focus:border-blue-500 focus:outline-none focus:ring-2 focus:ring-blue-200" {...register('description')} />
      </Field>
      {showCompleted && (
        <label className="flex items-center gap-2 text-sm text-slate-700">
          <input type="checkbox" className="h-4 w-4 rounded border-slate-300" {...register('is_completed')} /> Mark trip as completed
        </label>
      )}
      <div className="flex justify-end gap-2 pt-2">
        <Button type="button" variant="secondary" onClick={onCancel} disabled={isSubmitting}>Cancel</Button>
        <Button type="submit" loading={isSubmitting}>{submitLabel}</Button>
      </div>
    </form>
  );
}
