import { useState } from 'react';
import { useForm } from 'react-hook-form';
import { zodResolver } from '@hookform/resolvers/zod';
import { useOutletContext } from 'react-router-dom';
import { Plus, Receipt } from 'lucide-react';
import { Badge, Button, Card, Empty, ErrorBox, Field, Input, Modal, PageHeader, Select, Spinner } from '../components/ui';
import { createExpense, listExpenses } from '../api/expenses';
import { listMembers } from '../api/members';
import { useAsync } from '../hooks/useAsync';
import { expenseSchema } from '../schemas';
import { equalSplitCents, errorMessage, formatDate, formatMoney, todayISO, toCents } from '../utils/format';

const categories = ['Food', 'Stay', 'Travel', 'Activities', 'Shopping', 'Other'];

function ExpenseModal({ tripId, members, onClose, onCreated }) {
  const active = members.filter((m) => m.status === 'ACTIVE');
  const [apiError, setApiError] = useState('');
  const { register, handleSubmit, watch, setValue, formState: { errors, isSubmitting } } = useForm({
    resolver: zodResolver(expenseSchema),
    defaultValues: {
      name: '', description: '', category: '', amount: '', expense_date: todayISO(), paid_by_member_id: '',
      split_type: 'EQUAL', participant_member_ids: active.map((m) => m.id), custom_allocation: {},
    },
  });

  const splitType = watch('split_type');
  const selected = watch('participant_member_ids') || [];
  const custom = watch('custom_allocation') || {};
  const totalCents = toCents(watch('amount'));
  const validTotal = Number.isFinite(totalCents) && totalCents > 0;

  const toggle = (id) => {
    const next = selected.includes(id) ? selected.filter((x) => x !== id) : [...selected, id];
    setValue('participant_member_ids', next, { shouldValidate: true, shouldDirty: true });
  };

  // Equal split is a preview only; the server computes the real allocation.
  const shares = equalSplitCents(validTotal ? totalCents : 0, selected.length);
  const selectedInOrder = active.filter((m) => selected.includes(m.id));
  const allocatedCents = selectedInOrder.reduce((sum, m) => {
    const c = toCents(custom[m.id]);
    return sum + (Number.isFinite(c) ? c : 0);
  }, 0);
  const diffCents = splitType === 'CUSTOM' ? (validTotal ? totalCents : 0) - allocatedCents : 0;

  const submit = async (v) => {
    setApiError('');
    const payload = {
      name: v.name.trim(),
      description: v.description?.trim() || null,
      amount: v.amount,
      split_type: v.split_type,
      category: v.category || null,
      paid_by_member_id: v.paid_by_member_id,
      participant_member_ids: v.participant_member_ids,
      expense_date: v.expense_date,
    };
    if (v.split_type === 'CUSTOM') {
      payload.custom_allocation = Object.fromEntries(v.participant_member_ids.map((id) => [id, Number(v.custom_allocation[id])]));
    }
    try {
      await createExpense(tripId, payload);
      onCreated();
    } catch (e) {
      setApiError(errorMessage(e));
    }
  };

  return (
    <Modal title="Add Expense" onClose={onClose} wide>
      <form onSubmit={handleSubmit(submit)} className="space-y-3" noValidate>
        <ErrorBox message={apiError} />
        <div className="grid gap-3 sm:grid-cols-2">
          <Field label="Description" htmlFor="e-name" required error={errors.name?.message}>
            <Input id="e-name" placeholder="e.g. Hotel Booking" {...register('name')} />
          </Field>
          <Field label="Amount (₹)" htmlFor="e-amount" required error={errors.amount?.message}>
            <Input id="e-amount" type="number" step="0.01" min="0" inputMode="decimal" placeholder="Enter amount" {...register('amount')} />
          </Field>
          <Field label="Date" htmlFor="e-date" required error={errors.expense_date?.message}>
            <Input id="e-date" type="date" {...register('expense_date')} />
          </Field>
          <Field label="Payer" htmlFor="e-payer" required error={errors.paid_by_member_id?.message}>
            <Select id="e-payer" {...register('paid_by_member_id')}>
              <option value="">Select payer</option>
              {active.map((m) => <option key={m.id} value={m.id}>{m.user_name}</option>)}
            </Select>
          </Field>
          <Field label="Category" htmlFor="e-cat">
            <Select id="e-cat" {...register('category')}>
              <option value="">No category</option>
              {categories.map((c) => <option key={c}>{c}</option>)}
            </Select>
          </Field>
          <Field label="Notes" htmlFor="e-desc">
            <Input id="e-desc" placeholder="Optional" {...register('description')} />
          </Field>
        </div>

        <fieldset>
          <legend className="mb-1 text-xs font-medium text-slate-700">Participants</legend>
          <div className="mb-2 flex gap-5 text-sm">
            <label className="flex items-center gap-2"><input type="radio" value="EQUAL" {...register('split_type')} /> Equal Split</label>
            <label className="flex items-center gap-2"><input type="radio" value="CUSTOM" {...register('split_type')} /> Custom Split</label>
          </div>
          <ul className="divide-y divide-slate-100 rounded-lg border border-slate-200">
            {active.map((m) => {
              const on = selected.includes(m.id);
              const idx = selectedInOrder.findIndex((x) => x.id === m.id);
              return (
                <li key={m.id} className="flex items-center gap-3 px-3 py-2 text-sm">
                  <input id={`p-${m.id}`} type="checkbox" checked={on} onChange={() => toggle(m.id)} className="h-4 w-4 rounded border-slate-300" />
                  <label htmlFor={`p-${m.id}`} className="flex-1">{m.user_name}</label>
                  {splitType === 'CUSTOM' ? (
                    <Input aria-label={`Amount for ${m.user_name}`} type="number" step="0.01" min="0" disabled={!on} className="!w-28 !py-1 text-right" {...register(`custom_allocation.${m.id}`)} />
                  ) : (
                    <span className="text-slate-600">{on && validTotal ? formatMoney(shares[idx] / 100) : '—'}</span>
                  )}
                </li>
              );
            })}
          </ul>
          {errors.participant_member_ids && <p role="alert" className="mt-1 text-xs text-red-600">{errors.participant_member_ids.message}</p>}
          {errors.custom_allocation?.message && <p role="alert" className="mt-1 text-xs text-red-600">{errors.custom_allocation.message}</p>}
          {splitType === 'EQUAL' && <p className="mt-1 text-xs text-slate-400">Equal shares are a preview; the server calculates the final split.</p>}
        </fieldset>

        <div className="flex items-center justify-between text-sm">
          <span>Total: <strong>{formatMoney(validTotal ? totalCents / 100 : 0)}</strong></span>
          <span className={diffCents === 0 ? 'text-slate-600' : 'font-medium text-red-600'}>Difference: {formatMoney(diffCents / 100)}</span>
        </div>
        <div className="flex justify-end gap-2 pt-1">
          <Button type="button" variant="secondary" onClick={onClose} disabled={isSubmitting}>Cancel</Button>
          <Button type="submit" loading={isSubmitting}>Save Expense</Button>
        </div>
      </form>
    </Modal>
  );
}

