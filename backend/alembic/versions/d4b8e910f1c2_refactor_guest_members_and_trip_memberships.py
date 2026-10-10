"""refactor guest members and trip memberships

Revision ID: d4b8e910f1c2
Revises: 7be6688b9486
Create Date: 2026-10-10 11:00:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'd4b8e910f1c2'
down_revision: Union[str, Sequence[str], None] = '7be6688b9486'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """
    Data-preserving upgrade to guest-member architecture:
    1. Schema changes to trip_members (user_id nullable, add display_name).
    2. Add new nullable member-ID columns to financial tables.
    3. Validate pre-existing data integrity (orphaned user_id or cross-trip references).
    4. Deterministically provision missing trip memberships for registered users.
    5. Backfill member-ID columns from trip_members based on (trip_id, user_id).
    6. Validate 100% backfill coverage and trip-boundary integrity.
    7. Apply NOT NULL, foreign key, and check constraints to new member-ID columns.
    8. Drop obsolete user-ID columns and foreign keys.
    """
    bind = op.get_bind()

    # ------------------------------------------------------------------------
    # STEP 1: Pre-migration Data Integrity Audit (Fail-Fast Validation)
    # ------------------------------------------------------------------------

    # Check for invalid/orphaned user_id in expenses
    orphaned_exp_users = bind.execute(sa.text("""
        SELECT COUNT(*) FROM expenses e
        LEFT JOIN users u ON u.id = e.paid_by_user_id
        WHERE u.id IS NULL
    """)).scalar()
    if orphaned_exp_users > 0:
        raise RuntimeError(f"Pre-migration Check Failed: {orphaned_exp_users} expenses reference non-existent user_ids")

    # Check for invalid/orphaned user_id in expense_participants
    orphaned_part_users = bind.execute(sa.text("""
        SELECT COUNT(*) FROM expense_participants ep
        LEFT JOIN users u ON u.id = ep.user_id
        WHERE u.id IS NULL
    """)).scalar()
    if orphaned_part_users > 0:
        raise RuntimeError(f"Pre-migration Check Failed: {orphaned_part_users} expense_participants reference non-existent user_ids")

    # Check for invalid/orphaned user_id in expense_allocations
    orphaned_alloc_users = bind.execute(sa.text("""
        SELECT COUNT(*) FROM expense_allocations ea
        LEFT JOIN users u ON u.id = ea.user_id
        WHERE u.id IS NULL
    """)).scalar()
    if orphaned_alloc_users > 0:
        raise RuntimeError(f"Pre-migration Check Failed: {orphaned_alloc_users} expense_allocations reference non-existent user_ids")

    # Check for invalid/orphaned user_id in payments
    orphaned_pay_users = bind.execute(sa.text("""
        SELECT COUNT(*) FROM payments p
        LEFT JOIN users u_from ON u_from.id = p.from_user_id
        LEFT JOIN users u_to ON u_to.id = p.to_user_id
        WHERE u_from.id IS NULL OR u_to.id IS NULL
    """)).scalar()
    if orphaned_pay_users > 0:
        raise RuntimeError(f"Pre-migration Check Failed: {orphaned_pay_users} payments reference non-existent user_ids")

    # ------------------------------------------------------------------------
    # STEP 2: Schema Modifications (Add Columns & Relax Constraints)
    # ------------------------------------------------------------------------
    op.alter_column('trip_members', 'user_id', existing_type=sa.UUID(), nullable=True)
    op.add_column('trip_members', sa.Column('display_name', sa.String(length=100), nullable=True))

    op.add_column('expenses', sa.Column('paid_by_member_id', sa.UUID(), nullable=True))
    op.add_column('expense_participants', sa.Column('trip_member_id', sa.UUID(), nullable=True))
    op.add_column('expense_allocations', sa.Column('trip_member_id', sa.UUID(), nullable=True))
    op.add_column('payments', sa.Column('from_member_id', sa.UUID(), nullable=True))
    op.add_column('payments', sa.Column('to_member_id', sa.UUID(), nullable=True))

    # ------------------------------------------------------------------------
    # STEP 3: Safe & Deterministic Provisioning of Missing Memberships
    # ------------------------------------------------------------------------

    # A) Provision memberships for trip owners
    bind.execute(sa.text("""
        INSERT INTO trip_members (id, trip_id, user_id, joined_at, status, created_at, updated_at)
        SELECT gen_random_uuid(), t.id, t.owner_id, CURRENT_DATE, 'ACTIVE', NOW(), NOW()
        FROM trips t
        WHERE NOT EXISTS (
            SELECT 1 FROM trip_members tm WHERE tm.trip_id = t.id AND tm.user_id = t.owner_id
        )
    """))

    # B) Provision memberships for expense payers
    bind.execute(sa.text("""
        INSERT INTO trip_members (id, trip_id, user_id, joined_at, status, created_at, updated_at)
        SELECT gen_random_uuid(), sub.trip_id, sub.paid_by_user_id, CURRENT_DATE, 'ACTIVE', NOW(), NOW()
        FROM (SELECT DISTINCT trip_id, paid_by_user_id FROM expenses) sub
        WHERE NOT EXISTS (
            SELECT 1 FROM trip_members tm WHERE tm.trip_id = sub.trip_id AND tm.user_id = sub.paid_by_user_id
        )
    """))

    # C) Provision memberships for expense participants
    bind.execute(sa.text("""
        INSERT INTO trip_members (id, trip_id, user_id, joined_at, status, created_at, updated_at)
        SELECT gen_random_uuid(), sub.trip_id, sub.user_id, CURRENT_DATE, 'ACTIVE', NOW(), NOW()
        FROM (
            SELECT DISTINCT e.trip_id, ep.user_id
            FROM expense_participants ep
            JOIN expenses e ON e.id = ep.expense_id
        ) sub
        WHERE NOT EXISTS (
            SELECT 1 FROM trip_members tm WHERE tm.trip_id = sub.trip_id AND tm.user_id = sub.user_id
        )
    """))

    # D) Provision memberships for expense allocation recipients
    bind.execute(sa.text("""
        INSERT INTO trip_members (id, trip_id, user_id, joined_at, status, created_at, updated_at)
        SELECT gen_random_uuid(), sub.trip_id, sub.user_id, CURRENT_DATE, 'ACTIVE', NOW(), NOW()
        FROM (
            SELECT DISTINCT e.trip_id, ea.user_id
            FROM expense_allocations ea
            JOIN expenses e ON e.id = ea.expense_id
        ) sub
        WHERE NOT EXISTS (
            SELECT 1 FROM trip_members tm WHERE tm.trip_id = sub.trip_id AND tm.user_id = sub.user_id
        )
    """))

    # E) Provision memberships for payment senders and receivers
    bind.execute(sa.text("""
        INSERT INTO trip_members (id, trip_id, user_id, joined_at, status, created_at, updated_at)
        SELECT gen_random_uuid(), sub.trip_id, sub.user_id, CURRENT_DATE, 'ACTIVE', NOW(), NOW()
        FROM (
            SELECT DISTINCT trip_id, from_user_id AS user_id FROM payments
            UNION
            SELECT DISTINCT trip_id, to_user_id AS user_id FROM payments
        ) sub
        WHERE NOT EXISTS (
            SELECT 1 FROM trip_members tm WHERE tm.trip_id = sub.trip_id AND tm.user_id = sub.user_id
        )
    """))

    # ------------------------------------------------------------------------
    # STEP 4: Backfill Financial Table Foreign Keys
    # ------------------------------------------------------------------------

    # A) Expenses paid_by_member_id
    bind.execute(sa.text("""
        UPDATE expenses e
        SET paid_by_member_id = tm.id
        FROM trip_members tm
        WHERE tm.trip_id = e.trip_id AND tm.user_id = e.paid_by_user_id
    """))

    # B) Expense participants trip_member_id
    bind.execute(sa.text("""
        UPDATE expense_participants ep
        SET trip_member_id = tm.id
        FROM expenses e
        JOIN trip_members tm ON tm.trip_id = e.trip_id
        WHERE ep.expense_id = e.id AND tm.user_id = ep.user_id
    """))

    # C) Expense allocations trip_member_id
    bind.execute(sa.text("""
        UPDATE expense_allocations ea
        SET trip_member_id = tm.id
        FROM expenses e
        JOIN trip_members tm ON tm.trip_id = e.trip_id
        WHERE ea.expense_id = e.id AND tm.user_id = ea.user_id
    """))

    # D) Payments from_member_id and to_member_id
    bind.execute(sa.text("""
        UPDATE payments p
        SET from_member_id = tm_from.id,
            to_member_id = tm_to.id
        FROM trip_members tm_from, trip_members tm_to
        WHERE tm_from.trip_id = p.trip_id AND tm_from.user_id = p.from_user_id
          AND tm_to.trip_id = p.trip_id AND tm_to.user_id = p.to_user_id
    """))

    # ------------------------------------------------------------------------
    # STEP 5: Migration-time Validation & Trip Boundary Checks
    # ------------------------------------------------------------------------

    # 1. Unmapped expenses check
    unmapped_exp = bind.execute(sa.text("SELECT COUNT(*) FROM expenses WHERE paid_by_member_id IS NULL")).scalar()
    if unmapped_exp > 0:
        raise RuntimeError(f"Backfill Failed: {unmapped_exp} expenses could not be mapped to paid_by_member_id")

    # 2. Unmapped expense_participants check
    unmapped_part = bind.execute(sa.text("SELECT COUNT(*) FROM expense_participants WHERE trip_member_id IS NULL")).scalar()
    if unmapped_part > 0:
        raise RuntimeError(f"Backfill Failed: {unmapped_part} expense_participants could not be mapped to trip_member_id")

    # 3. Unmapped expense_allocations check
    unmapped_alloc = bind.execute(sa.text("SELECT COUNT(*) FROM expense_allocations WHERE trip_member_id IS NULL")).scalar()
    if unmapped_alloc > 0:
        raise RuntimeError(f"Backfill Failed: {unmapped_alloc} expense_allocations could not be mapped to trip_member_id")

    # 4. Unmapped payments check
    unmapped_pay = bind.execute(sa.text("SELECT COUNT(*) FROM payments WHERE from_member_id IS NULL OR to_member_id IS NULL")).scalar()
    if unmapped_pay > 0:
        raise RuntimeError(f"Backfill Failed: {unmapped_pay} payments could not be mapped to from_member_id/to_member_id")

    # 5. Cross-trip boundary check for expenses
    cross_trip_exp = bind.execute(sa.text("""
        SELECT COUNT(*)
        FROM expenses e
        JOIN trip_members tm ON e.paid_by_member_id = tm.id
        WHERE e.trip_id != tm.trip_id
    """)).scalar()
    if cross_trip_exp > 0:
        raise RuntimeError(f"Trip Boundary Violation: {cross_trip_exp} expenses mapped to a member from a different trip")

    # 6. Cross-trip boundary check for expense_participants
    cross_trip_part = bind.execute(sa.text("""
        SELECT COUNT(*)
        FROM expense_participants ep
        JOIN expenses e ON ep.expense_id = e.id
        JOIN trip_members tm ON ep.trip_member_id = tm.id
        WHERE e.trip_id != tm.trip_id
    """)).scalar()
    if cross_trip_part > 0:
        raise RuntimeError(f"Trip Boundary Violation: {cross_trip_part} expense_participants mapped to a member from a different trip")

    # 7. Cross-trip boundary check for expense_allocations
    cross_trip_alloc = bind.execute(sa.text("""
        SELECT COUNT(*)
        FROM expense_allocations ea
        JOIN expenses e ON ea.expense_id = e.id
        JOIN trip_members tm ON ea.trip_member_id = tm.id
        WHERE e.trip_id != tm.trip_id
    """)).scalar()
    if cross_trip_alloc > 0:
        raise RuntimeError(f"Trip Boundary Violation: {cross_trip_alloc} expense_allocations mapped to a member from a different trip")

    # 8. Cross-trip boundary check for payments
    cross_trip_pay = bind.execute(sa.text("""
        SELECT COUNT(*)
        FROM payments p
        JOIN trip_members tm_f ON p.from_member_id = tm_f.id
        JOIN trip_members tm_t ON p.to_member_id = tm_t.id
        WHERE p.trip_id != tm_f.trip_id OR p.trip_id != tm_t.trip_id
    """)).scalar()
    if cross_trip_pay > 0:
        raise RuntimeError(f"Trip Boundary Violation: {cross_trip_pay} payments mapped to a member from a different trip")

    # ------------------------------------------------------------------------
    # STEP 6: Apply NOT NULL & Constraints to New Columns
    # ------------------------------------------------------------------------

    # Expenses
    op.alter_column('expenses', 'paid_by_member_id', existing_type=sa.UUID(), nullable=False)
    op.create_foreign_key('fk_expenses_paid_by_member_id', 'expenses', 'trip_members', ['paid_by_member_id'], ['id'])

    # Expense Participants
    op.alter_column('expense_participants', 'trip_member_id', existing_type=sa.UUID(), nullable=False)
    op.create_foreign_key('fk_expense_participants_trip_member_id', 'expense_participants', 'trip_members', ['trip_member_id'], ['id'])

    # Expense Allocations
    op.alter_column('expense_allocations', 'trip_member_id', existing_type=sa.UUID(), nullable=False)
    op.create_foreign_key('fk_expense_allocations_trip_member_id', 'expense_allocations', 'trip_members', ['trip_member_id'], ['id'])

    # Payments
    op.alter_column('payments', 'from_member_id', existing_type=sa.UUID(), nullable=False)
    op.alter_column('payments', 'to_member_id', existing_type=sa.UUID(), nullable=False)
    op.create_foreign_key('fk_payments_from_member_id', 'payments', 'trip_members', ['from_member_id'], ['id'])
    op.create_foreign_key('fk_payments_to_member_id', 'payments', 'trip_members', ['to_member_id'], ['id'])

    op.create_check_constraint('ck_payment_amount_positive', 'payments', sa.text('amount > 0'))
    op.create_check_constraint('ck_payment_different_members', 'payments', sa.text('from_member_id != to_member_id'))

    # ------------------------------------------------------------------------
    # STEP 7: Drop Obsolete Foreign Keys & User Columns
    # ------------------------------------------------------------------------
    op.drop_constraint('expenses_paid_by_user_id_fkey', 'expenses', type_='foreignkey')
    op.drop_column('expenses', 'paid_by_user_id')

    op.drop_constraint('expense_participants_user_id_fkey', 'expense_participants', type_='foreignkey')
    op.drop_column('expense_participants', 'user_id')

    op.drop_constraint('expense_allocations_user_id_fkey', 'expense_allocations', type_='foreignkey')
    op.drop_column('expense_allocations', 'user_id')

    op.drop_constraint('payments_from_user_id_fkey', 'payments', type_='foreignkey')
    op.drop_constraint('payments_to_user_id_fkey', 'payments', type_='foreignkey')
    op.drop_column('payments', 'from_user_id')
    op.drop_column('payments', 'to_user_id')


def downgrade() -> None:
    """
    Downgrade procedure.
    CRITICAL: Downgrading is only possible if NO guest members (user_id IS NULL) exist.
    If guest members exist, the downgrade will abort to prevent silent data corruption/loss.
    """
    bind = op.get_bind()

    # Refuse downgrade if guest members exist
    guest_count = bind.execute(sa.text("SELECT COUNT(*) FROM trip_members WHERE user_id IS NULL")).scalar()
    if guest_count > 0:
        raise RuntimeError(
            f"Downgrade Refused: Found {guest_count} guest member(s) with user_id=NULL. "
            "The old schema requires non-null registered user IDs for all financial records and memberships. "
            "Downgrading with guest records would cause data loss."
        )

    # 1. Re-add obsolete user FK columns
    op.add_column('payments', sa.Column('to_user_id', sa.UUID(), nullable=True))
    op.add_column('payments', sa.Column('from_user_id', sa.UUID(), nullable=True))
    op.add_column('expense_allocations', sa.Column('user_id', sa.UUID(), nullable=True))
    op.add_column('expense_participants', sa.Column('user_id', sa.UUID(), nullable=True))
    op.add_column('expenses', sa.Column('paid_by_user_id', sa.UUID(), nullable=True))

    # 2. Restore user_id values from trip_members
    bind.execute(sa.text("""
        UPDATE expenses e SET paid_by_user_id = tm.user_id
        FROM trip_members tm WHERE tm.id = e.paid_by_member_id;
    """))

    bind.execute(sa.text("""
        UPDATE expense_participants ep SET user_id = tm.user_id
        FROM trip_members tm WHERE tm.id = ep.trip_member_id;
    """))

    bind.execute(sa.text("""
        UPDATE expense_allocations ea SET user_id = tm.user_id
        FROM trip_members tm WHERE tm.id = ea.trip_member_id;
    """))

    bind.execute(sa.text("""
        UPDATE payments p SET from_user_id = tm_f.user_id, to_user_id = tm_t.user_id
        FROM trip_members tm_f, trip_members tm_t
        WHERE tm_f.id = p.from_member_id AND tm_t.id = p.to_member_id;
    """))

    # 3. Re-enforce NOT NULL and old foreign keys
    op.alter_column('expenses', 'paid_by_user_id', existing_type=sa.UUID(), nullable=False)
    op.create_foreign_key('expenses_paid_by_user_id_fkey', 'expenses', 'users', ['paid_by_user_id'], ['id'])

    op.alter_column('expense_participants', 'user_id', existing_type=sa.UUID(), nullable=False)
    op.create_foreign_key('expense_participants_user_id_fkey', 'expense_participants', 'users', ['user_id'], ['id'])

    op.alter_column('expense_allocations', 'user_id', existing_type=sa.UUID(), nullable=False)
    op.create_foreign_key('expense_allocations_user_id_fkey', 'expense_allocations', 'users', ['user_id'], ['id'])

    op.alter_column('payments', 'from_user_id', existing_type=sa.UUID(), nullable=False)
    op.alter_column('payments', 'to_user_id', existing_type=sa.UUID(), nullable=False)
    op.create_foreign_key('payments_from_user_id_fkey', 'payments', 'users', ['from_user_id'], ['id'])
    op.create_foreign_key('payments_to_user_id_fkey', 'payments', 'users', ['to_user_id'], ['id'])

    # 4. Drop member columns and constraints
    op.drop_constraint('ck_payment_different_members', 'payments', type_='check')
    op.drop_constraint('ck_payment_amount_positive', 'payments', type_='check')

    op.drop_constraint('fk_payments_to_member_id', 'payments', type_='foreignkey')
    op.drop_constraint('fk_payments_from_member_id', 'payments', type_='foreignkey')
    op.drop_column('payments', 'to_member_id')
    op.drop_column('payments', 'from_member_id')

    op.drop_constraint('fk_expense_allocations_trip_member_id', 'expense_allocations', type_='foreignkey')
    op.drop_column('expense_allocations', 'trip_member_id')

    op.drop_constraint('fk_expense_participants_trip_member_id', 'expense_participants', type_='foreignkey')
    op.drop_column('expense_participants', 'trip_member_id')

    op.drop_constraint('fk_expenses_paid_by_member_id', 'expenses', type_='foreignkey')
    op.drop_column('expenses', 'paid_by_member_id')

    # 5. Restore trip_members schema
    op.drop_column('trip_members', 'display_name')
    op.alter_column('trip_members', 'user_id', existing_type=sa.UUID(), nullable=False)
