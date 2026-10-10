
def calculate_balance(paid: float, owed: float) -> float:
    return paid - owed


def test_member_should_receive_money():
    balance = calculate_balance(paid=1000, owed=400)

    assert balance == 600


def test_member_should_owe_money():
    balance = calculate_balance(paid=200, owed=500)

    assert balance == -300


def test_member_with_no_balance():
    balance = calculate_balance(paid=500, owed=500)

    assert balance == 0