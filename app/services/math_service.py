MAX_EXPONENT = 1000
MAX_FIBONACCI_N = 10000
MAX_FACTORIAL_N = 1000


class MathValidationError(ValueError):
    """Raised when a mathematical operation receives invalid input."""


def _validate_non_negative_integer(
    value: int,
    name: str,
    maximum: int,
) -> None:
    if isinstance(value, bool) or not isinstance(value, int):
        raise MathValidationError(
            f"{name} must be a non-negative integer."
        )

    if value < 0:
        raise MathValidationError(
            f"{name} must not be negative."
        )

    if value > maximum:
        raise MathValidationError(
            f"{name} must not be greater than {maximum}."
        )


def power(base: int | float, exponent: int) -> int | float:
    """
    Calculate base raised to the power of exponent.
    """

    if isinstance(base, bool) or not isinstance(base, (int, float)):
        raise MathValidationError(
            "base must be an integer or a float."
        )

    _validate_non_negative_integer(
        exponent,
        "exponent",
        MAX_EXPONENT,
    )

    return base ** exponent


def fibonacci(n: int) -> int:
    """
    Calculate the Fibonacci number at index n.

    Fibonacci uses zero-based indexing:
    F(0) = 0
    F(1) = 1
    """

    _validate_non_negative_integer(
        n,
        "n",
        MAX_FIBONACCI_N,
    )

    if n == 0:
        return 0

    if n == 1:
        return 1

    previous = 0
    current = 1

    for _ in range(2, n + 1):
        previous, current = current, previous + current

    return current


def factorial(n: int) -> int:
    """
    Calculate the factorial of n.
    """

    _validate_non_negative_integer(
        n,
        "n",
        MAX_FACTORIAL_N,
    )

    if n == 0 or n == 1:
        return 1

    result = 1

    for number in range(2, n + 1):
        result *= number

    return result