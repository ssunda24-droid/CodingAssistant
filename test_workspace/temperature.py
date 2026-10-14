import math


def celsius_to_fahrenheit(celsius: int | float) -> float:
    """Convert a Celsius temperature to Fahrenheit."""
    if isinstance(celsius, bool) or not isinstance(celsius, (int, float)):
        raise ValueError("Temperature must be a numeric value.")

    if not math.isfinite(celsius):
        raise ValueError("Temperature must be finite.")

    return (celsius * 9 / 5) + 32
