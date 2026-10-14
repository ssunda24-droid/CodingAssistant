import pytest

from temperature import celsius_to_fahrenheit


def test_normal_temperature():
    assert celsius_to_fahrenheit(25) == 77


def test_freezing_point():
    assert celsius_to_fahrenheit(0) == 32


def test_boiling_point():
    assert celsius_to_fahrenheit(100) == 212


def test_negative_temperature():
    assert celsius_to_fahrenheit(-40) == -40


@pytest.mark.parametrize(
    "invalid_input",
    ["abc", None, True, False, float("nan"), float("inf"), float("-inf")],
)
def test_invalid_input(invalid_input):
    with pytest.raises(ValueError):
        celsius_to_fahrenheit(invalid_input)
