"""Bounded arithmetic interpreter for untrusted declarative lab expressions.

No Python bytecode is generated or executed. Every syntax node and numeric
intermediate is checked, then evaluated through explicit arithmetic dispatch.
"""

import ast
import math
import re
from functools import lru_cache

import numpy as np

MAX_EXPRESSION_LENGTH = 400
MAX_AST_NODES = 96
MAX_DEPTH = 16
MAX_POINTS = 1000
MAX_LITERAL = 1e12
MAX_RESULT = 1e100
FUNCTIONS = {
    "sin": np.sin, "cos": np.cos, "tan": np.tan, "exp": np.exp,
    "log": np.log, "sqrt": np.sqrt, "abs": np.abs,
}
CONSTANTS = {"pi": math.pi, "e": math.e}
OPERATORS = {
    ast.Add: np.add, ast.Sub: np.subtract, ast.Mult: np.multiply,
    ast.Div: np.divide, ast.Pow: np.power,
}


class MathExpressionError(ValueError):
    """Unsafe syntax, excessive computation, or an undefined numeric result."""


def valid_identifier(value):
    return (isinstance(value, str) and re.fullmatch(r"[A-Za-z][A-Za-z0-9_]{0,47}", value)
            is not None and "__" not in value)


def valid_variable(value):
    return valid_identifier(value) and value not in FUNCTIONS and value not in CONSTANTS


@lru_cache(maxsize=128)
def _parse(expression, variables):
    if not isinstance(expression, str) or not 1 <= len(expression) <= MAX_EXPRESSION_LENGTH:
        raise MathExpressionError("Expression length is outside the supported range.")
    if len(variables) > 5 or any(not valid_variable(name) for name in variables):
        raise MathExpressionError("Invalid declared variables.")
    try:
        tree = ast.parse(expression, mode="eval")
    except (SyntaxError, ValueError, RecursionError) as error:
        raise MathExpressionError("Invalid expression syntax.") from error
    if sum(1 for _ in ast.walk(tree)) > MAX_AST_NODES:
        raise MathExpressionError("Expression is too complex.")
    names = set(variables) | CONSTANTS.keys()

    def check(node, depth=0):
        if depth > MAX_DEPTH:
            raise MathExpressionError("Expression is too deeply nested.")
        if type(node) is ast.Constant:
            if type(node.value) not in (int, float) or abs(node.value) > MAX_LITERAL or not math.isfinite(node.value):
                raise MathExpressionError("Only bounded real numeric constants are supported.")
        elif type(node) is ast.Name:
            if node.id not in names or not isinstance(node.ctx, ast.Load):
                raise MathExpressionError("Undeclared symbol.")
        elif type(node) is ast.BinOp and type(node.op) in OPERATORS:
            check(node.left, depth + 1)
            check(node.right, depth + 1)
        elif type(node) is ast.UnaryOp and type(node.op) in (ast.UAdd, ast.USub):
            check(node.operand, depth + 1)
        elif type(node) is ast.Call and type(node.func) is ast.Name and node.func.id in FUNCTIONS:
            if len(node.args) != 1 or node.keywords:
                raise MathExpressionError("Functions require one positional argument.")
            check(node.args[0], depth + 1)
        else:
            raise MathExpressionError("Unsupported expression construct.")

    check(tree.body)
    return tree.body


def validate_expression(expression, variables):
    """Validate without executing; return the original expression for storage."""
    _parse(expression, tuple(sorted(variables)))
    return expression


def _number(value):
    # Internal callers supply scalars or one bounded, real NumPy vector. Never
    # coerce arbitrary objects, which could have executable conversion hooks.
    if type(value) in (int, float):
        try:
            result = float(value)
        except (OverflowError, ValueError) as error:
            raise MathExpressionError("Invalid numeric value.") from error
    elif type(value) is np.ndarray and value.dtype.kind in "fiu" and value.ndim == 1 and 1 <= value.size <= MAX_POINTS:
        result = value.astype(float, copy=False)
    elif isinstance(value, (np.floating, np.integer)):
        result = float(value)
    else:
        raise MathExpressionError("Only real scalars and bounded vectors are supported.")
    if not np.all(np.isfinite(result)) or np.any(np.abs(result) > MAX_RESULT):
        raise MathExpressionError("Result is not a finite supported number.")
    return result


def evaluate_expression(expression, values):
    """Evaluate only validated arithmetic; numeric failures stay within the lab."""
    node = _parse(expression, tuple(sorted(values)))
    environment = {name: _number(value) for name, value in values.items()}
    environment.update(CONSTANTS)

    def calculate(part):
        if type(part) is ast.Constant:
            return float(part.value)
        if type(part) is ast.Name:
            return environment[part.id]
        if type(part) is ast.UnaryOp:
            value = calculate(part.operand)
            return _number(-value if type(part.op) is ast.USub else value)
        if type(part) is ast.Call:
            return _number(FUNCTIONS[part.func.id](calculate(part.args[0])))
        left, right = calculate(part.left), calculate(part.right)
        if type(part.op) is ast.Pow and np.any(np.abs(right) > 1000):
            raise MathExpressionError("Exponent is outside the supported range.")
        return _number(OPERATORS[type(part.op)](left, right))

    try:
        with np.errstate(divide="raise", invalid="raise", over="raise", under="ignore"):
            return _number(calculate(node))
    except (FloatingPointError, OverflowError, ZeroDivisionError, ValueError) as error:
        raise MathExpressionError("Expression is undefined for these values.") from error
