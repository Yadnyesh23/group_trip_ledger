import { useState } from 'react';
import { Link, NavLink, Outlet, useNavigate } from 'react-router-dom';
import { Info, LayoutDashboard, LogOut, Menu, Settings, User, X } from 'lucide-react';
import { Avatar, Logo } from '../components/ui';
import { useAuth } from '../context/AuthContext';

const nav = [
  { to: '/dashboard', label: 'Dashboard', icon: LayoutDashboard },
  { to: '/profile', label: 'Profile', icon: User },
  { to: '/about', label: 'About', icon: Info },
];

const linkCls = ({ isActive }) =>
  `flex items-center gap-3 rounded-lg px-3 py-2 text-sm font-medium focus:outline-none focus-visible:ring-2 focus-visible:ring-blue-500 ${
    isActive ? 'bg-blue-50 text-blue-700' : 'text-slate-600 hover:bg-slate-100'
  }`;

export default function AppLayout() {
  const { user, logout } = useAuth();
  const navigate = useNavigate();
  const [open, setOpen] = useState(false);

  const signOut = async () => {
    await logout();
    navigate('/login');
  };

  const links = (
    <nav className="flex flex-1 flex-col gap-1" aria-label="Main">
      {nav.map(({ to, label, icon: Icon }) => (
        <NavLink key={to} to={to} className={linkCls} onClick={() => setOpen(false)}>
          <Icon className="h-4 w-4" aria-hidden="true" /> {label}
        </NavLink>
      ))}
      <button onClick={signOut} className="mt-auto flex items-center gap-3 rounded-lg px-3 py-2 text-sm font-medium text-slate-600 hover:bg-slate-100 focus:outline-none focus-visible:ring-2 focus-visible:ring-blue-500">
        <LogOut className="h-4 w-4" aria-hidden="true" /> Logout
      </button>
    </nav>
  );

  return (
    <div className="min-h-screen bg-slate-50">
      <header className="sticky top-0 z-30 flex h-14 items-center justify-between border-b border-slate-200 bg-white px-4">
        <div className="flex items-center gap-3">
          <button className="md:hidden" onClick={() => setOpen(true)} aria-label="Open menu">
            <Menu className="h-5 w-5" />
          </button>
          <Logo to="/dashboard" />
        </div>
        <Link to="/profile" aria-label="Profile" title={user?.name}>
          <Avatar name={user?.name || ''} />
        </Link>
      </header>

      <div className="flex">
        <aside className="sticky top-14 hidden h-[calc(100vh-3.5rem)] w-56 shrink-0 flex-col border-r border-slate-200 bg-white p-3 md:flex">{links}</aside>

        {open && (
          <div className="fixed inset-0 z-40 md:hidden">
            <div className="absolute inset-0 bg-slate-900/50" onClick={() => setOpen(false)} />
            <aside className="relative flex h-full w-64 flex-col bg-white p-3">
              <button className="mb-2 self-end" onClick={() => setOpen(false)} aria-label="Close menu">
                <X className="h-5 w-5" />
              </button>
              {links}
            </aside>
          </div>
        )}

        <main className="min-w-0 flex-1 p-4 pb-24 md:p-6 md:pb-6">
          <Outlet />
        </main>
      </div>

      <nav className="fixed inset-x-0 bottom-0 z-30 flex border-t border-slate-200 bg-white md:hidden" aria-label="Mobile">
        {nav.map(({ to, label, icon: Icon }) => (
          <NavLink key={to} to={to} className={({ isActive }) => `flex flex-1 flex-col items-center gap-0.5 py-2 text-[11px] font-medium ${isActive ? 'text-blue-600' : 'text-slate-500'}`}>
            <Icon className="h-5 w-5" aria-hidden="true" /> {label}
          </NavLink>
        ))}
      </nav>
    </div>
  );
}