export default function Expenses() {
  const { trip } = useOutletContext();
  const { data, loading, error, reload } = useAsync(
    async () => {
      const [expenses, members] = await Promise.all([listExpenses(trip.id), listMembers(trip.id)]);
      return { expenses: expenses.expenses, members };
    },
    [trip.id],
  );
  const [adding, setAdding] = useState(false);
  const expenses = data ? [...data.expenses].sort((a, b) => b.expense_date.localeCompare(a.expense_date)) : [];

  return (
    <div>
      <PageHeader title="Expenses" subtitle={trip.name} action={<Button onClick={() => setAdding(true)} disabled={!data}><Plus className="h-4 w-4" /> Add Expense</Button>} />
      {loading && <Spinner />}
      <ErrorBox message={error} onRetry={reload} />
      {data && expenses.length === 0 && <Empty icon={Receipt} title="No expenses yet" text="Add the first shared expense for this trip." />}
      {expenses.length > 0 && (
        <Card className="overflow-x-auto !p-0">
          <table className="w-full min-w-[600px] text-left text-sm">
            <thead className="border-b border-slate-200 text-xs text-slate-500">
              <tr><th className="px-4 py-3 font-medium">Date</th><th className="px-4 py-3 font-medium">Description</th><th className="px-4 py-3 font-medium">Payer</th><th className="px-4 py-3 font-medium">Amount</th><th className="px-4 py-3 font-medium">Split</th></tr>
            </thead>
            <tbody className="divide-y divide-slate-100">
              {expenses.map((e) => (
                <tr key={e.id}>
                  <td className="px-4 py-3 text-slate-600">{formatDate(e.expense_date)}</td>
                  <td className="px-4 py-3"><div className="font-medium text-slate-800">{e.name}</div>{e.category && <div className="text-xs text-slate-400">{e.category}</div>}</td>
                  <td className="px-4 py-3">{e.paid_by_name}</td>
                  <td className="px-4 py-3 font-medium">{formatMoney(e.amount)}</td>
                  <td className="px-4 py-3"><Badge tone={e.split_type === 'EQUAL' ? 'blue' : 'orange'}>{e.split_type === 'EQUAL' ? 'Equal' : 'Custom'}</Badge></td>
                </tr>
              ))}
            </tbody>
          </table>
        </Card>
      )}
      {adding && data && <ExpenseModal tripId={trip.id} members={data.members} onClose={() => setAdding(false)} onCreated={() => { setAdding(false); reload(); }} />}
    </div>
  );
}
