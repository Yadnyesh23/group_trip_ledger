import { ArrowRightLeft, Map as MapIcon, Mountain, Receipt, Users } from 'lucide-react';
import { Card, PageHeader } from '../components/ui';

const features = [
  { icon: MapIcon, title: 'Plan Your Trip', text: 'Create and manage group trips with ease — set dates, locations, and invite members.' },
  { icon: Users, title: 'Add Members', text: 'Add participants to any trip and keep track of who owes what.' },
  { icon: Receipt, title: 'Track Expenses', text: 'Log shared expenses as they happen, with flexible split options.' },
  { icon: ArrowRightLeft, title: 'Settle Balances', text: 'See who owes whom and settle up with minimal transfers.' },
];

export default function About() {
  return (
    <div className="mx-auto max-w-5xl">
      <PageHeader title="About" subtitle="Learn more about GroupTrip Ledger" />

      <Card className="mb-5">
        <div className="flex items-center gap-3 mb-3">
          <span className="flex h-10 w-10 items-center justify-center rounded-full bg-blue-50">
            <Mountain className="h-5 w-5 text-blue-600" />
          </span>
          <h2 className="text-lg font-semibold text-slate-900">GroupTrip Ledger</h2>
        </div>
        <p className="text-sm text-slate-600 leading-relaxed">
          GroupTrip Ledger is a trip planner and expense splitter for groups. It helps you organize
          participants, track shared expenses, and keep your finances simple and fair — so you can
          focus on enjoying the trip.
        </p>
      </Card>

      <h2 className="text-lg font-semibold text-slate-900 mb-3">Features</h2>
      <div className="grid gap-4 sm:grid-cols-2">
        {features.map(({ icon: Icon, title, text }) => (
          <Card key={title}>
            <div className="flex items-start gap-3">
              <span className="flex h-9 w-9 shrink-0 items-center justify-center rounded-full bg-blue-50 text-blue-600">
                <Icon className="h-4 w-4" />
              </span>
              <div>
                <h3 className="font-semibold text-slate-900">{title}</h3>
                <p className="mt-1 text-sm text-slate-500">{text}</p>
              </div>
            </div>
          </Card>
        ))}
      </div>

      <p className="mt-6 text-center text-xs text-slate-400">
        Built with React, Vite, Tailwind CSS &amp; FastAPI.
      </p>
    </div>
  );
}
