from decimal import Decimal


class SettlementEngine:

    @staticmethod
    def settle_balances(balances: list[dict]) -> list[dict]:
        """
        Takes a list of dicts with "member_id" and "balance" keys.
        Returns a list of settlement suggestions:
            {"payer": <member_id>, "payee": <member_id>, "amount": <Decimal>}
        where payer is someone who owes money (negative balance)
        and payee is someone who should receive money (positive balance).
        """
        creditors = [
            {"member_id": c["member_id"], "balance": Decimal(str(c["balance"]))}
            for c in balances if Decimal(str(c["balance"])) > 0
        ]
        debtors = [
            {"member_id": d["member_id"], "balance": Decimal(str(d["balance"]))}
            for d in balances if Decimal(str(d["balance"])) < 0
        ]

        settlements = []

        while creditors and debtors:
            credit_user = max(creditors, key=lambda x: x["balance"])
            debt_user = min(debtors, key=lambda x: x["balance"])

            amount = min(credit_user["balance"], -debt_user["balance"])

            settlements.append(
                {
                    "payer": debt_user["member_id"],
                    "payee": credit_user["member_id"],
                    "amount": amount,
                }
            )

            credit_user["balance"] -= amount
            debt_user["balance"] += amount

            if credit_user["balance"] == 0:
                creditors.remove(credit_user)

            if debt_user["balance"] == 0:
                debtors.remove(debt_user)
        return settlements
