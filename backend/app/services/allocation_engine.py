from uuid import UUID
from decimal import Decimal, ROUND_DOWN

from app.models.expenses import SplitType


class AllocationEngine:

    @staticmethod
    def calculate(
        expense_amount: Decimal,
        split_type: SplitType,
        participant_user_ids: list[UUID],
        custom_allocation: dict[UUID, Decimal] | None = None,
    ) -> dict[UUID, Decimal]:

        # -------------------------
        # 1. Basic validation
        # -------------------------
        if not participant_user_ids:
            raise ValueError("At least one participant is required")

        if len(participant_user_ids) != len(set(participant_user_ids)):
            raise ValueError("Duplicate participants are not allowed")

        if expense_amount <= 0:
            raise ValueError("Expense amount must be greater than zero")

        # -------------------------
        # 2. EQUAL split
        # -------------------------
        if split_type == SplitType.EQUAL:

            total_participants = len(participant_user_ids)

            # Calculate base amount to 2 decimal places
            total_cents = int(
                (expense_amount * 100).quantize(
                    Decimal("1"),
                    rounding=ROUND_DOWN
                )
            )

            base_cents = total_cents // total_participants
            remainder_cents = total_cents % total_participants

            allocation = {}

            for index, participant_id in enumerate(participant_user_ids):

                cents = base_cents

                # Distribute remaining cents
                if index < remainder_cents:
                    cents += 1

                allocation[participant_id] = (
                    Decimal(cents) / Decimal("100")
                )

            return allocation

        # -------------------------
        # 3. CUSTOM split
        # -------------------------
        if split_type == SplitType.CUSTOM:

            if custom_allocation is None:
                raise ValueError(
                    "Custom allocation is required for CUSTOM split"
                )

            # Check that every participant has an allocation
            if set(custom_allocation.keys()) != set(participant_user_ids):
                raise ValueError(
                    "Custom allocation must contain exactly the participants"
                )

            # Check individual amounts
            for user_id, amount in custom_allocation.items():

                if amount < 0:
                    raise ValueError(
                        f"Allocation cannot be negative for user {user_id}"
                    )

            # Check total
            custom_total = sum(
                custom_allocation.values(),
                Decimal("0")
            )

            if custom_total != expense_amount:
                raise ValueError(
                    "Custom allocation total must equal expense amount"
                )

            return custom_allocation

        # -------------------------
        # 4. Invalid split type
        # -------------------------
        raise ValueError(
            f"Unsupported split type: {split_type}"
        )