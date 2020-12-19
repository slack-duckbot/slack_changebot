from app.helpers.slack import is_change_channel
from app.helpers.slack import get_change_number_from_channel_name


def test_is_change_channel_returns_correct_responses():
    assert (
        is_change_channel("111-changes", change_channel_prefix="111-change-") == False
    )
    assert (
        is_change_channel("111-change-999", change_channel_prefix="111-change-") == True
    )
    assert (
        is_change_channel("111-change999", change_channel_prefix="111-change-") == False
    )


def test_extract_change_number_from_channel_name():
    assert get_change_number_from_channel_name("111-change-123") == 123
