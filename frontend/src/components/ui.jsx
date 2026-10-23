import { forwardRef, useEffect, useState } from 'react';
import { Link } from 'react-router-dom';
import { AlertCircle, Eye, EyeOff, Loader2, Mountain, X } from 'lucide-react';

export function Logo({ to = '/', className = '' }) {
  return (
    <Link to={to} className={`flex items-center gap-2 font-bold text-slate-900 ${className}`}>
      <Mountain className="h-6 w-6 text-blue-600" aria-hidden="true" />
      <span>GroupTrip Ledger</span>
    </Link>
  );
}

const variants = {
  primary: 'bg-blue-600 text-white hover:bg-blue-700',
  secondary: 'border border-slate-300 bg-white text-slate-700 hover:bg-slate-50',
  danger: 'border border-red-300 bg-white text-red-600 hover:bg-red-50',
};

export function Button({ variant = 'primary', loading = false, disabled, className = '', children, ...rest }) {
  return (
    <button
      disabled={disabled || loading}
      className={`inline-flex items-center justify-center gap-2 rounded-lg px-4 py-2 text-sm font-semibold transition focus:outline-none focus-visible:ring-2 focus-visible:ring-blue-500 focus-visible:ring-offset-2 disabled:cursor-not-allowed disabled:opacity-60 ${variants[variant]} ${className}`}
      {...rest}
    >
      {loading && <Loader2 className="h-4 w-4 animate-spin" aria-hidden="true" />}
      {children}
    </button>
  );
}

export function LinkButton({ to, variant = 'primary', className = '', children }) {
  return (
    <Link
      to={to}
      className={`inline-flex items-center justify-center gap-2 rounded-lg px-4 py-2 text-sm font-semibold focus:outline-none focus-visible:ring-2 focus-visible:ring-blue-500 ${variants[variant]} ${className}`}
    >
      {children}
    </Link>
  );
}

const inputCls =
  'w-full rounded-lg border border-slate-300 bg-white px-3 py-2 text-sm text-slate-900 placeholder:text-slate-400 focus:border-blue-500 focus:outline-none focus:ring-2 focus:ring-blue-200 disabled:bg-slate-100 disabled:text-slate-500';

export const Input = forwardRef(function Input({ className = '', ...props }, ref) {
  return <input ref={ref} className={`${inputCls} ${className}`} {...props} />;
});

export const Select = forwardRef(function Select({ className = '', children, ...props }, ref) {
  return (
    <select ref={ref} className={`${inputCls} ${className}`} {...props}>
      {children}
    </select>
  );
});

export const PasswordInput = forwardRef(function PasswordInput(props, ref) {
  const [show, setShow] = useState(false);
  return (
    <div className="relative">
      <Input ref={ref} type={show ? 'text' : 'password'} className="pr-10" {...props} />
      <button
        type="button"
        onClick={() => setShow((s) => !s)}
        aria-label={show ? 'Hide password' : 'Show password'}
        className="absolute right-2 top-1/2 -translate-y-1/2 rounded p-1 text-slate-400 hover:text-slate-600 focus:outline-none focus-visible:ring-2 focus-visible:ring-blue-500"
      >
        {show ? <EyeOff className="h-4 w-4" /> : <Eye className="h-4 w-4" />}
      </button>
    </div>
  );
});

export function Field({ label, htmlFor, error, required, children }) {
  return (
    <div>
      <label htmlFor={htmlFor} className="mb-1 block text-xs font-medium text-slate-700">
        {label}
        {required && <span className="text-red-500"> *</span>}
      </label>
      {children}
      {error && (
        <p role="alert" className="mt-1 text-xs text-red-600">
          {error}
        </p>
      )}
    </div>
  );
}

export const Card = ({ className = '', children }) => (
  <div className={`rounded-xl border border-slate-200 bg-white p-5 shadow-sm ${className}`}>{children}</div>
);

const tones = {
  green: 'bg-emerald-50 text-emerald-700',
  blue: 'bg-blue-50 text-blue-700',
  orange: 'bg-orange-50 text-orange-700',
  gray: 'bg-slate-100 text-slate-600',
  red: 'bg-red-50 text-red-600',
};
export const Badge = ({ tone = 'gray', children }) => (
  <span className={`inline-block rounded-full px-2.5 py-0.5 text-xs font-medium ${tones[tone]}`}>{children}</span>
);

