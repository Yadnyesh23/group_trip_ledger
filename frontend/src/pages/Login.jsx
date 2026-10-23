import { useForm } from 'react-hook-form';
import { zodResolver } from '@hookform/resolvers/zod';
import { Link, Navigate, useLocation, useNavigate } from 'react-router-dom';
import { useState } from 'react';
import AuthLayout from '../layouts/AuthLayout';
import { Button, ErrorBox, Field, Input, PasswordInput } from '../components/ui';
import { useAuth } from '../context/AuthContext';
import { loginSchema } from '../schemas';
import { errorMessage } from '../utils/format';
import { TempleNightScene } from '../effects/temple-night/TempleNightScene';

export default function Login() {
  const { user, login } = useAuth();
  const navigate = useNavigate();
  const location = useLocation();
  const [apiError, setApiError] = useState('');

  const {
    register,
    handleSubmit,
    formState: { errors, isSubmitting },
  } = useForm({
    resolver: zodResolver(loginSchema),
    defaultValues: {
      email: '',
      password: '',
      remember: true,
    },
  });

  if (user) return <Navigate to="/dashboard" replace />;

  const onSubmit = async (values) => {
    setApiError('');

    try {
      await login(values);
      navigate(location.state?.from || '/dashboard', {
        replace: true,
      });
    } catch (e) {
      setApiError(errorMessage(e));
    }
  };

  return (
    <AuthLayout
      panel={<TempleNightScene />}
      quote={'Good Trips\nBetter Memories\nShared Finances'}
    >

      <h1 className="text-2xl font-bold text-slate-900">
        Welcome Back
      </h1>

      <p className="mb-6 mt-1 text-sm text-slate-500">
        Sign in to your account to continue
      </p>

      {location.state?.registered && (
        <div
          className="mb-4 rounded-lg bg-emerald-50 p-3 text-sm text-emerald-700"
          role="status"
        >
          Account created. Please sign in.
        </div>
      )}

      <form
        onSubmit={handleSubmit(onSubmit)}
        className="space-y-4"
        noValidate
      >
        <ErrorBox message={apiError} />

        <Field
          label="Email Address"
          htmlFor="email"
          error={errors.email?.message}
        >
          <Input
            id="email"
            type="email"
            autoComplete="email"
            placeholder="you@example.com"
            {...register('email')}
          />
        </Field>

        <Field
          label="Password"
          htmlFor="password"
          error={errors.password?.message}
        >
          <PasswordInput
            id="password"
            autoComplete="current-password"
            placeholder="Enter your password"
            {...register('password')}
          />
        </Field>

        <label className="flex items-center gap-2 text-xs text-slate-600">
          <input
            type="checkbox"
            className="h-4 w-4 rounded border-slate-300 text-blue-600"
            {...register('remember')}
          />
          Remember me
        </label>

        <Button
          type="submit"
          loading={isSubmitting}
          className="w-full"
        >
          Login
        </Button>
      </form>

      <p className="mt-6 text-center text-xs text-slate-500">
        Don&apos;t have an account?{' '}
        <Link
          to="/register"
          className="font-semibold text-blue-600"
        >
          Register
        </Link>
      </p>
    </AuthLayout>
  );
}
