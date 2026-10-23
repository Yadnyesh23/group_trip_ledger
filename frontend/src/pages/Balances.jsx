import { useOutletContext } from 'react-router-dom';
import { ArrowDownLeft, ArrowUpRight, CheckCircle2, Scale } from 'lucide-react';
import { Avatar, Card, Empty, ErrorBox, PageHeader, Spinner } from '../components/ui';
import { getBalances, getSettlements } from '../api/finance';
import { useAsync } from '../hooks/useAsync';
import { formatMoney, toCents } from '../utils/format';

// Positive balance = the member should receive money; negative = the member owes money.
export default function Balances() {
  const { trip } = useOutletContext();
  const { data, loading, error, reload } = useAsync(
    async () => {
      const [balances, settlements] = await Promise.all([getBalances(trip.id), getSettlements(trip.id)]);
      return { balances, settlements };
    },
    [trip.id],
  );

  let receive = 0;
  let pay = 0;
  data?.balances.forEach((b) => {
    const c = toCents(b.balance);
    if (c > 0) receive += c;
    else pay += -c;
  });

  const summary = [
    { label: 'Total to Receive', value: receive, icon: ArrowDownLeft, cls: 'bg-emerald-50 text-emerald-700' },
    { label: 'Total to Pay', value: pay, icon: ArrowUpRight, cls: 'bg-red-50 text-red-600' },
    { label: 'Net Balance', value: receive - pay, icon: Scale, cls: 'bg-blue-50 text-blue-700' },
  ];

  return (
    <div>
      <PageHeader title="Balances & Settlements" subtitle={trip.name} />
      {loading && <Spinner />}
      <ErrorBox message={error} onRetry={reload} />
      {data && (
        <>
          <div className="grid gap-3 sm:grid-cols-3">
            {summary.map(({ label, value, icon: Icon, cls }) => (
              <div key={label} className={`rounded-xl p-4 ${cls}`}>
                <p className="flex items-center gap-1.5 text-xs font-medium"><Icon className="h-4 w-4" aria-hidden="true" /> {label}</p>
                <p className="mt-1 text-xl font-bold">{formatMoney(value / 100)}</p>
              </div>
            ))}
          </div>

          <div className="mt-5 grid gap-4 lg:grid-cols-2">
            <Card>
              <h2 className="mb-3 font-semibold text-slate-900">Member Balances</h2>
              {data.balances.length === 0 ? <p className="text-sm text-slate-500">No balances yet. Add expenses to see who owes what.</p> : (
                <ul className="divide-y divide-slate-100">
                  {data.balances.map((b) => {
                    const c = toCents(b.balance);
                    return (
                      <li key={b.member_id} className="flex items-center gap-3 py-2.5 text-sm">
                        <Avatar name={b.member_name} />
                        <span className="flex-1">{b.member_name}</span>
                        <span className={`font-semibold ${c > 0 ? 'text-emerald-600' : c < 0 ? 'text-red-600' : 'text-slate-500'}`}>
                          {c > 0 ? '+' : c < 0 ? '−' : ''}{formatMoney(Math.abs(c) / 100)}
                        </span>
                      </li>
                    );
                  })}
                </ul>
              )}
            </Card>

            <Card>
              <h2 className="mb-1 font-semibold text-slate-900">Suggested Settlements</h2>
              <p className="mb-3 text-xs text-slate-400">Suggestions only. Nothing is recorded as paid.</p>
              {data.settlements.length === 0 ? (
                <Empty icon={CheckCircle2} title="All settled up" text="No transfers are needed right now." />
              ) : (
                <ul className="space-y-2">
                  {data.settlements.map((s, i) => (
                    <li key={`${s.payer}-${s.payee}-${i}`} className="rounded-lg border border-slate-200 p-3 text-sm">
                      <span className="font-medium">{s.payer_name}</span> pays <span className="font-medium">{s.payee_name}</span>
                      <div className="mt-0.5 text-lg font-bold text-slate-900">{formatMoney(s.amount)}</div>
                    </li>
                  ))}
                </ul>
              )}
            </Card>
          </div>
        </>
      )}
    </div>
  );
}