export const Avatar = ({ name, size = 'h-8 w-8' }) => {
  const letters = name.split(' ').filter(Boolean).slice(0, 2).map((p) => p[0].toUpperCase()).join('') || '?';
  return (
    <span className={`flex ${size} shrink-0 items-center justify-center rounded-full bg-blue-100 text-xs font-semibold text-blue-700`} aria-hidden="true">
      {letters}
    </span>
  );
};

export function Spinner({ full = false }) {
  return (
    <div className={`flex items-center justify-center ${full ? 'min-h-screen' : 'py-16'}`} role="status" aria-label="Loading">
      <Loader2 className="h-7 w-7 animate-spin text-blue-600" />
    </div>
  );
}

export function ErrorBox({ message, onRetry }) {
  if (!message) return null;
  return (
    <div role="alert" className="flex items-start gap-2 rounded-lg border border-red-200 bg-red-50 p-3 text-sm text-red-700">
      <AlertCircle className="mt-0.5 h-4 w-4 shrink-0" aria-hidden="true" />
      <div className="flex-1">{message}</div>
      {onRetry && (
        <button onClick={onRetry} className="font-semibold underline">
          Retry
        </button>
      )}
    </div>
  );
}

export function Empty({ icon: Icon, title, text, children }) {
  return (
    <div className="flex flex-col items-center rounded-xl border border-dashed border-slate-300 bg-white px-6 py-12 text-center">
      {Icon && <Icon className="mb-3 h-10 w-10 text-slate-300" aria-hidden="true" />}
      <h3 className="font-semibold text-slate-800">{title}</h3>
      {text && <p className="mt-1 max-w-sm text-sm text-slate-500">{text}</p>}
      {children && <div className="mt-4">{children}</div>}
    </div>
  );
}

export function Modal({ title, onClose, children, wide = false }) {
  useEffect(() => {
    const onKey = (e) => e.key === 'Escape' && onClose();
    document.addEventListener('keydown', onKey);
    return () => document.removeEventListener('keydown', onKey);
  }, [onClose]);

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center bg-slate-900/50 p-4" onMouseDown={(e) => e.target === e.currentTarget && onClose()}>
      <div role="dialog" aria-modal="true" aria-label={title} className={`max-h-[92vh] w-full overflow-y-auto rounded-xl bg-white p-5 shadow-xl ${wide ? 'max-w-lg' : 'max-w-md'}`}>
        <div className="mb-4 flex items-center justify-between">
          <h2 className="text-base font-semibold text-slate-900">{title}</h2>
          <button onClick={onClose} aria-label="Close" className="rounded p-1 text-slate-400 hover:text-slate-700 focus:outline-none focus-visible:ring-2 focus-visible:ring-blue-500">
            <X className="h-5 w-5" />
          </button>
        </div>
        {children}
      </div>
    </div>
  );
}

export function ConfirmDialog({ title, text, confirmLabel = 'Confirm', onConfirm, onClose }) {
  const [busy, setBusy] = useState(false);
  const [error, setError] = useState('');
  const run = async () => {
    setBusy(true);
    setError('');
    try {
      await onConfirm();
    } catch (e) {
      setError(e.message || 'Something went wrong.');
      setBusy(false);
    }
  };
  return (
    <Modal title={title} onClose={onClose}>
      <p className="text-sm text-slate-600">{text}</p>
      {error && <div className="mt-3"><ErrorBox message={error} /></div>}
      <div className="mt-5 flex justify-end gap-2">
        <Button variant="secondary" onClick={onClose} disabled={busy}>Cancel</Button>
        <Button variant="danger" loading={busy} onClick={run}>{confirmLabel}</Button>
      </div>
    </Modal>
  );
}

// Page heading used by Members / Expenses / Balances etc.
export const PageHeader = ({ title, subtitle, action }) => (
  <div className="mb-5 flex flex-wrap items-start justify-between gap-3">
    <div>
      <h1 className="text-xl font-bold text-slate-900">{title}</h1>
      {subtitle && <p className="text-sm text-slate-500">{subtitle}</p>}
    </div>
    {action}
  </div>
);

// Gradient stand-ins for the photo covers in the design (no stock photos are bundled).
const covers = [
  'from-sky-400 via-cyan-500 to-emerald-500',
  'from-indigo-400 via-sky-500 to-teal-400',
  'from-orange-300 via-rose-400 to-amber-500',
  'from-emerald-400 via-teal-500 to-blue-500',
];
export const coverFor = (id = '') => covers[[...id].reduce((a, c) => a + c.charCodeAt(0), 0) % covers.length];
