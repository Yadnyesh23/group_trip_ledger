import { ArrowRightLeft, Map as MapIcon, Receipt, Users } from 'lucide-react';
import { Link } from 'react-router-dom';
import { LinkButton, Logo } from '../components/ui';
import { useAuth } from '../context/AuthContext';
import { TempleNightScene } from '../effects/temple-night/TempleNightScene';

const features = [
  { icon: MapIcon,         title: 'Plan Your Trip',   text: 'Create and manage your trips with ease.' },
  { icon: Receipt,         title: 'Track Expenses',   text: 'Keep a record of shared expenses as they happen.' },
  { icon: ArrowRightLeft,  title: 'Settle Easily',    text: 'See balances and settle with simple transfers.' },
];

export default function Landing() {
  const { user } = useAuth();

  return (
    <div className="min-h-screen bg-white">
      {/* ── Header ───────────────────────────────────────────────────── */}
      <header className="mx-auto flex max-w-6xl items-center justify-between px-6 py-4">
        <Logo />
        <nav className="hidden gap-6 text-sm text-slate-600 sm:flex" aria-label="Sections">
          <a href="#top"      className="hover:text-blue-600">Home</a>
          <a href="#features" className="hover:text-blue-600">Features</a>
          <a href="#about"    className="hover:text-blue-600">About</a>
        </nav>
        <div className="flex items-center gap-2">
          {user ? (
            <LinkButton to="/dashboard">Dashboard</LinkButton>
          ) : (
            <>
              <Link to="/login"    className="rounded-lg px-3 py-2 text-sm font-medium text-slate-700 hover:bg-slate-100">Login</Link>
              <LinkButton to="/register">Register</LinkButton>
            </>
          )}
        </div>
      </header>

      {/* ── Hero ─────────────────────────────────────────────────────── */}
      <section
        id="top"
        className="mx-auto grid max-w-6xl items-center gap-10 px-6 py-12 md:grid-cols-2 md:py-20"
      >
        {/* Copy */}
        <div>
          <h1 className="text-4xl font-bold leading-tight text-slate-900 md:text-5xl">
            Plan Trips. Split Expenses. Travel Together.
          </h1>
          <p className="mt-4 max-w-md text-slate-600">
            GroupTrip Ledger helps you organise participants, track expenses,
            and keep your finances simple and fair.
          </p>
          <div className="mt-6 flex gap-3">
            <LinkButton to={user ? '/dashboard' : '/register'}>Get Started</LinkButton>
            <a
              href="#features"
              className="inline-flex items-center rounded-lg border border-slate-300 px-4 py-2 text-sm font-semibold text-slate-700 hover:bg-slate-50"
            >
              Learn More
            </a>
          </div>
        </div>

        {/* Three.js Temple Night hero visual */}
        <div
          className="relative rounded-2xl shadow-2xl overflow-hidden md:h-80"
          style={{ height: '18rem' }}
          aria-label="Animated night temple scene"
        >
          <TempleNightScene />

          {/* Info card overlay */}
          <div className="pointer-events-none absolute bottom-4 right-4 flex items-center gap-3 rounded-xl bg-white/80 backdrop-blur px-4 py-3 shadow-lg">
            <span className="font-semibold text-slate-800">
              Better Trips<br />Together
            </span>
            <Users className="h-9 w-9 text-blue-600" />
          </div>
        </div>
      </section>

      {/* ── Features ─────────────────────────────────────────────────── */}
      <section
        id="features"
        className="mx-auto grid max-w-6xl gap-8 px-6 py-12 text-center sm:grid-cols-3"
      >
        {features.map(({ icon: Icon, title, text }) => (
          <div key={title}>
            <span className="mx-auto flex h-12 w-12 items-center justify-center rounded-full bg-blue-50 text-blue-600">
              <Icon className="h-6 w-6" />
            </span>
            <h3 className="mt-3 font-semibold text-slate-900">{title}</h3>
            <p className="mx-auto mt-1 max-w-[16rem] text-sm text-slate-500">{text}</p>
          </div>
        ))}
      </section>

      {/* ── Footer ───────────────────────────────────────────────────── */}
      <footer id="about" className="border-t border-slate-200 py-6 text-center text-sm text-slate-500">
        GroupTrip Ledger — a trip planner and expense splitter for groups.
      </footer>
    </div>
  );
}
