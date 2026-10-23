import { useState } from 'react';
import { useOutletContext } from 'react-router-dom';
import { Calendar, Download, MapPin, Receipt, Users } from 'lucide-react';
import { Avatar, Badge, Button, Card, ErrorBox, PageHeader, Spinner } from '../components/ui';
import { downloadReportPdf, getReport } from '../api/finance';
import { useAsync } from '../hooks/useAsync';
import { errorMessage, formatDate, formatDateRange, formatMoney, toCents } from '../utils/format';

const tabs = ['Summary', 'Members', 'Expenses', 'Balances', 'Settlements'];

export default function Report() {
  const { trip } = useOutletContext();
  const { data: report, loading, error, reload } = useAsync(() => getReport(trip.id), [trip.id]);
  const [tab, setTab] = useState('Summary');
  const [downloading, setDownloading] = useState(false);
  const [pdfError, setPdfError] = useState('');

  const download = async () => {
    setDownloading(true);
    setPdfError('');
    try {
      await downloadReportPdf(trip.id);
    } catch (e) {
      // With responseType "blob", error bodies arrive as Blobs, so fall back to a generic message.
      setPdfError(e?.response?.data instanceof Blob ? `Could not download the PDF (${e.response.status}).` : errorMessage(e));
    } finally {
      setDownloading(false);
    }
  };

  const members = report?.members.members ?? [];
  const expenses = report?.expenses.expenses ?? [];
  const balances = report?.balances.balances ?? [];
  const settlements = report?.settlements.settlements ?? [];
  const totalSpent = expenses.reduce((s, e) => s + toCents(e.amount), 0) / 100;

  const th = 'px-4 py-3 font-medium';
  return (
    <div>
      <PageHeader title="Trip Report" subtitle={trip.name} action={<Button onClick={download} loading={downloading}><Download className="h-4 w-4" /> Download PDF</Button>} />
      <ErrorBox message={pdfError} />
      {loading && <Spinner />}
      <ErrorBox message={error} onRetry={reload} />
      {report && (
        <>
          <div role="tablist" className="mb-4 flex gap-1 overflow-x-auto border-b border-slate-200">
            {tabs.map((t) => (
              <button key={t} role="tab" aria-selected={tab === t} onClick={() => setTab(t)} className={`whitespace-nowrap border-b-2 px-4 py-2 text-sm font-medium ${tab === t ? 'border-blue-600 text-blue-600' : 'border-transparent text-slate-500 hover:text-slate-800'}`}>{t}</button>
            ))}
          </div>

          {tab === 'Summary' && (
            <div className="space-y-4">
              <Card>
                <h2 className="mb-3 font-semibold text-slate-900">Trip Information</h2>
                <div className="grid gap-4 sm:grid-cols-4">
                  {[[MapPin, 'Location', trip.location || '—'], [Calendar, 'Dates', formatDateRange(trip.start_date, trip.end_date)], [Receipt, 'Total Expenses', formatMoney(totalSpent)], [Users, 'Participants', members.length]].map(([Icon, label, value]) => (
                    <div key={label} className="flex items-start gap-2">
                      <Icon className="mt-0.5 h-5 w-5 text-blue-600" aria-hidden="true" />
                      <div><p className="text-xs text-slate-500">{label}</p><p className="text-sm font-semibold text-slate-800">{value}</p></div>
                    </div>
                  ))}
                </div>
              </Card>
              <div className="grid gap-4 lg:grid-cols-2">
                <Card>
                  <h2 className="mb-2 font-semibold text-slate-900">Members</h2>
                  <ul className="divide-y divide-slate-100 text-sm">
                    {members.slice(0, 5).map((m) => (
                      <li key={m.id} className="flex items-center gap-3 py-2"><Avatar name={m.user_name} /><span className="flex-1">{m.user_name}</span><Badge tone={m.user_id ? 'green' : 'orange'}>{m.user_id ? 'Registered' : 'Guest'}</Badge></li>
                    ))}
                  </ul>
                </Card>
                <Card>
                  <h2 className="mb-2 font-semibold text-slate-900">Recent Expenses</h2>
                  {expenses.length === 0 ? <p className="text-sm text-slate-500">No expenses recorded.</p> : (
                    <ul className="divide-y divide-slate-100 text-sm">
                      {[...expenses].sort((a, b) => b.expense_date.localeCompare(a.expense_date)).slice(0, 5).map((e) => (
                        <li key={e.id} className="flex items-center justify-between gap-3 py-2"><span>{e.name}<span className="block text-xs text-slate-400">{formatDate(e.expense_date)}</span></span><span className="font-medium">{formatMoney(e.amount)}</span></li>
                      ))}
                    </ul>
                  )}
                </Card>
              </div>
            </div>
          )}

          {tab === 'Members' && (
            <Card className="overflow-x-auto !p-0">
              <table className="w-full min-w-[480px] text-left text-sm"><thead className="border-b border-slate-200 text-xs text-slate-500"><tr><th className={th}>Name</th><th className={th}>Type</th><th className={th}>Status</th><th className={th}>Joined</th></tr></thead>
                <tbody className="divide-y divide-slate-100">{members.map((m) => (
                  <tr key={m.id}><td className="px-4 py-3">{m.user_name}</td><td className="px-4 py-3">{m.user_id ? 'Registered' : 'Guest'}</td><td className="px-4 py-3">{m.status === 'ACTIVE' ? 'Active' : 'Left'}</td><td className="px-4 py-3">{formatDate(m.joined_at)}</td></tr>
                ))}</tbody></table>
            </Card>
          )}

          {tab === 'Expenses' && (
            <Card className="overflow-x-auto !p-0">
              <table className="w-full min-w-[640px] text-left text-sm"><thead className="border-b border-slate-200 text-xs text-slate-500"><tr><th className={th}>Date</th><th className={th}>Description</th><th className={th}>Payer</th><th className={th}>Amount</th><th className={th}>Allocations</th></tr></thead>
                <tbody className="divide-y divide-slate-100">{expenses.map((e) => (
                  <tr key={e.id} className="align-top"><td className="px-4 py-3">{formatDate(e.expense_date)}</td><td className="px-4 py-3">{e.name}</td><td className="px-4 py-3">{e.paid_by_name}</td><td className="px-4 py-3 font-medium">{formatMoney(e.amount)}</td>
                    <td className="px-4 py-3 text-xs text-slate-600">{(e.allocations || []).map((a) => <div key={a.member_id}>{a.member_name}: {formatMoney(a.amount)}</div>)}</td></tr>
                ))}</tbody></table>
            </Card>
          )}

          {tab === 'Balances' && (
            <Card className="overflow-x-auto !p-0">
              <table className="w-full text-left text-sm"><thead className="border-b border-slate-200 text-xs text-slate-500"><tr><th className={th}>Member</th><th className={`${th} text-right`}>Balance</th></tr></thead>
                <tbody className="divide-y divide-slate-100">{balances.map((b) => {
                  const c = toCents(b.balance);
                  return <tr key={b.member_id}><td className="px-4 py-3">{b.member_name}</td><td className={`px-4 py-3 text-right font-semibold ${c > 0 ? 'text-emerald-600' : c < 0 ? 'text-red-600' : ''}`}>{c > 0 ? '+' : c < 0 ? '−' : ''}{formatMoney(Math.abs(c) / 100)}</td></tr>;
                })}</tbody></table>
            </Card>
          )}

          {tab === 'Settlements' && (
            <Card>
              {settlements.length === 0 ? <p className="text-sm text-slate-500">Everyone is settled up.</p> : (
                <ul className="divide-y divide-slate-100 text-sm">{settlements.map((s, i) => (
                  <li key={i} className="flex items-center justify-between py-2.5"><span><strong>{s.payer_name}</strong> pays <strong>{s.payee_name}</strong></span><span className="font-semibold">{formatMoney(s.amount)}</span></li>
                ))}</ul>
              )}
              <p className="mt-3 text-xs text-slate-400">Suggested transfers only. No payments are recorded.</p>
            </Card>
          )}
        </>
      )}
    </div>
  );
}
