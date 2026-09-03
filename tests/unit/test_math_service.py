import pytest

from app.services.math_service import (
    MAX_EXPONENT,
    MAX_FACTORIAL_N,
    MAX_FIBONACCI_N,
    MathValidationError,
    factorial,
    fibonacci,
    power,
)


def test_power_normal_case():
    assert power(2, 10) == 1024


def test_power_with_zero_base():
    assert power(0, 5) == 0


def test_power_with_zero_exponent():
    assert power(5, 0) == 1


def test_power_rejects_negative_exponent():
    with pytest.raises(MathValidationError, match="must not be negative"):
        power(2, -1)


def test_power_rejects_exponent_above_limit():
    with pytest.raises(MathValidationError, match="greater than"):
        power(2, MAX_EXPONENT + 1)


def test_power_rejects_invalid_base():
    with pytest.raises(MathValidationError, match="base"):
        power("2", 3)


def test_fibonacci_zero():
    assert fibonacci(0) == 0


def test_fibonacci_one():
    assert fibonacci(1) == 1


def test_fibonacci_normal_case():
    assert fibonacci(10) == 55


def test_fibonacci_rejects_negative_value():
    with pytest.raises(MathValidationError, match="must not be negative"):
        fibonacci(-1)


def test_fibonacci_rejects_value_above_limit():
    with pytest.raises(MathValidationError, match="greater than"):
        fibonacci(MAX_FIBONACCI_N + 1)


def test_factorial_zero():
    assert factorial(0) == 1


def test_factorial_one():
    assert factorial(1) == 1


def test_factorial_normal_case():
    assert factorial(5) == 120


def test_factorial_rejects_negative_value():
    with pytest.raises(MathValidationError, match="must not be negative"):
        factorial(-1)


def test_factorial_rejects_value_above_limit():
    with pytest.raises(MathValidationError, match="greater than"):
        factorial(MAX_FACTORIAL_N + 1)