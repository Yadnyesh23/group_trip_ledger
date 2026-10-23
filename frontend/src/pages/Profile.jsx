import { useNavigate } from 'react-router-dom';
import { ChevronRight, KeyRound, LogOut } from 'lucide-react';
import { Avatar, Button, Card, Field, Input, PageHeader } from '../components/ui';
import { useAuth } from '../context/AuthContext';
import { formatDate } from '../utils/format';

// The backend only exposes GET /auth/me and logout, so profile fields are read-only.
export default function Profile() {
  const { user, logout } = useAuth();
  const navigate = useNavigate();
  const signOut = async () => {
    await logout();
    navigate('/login');
  };

  return (
    <div className="mx-auto max-w-2xl">
      <PageHeader title="Profile & Settings" />
      <Card>
        <h2 className="mb-4 font-semibold text-slate-900">User Profile</h2>
        <div className="mb-4 flex items-center gap-3">
          <Avatar name={user.name} size="h-12 w-12" />
          <div><p className="font-semibold text-slate-900">{user.name}</p><p className="text-sm text-slate-500">{user.email}</p></div>
        </div>
        <div className="grid gap-3 sm:grid-cols-2">
          <Field label="Full Name" htmlFor="p-name"><Input id="p-name" value={user.name} disabled readOnly /></Field>
          <Field label="Email Address" htmlFor="p-email"><Input id="p-email" value={user.email} disabled readOnly /></Field>
        </div>
        <p className="mt-3 text-xs text-slate-400">Member since {formatDate(user.created_at)}. Profile editing is not available in the current API.</p>
      </Card>

      <Card className="mt-4">
        <h2 className="mb-2 font-semibold text-slate-900">Account Settings</h2>
        <div className="flex items-center justify-between rounded-lg border border-slate-200 px-3 py-3 text-sm text-slate-400" aria-disabled="true">
          <span className="flex items-center gap-2"><KeyRound className="h-4 w-4" /> Change Password <span className="text-xs">(not available in the API yet)</span></span>
          <ChevronRight className="h-4 w-4" />
        </div>
      </Card>

      <Button variant="danger" onClick={signOut} className="mt-4"><LogOut className="h-4 w-4" /> Logout</Button>
    </div>
  );
}
