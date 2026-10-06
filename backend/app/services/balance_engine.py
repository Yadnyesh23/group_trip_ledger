from collections import defaultdict
from decimal import Decimal

TWO_PLACES = Decimal("0.01")
ZERO = Decimal("0")


class BalanceError(ValueError):
    """Raised when expense/allocation data is inconsistent."""


class BalanceEngine:
    @staticmethod
    def _to_decimal(value) -> Decimal:
        # str() avoids float artifacts, e.g. Decimal(0.1) != Decimal("0.1")
        return Decimal(str(value))

    @staticmethod
    def calculate_balances(expenses: list[dict], allocations: list[dict]) -> dict[str, Decimal]:
        """
        Returns {user_id: net_balance}.
          positive -> user should receive that amount
          negative -> user should pay that amount
        Balances always sum to exactly zero.
        """
        to_dec = BalanceEngine._to_decimal

        # 1. Group allocations by expense once (O(n + m) instead of O(n * m))
        allocs_by_expense = defaultdict(list)
        for a in allocations:
            allocs_by_expense[a["expense_id"]].append(a)

        # Catch allocations pointing to an expense that doesn't exist (e.g. a typo'd ID)
        orphans = set(allocs_by_expense) - {e["id"] for e in expenses}
        if orphans:
            raise BalanceError(f"Allocations reference unknown expense ids: {sorted(orphans)}")

        paid = defaultdict(Decimal)   # what each user actually paid out
        owed = defaultdict(Decimal)   # what each user's share of everything adds up to

        # 2. Walk each expense: credit the payer, debit every allocated user
        for expense in expenses:
            amount = to_dec(expense["amount"])
            expense_allocs = allocs_by_expense.get(expense["id"], [])

            # 3. Shares must add up to the expense total, otherwise money is created/lost
            allocated = sum((to_dec(a["amount"]) for a in expense_allocs), ZERO)
            if allocated != amount:
                raise BalanceError(
                    f"Expense '{expense['name']}' ({expense['id']}): "
                    f"allocations sum to {allocated}, expected {amount}"
                )

            paid[expense["paid_by_user_id"]] += amount
            for a in expense_allocs:
                owed[a["user_id"]] += to_dec(a["amount"])

        # 4. Net = paid - owed, for everyone who appears on either side
        users = set(paid) | set(owed)
        balances = {u: (paid[u] - owed[u]).quantize(TWO_PLACES) for u in users}

        # 5. Invariant: in a closed group, everything nets to zero
        if sum(balances.values(), ZERO) != ZERO:
            raise BalanceError("Balances do not sum to zero")

        # 6. Biggest creditor first, biggest debtor last
        return dict(sorted(balances.items(), key=lambda kv: kv[1], reverse=True))


