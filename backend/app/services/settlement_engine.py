balances = [
    {"user_id": "d860b20f-8c47-4c81-ac4a-2e39b733f89d", "balance": 5000},
    {"user_id": "39390e33-5766-4487-9915-a29db8d6fbd4", "balance": 1500},
    {"user_id": "25aedaa9-1b30-43fb-b373-f8d01c957834", "balance": -2500},
    {"user_id": "ebbd4ef3-7897-49f9-85dc-b0cce34a767c", "balance": -4000},
]


class SettlementEngine:

    @staticmethod
    def settle_balances(balances: list[dict]) -> list[dict]:
        """
        Output will be like
        "Yash pays Rahul 2500"
        "Yash pays Rahul 2500"
        settlements = [
            { "payer" : "Yash", "payee" : "Rahul", "amount" : 2500 },
            { "payer" : "Yash", "payee" : "Rahul", "amount" : 2500 }
        ]
        """
        creditors = [c for c in balances if c["balance"] > 0]
        debtors = [d for d in balances if d["balance"] < 0]

        settlements = []

        while creditors and debtors:
            credit_user = max(creditors, key=lambda x: x["balance"])
            debt_user = min(debtors, key=lambda x: x["balance"])

            amount = min(credit_user["balance"], -debt_user["balance"])

            settlements.append(
                {
                    "payer": debt_user["user_id"],
                    "payee": credit_user["user_id"],
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
