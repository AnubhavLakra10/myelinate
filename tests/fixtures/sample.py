"""Sample Python file for testing tree-sitter extraction."""

import os  # noqa: F401
from pathlib import Path  # noqa: F401


def greet(name: str) -> str:
    """Greet someone by name."""
    return f"Hello, {name}"


def farewell(name: str) -> str:
    """Say goodbye, reusing greet."""
    greeting = greet(name)
    return greeting.replace("Hello", "Goodbye")


class Calculator:
    """A simple calculator."""

    def add(self, a: int, b: int) -> int:
        return a + b

    def multiply(self, a: int, b: int) -> int:
        return a * b
