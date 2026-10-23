import { z } from 'zod';
import { toCents } from '../utils/format';

const email = z.string().trim().min(1, 'Email is required').email('Enter a valid email address');

export const loginSchema = z.object({
  email,
  password: z.string().min(1, 'Password is required'),
  remember: z.boolean().optional(),
});

export const registerSchema = z
  .object({
    name: z.string().trim().min(1, 'Full name is required'),
    email,
    password: z.string().min(8, 'Use at least 8 characters'),
    confirm: z.string().min(1, 'Confirm your password'),
  })
  .refine((v) => v.password === v.confirm, { path: ['confirm'], message: 'Passwords do not match' });

export const tripSchema = z
  .object({
    name: z.string().trim().min(1, 'Trip name is required'),
    location: z.string().optional(),
    description: z.string().optional(),
    start_date: z.string().min(1, 'Start date is required'),
    end_date: z.string().min(1, 'End date is required'),
    is_completed: z.boolean().optional(),
  })
  .refine((v) => !v.start_date || !v.end_date || v.end_date >= v.start_date, {
    path: ['end_date'],
    message: 'End date cannot be before the start date',
  });

export const memberSchema = z.object({
  display_name: z.string().trim().min(1, 'Name is required').max(100, 'Use 100 characters or fewer'),
});

export const expenseSchema = z
  .object({
    name: z.string().trim().min(1, 'Description is required'),
    description: z.string().optional(),
    category: z.string().optional(),
    amount: z.coerce.number({ invalid_type_error: 'Enter an amount' }).gt(0, 'Amount must be greater than 0'),
    expense_date: z.string().min(1, 'Date is required'),
    paid_by_member_id: z.string().min(1, 'Select who paid'),
    split_type: z.enum(['EQUAL', 'CUSTOM']),
    participant_member_ids: z.array(z.string()).min(1, 'Select at least one participant'),
    custom_allocation: z.record(z.any()).optional(),
  })
  .superRefine((v, ctx) => {
    if (v.split_type !== 'CUSTOM') return;
    const amounts = v.participant_member_ids.map((id) => toCents(v.custom_allocation?.[id]));
    if (amounts.some((c) => !Number.isFinite(c) || c <= 0)) {
      ctx.addIssue({ code: 'custom', path: ['custom_allocation'], message: 'Enter an amount for every selected participant' });
    } else if (amounts.reduce((a, b) => a + b, 0) !== toCents(v.amount)) {
      ctx.addIssue({ code: 'custom', path: ['custom_allocation'], message: 'Custom amounts must add up to the total' });
    }
  });
