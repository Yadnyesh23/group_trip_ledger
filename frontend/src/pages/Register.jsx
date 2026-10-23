import { useForm } from 'react-hook-form';
import { zodResolver } from '@hookform/resolvers/zod';
import { Link, useNavigate } from 'react-router-dom';
import { useState } from 'react';
import AuthLayout from '../layouts/AuthLayout';
import { Button, ErrorBox, Field, Input, PasswordInput } from '../components/ui';
import { registerUser } from '../api/auth';
import { registerSchema } from '../schemas';
import { errorMessage } from '../utils/format';
import { MountainSunriseScene } from '../effects/mountain-sunrise/MountainSunriseScene';

export default function Register() {
  const navigate = useNavigate();
  const [apiError, setApiError] = useState('');
  const { register, handleSubmit, formState: { errors, isSubmitting } } = useForm({
    resolver: zodResolver(registerSchema),
    defaultValues: { name: '', email: '', password: '', confirm: '' },
  });

  const onSubmit = async ({ name, email, password }) => {
    setApiError('');
    try {
      await registerUser({ name, email, password }); // `confirm` is frontend-only
      navigate('/login', { state: { registered: true } });
    } catch (e) {
      setApiError(errorMessage(e));
    }
  };

  return (
    <AuthLayout
      panel={<MountainSunriseScene />}
      quote={'More Trips\nLess Hassle'}
    >
      <h1 className="text-2xl font-bold text-slate-900">Create Your Account</h1>
      <p className="mb-6 mt-1 text-sm text-slate-500">Join GroupTrip Ledger and start planning your trips</p>
      <form onSubmit={handleSubmit(onSubmit)} className="space-y-4" noValidate>
        <ErrorBox message={apiError} />
        <Field label="Full Name" htmlFor="name" error={errors.name?.message}>
          <Input id="name" autoComplete="name" placeholder="Enter your name" {...register('name')} />
        </Field>
        <Field label="Email Address" htmlFor="email" error={errors.email?.message}>
          <Input id="email" type="email" autoComplete="email" placeholder="you@example.com" {...register('email')} />
        </Field>
        <Field label="Password" htmlFor="password" error={errors.password?.message}>
          <PasswordInput id="password" autoComplete="new-password" placeholder="Create a password" {...register('password')} />
        </Field>
        <Field label="Confirm Password" htmlFor="confirm" error={errors.confirm?.message}>
          <PasswordInput id="confirm" autoComplete="new-password" placeholder="Confirm your password" {...register('confirm')} />
        </Field>
        <Button type="submit" loading={isSubmitting} className="w-full">Register</Button>
      </form>
      <p className="mt-6 text-center text-xs text-slate-500">
        Already have an account? <Link to="/login" className="font-semibold text-blue-600">Login</Link>
      </p>
    </AuthLayout>
  );
}
