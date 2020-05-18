from app.helpers.general import represents_an_int


def test_represents_an_int_returns_true_if_int():
    assert represents_an_int("1234a") == False
    assert represents_an_int("1234") == True
