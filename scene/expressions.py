"""Tiny safe finite-set expression parser. No Python AST or execution."""

import re
from dataclasses import dataclass

MAX_EXPRESSION_LENGTH = 120
MAX_EXPRESSION_DEPTH = 8
_TOKEN = re.compile(r"\s*([A-Za-z][A-Za-z0-9_]{0,31}|[|&~()\-])")


class EventExpressionError(ValueError):
    pass


@dataclass(frozen=True)
class Node:
    op: str
    value: str | None = None
    left: "Node | None" = None
    right: "Node | None" = None


def _tokens(expression):
    if not isinstance(expression, str) or not expression.strip():
        raise EventExpressionError("Expression is empty.")
    if len(expression) > MAX_EXPRESSION_LENGTH:
        raise EventExpressionError("Expression is too long.")
    tokens, position = [], 0
    while position < len(expression):
        match = _TOKEN.match(expression, position)
        if not match:
            raise EventExpressionError("Expression contains unsupported syntax.")
        tokens.append(match.group(1))
        position = match.end()
    return tokens


class _Parser:
    def __init__(self, tokens, identifiers):
        self.tokens, self.identifiers, self.index = tokens, set(identifiers), 0

    def parse(self):
        node = self.union(0)
        if self.index != len(self.tokens):
            raise EventExpressionError("Unexpected token.")
        return node

    def peek(self):
        return self.tokens[self.index] if self.index < len(self.tokens) else None

    def take(self):
        token = self.peek()
        self.index += 1
        return token

    def union(self, depth):
        node = self.intersection(depth)
        while self.peek() == "|":
            self.take(); node = Node("|", left=node, right=self.intersection(depth))
        return node

    def intersection(self, depth):
        node = self.unary(depth)
        while self.peek() in {"&", "-"}:
            op = self.take(); node = Node(op, left=node, right=self.unary(depth))
        return node

    def unary(self, depth):
        if depth > MAX_EXPRESSION_DEPTH:
            raise EventExpressionError("Expression is nested too deeply.")
        if self.peek() == "~":
            self.take(); return Node("~", left=self.unary(depth + 1))
        if self.peek() == "(":
            self.take()
            node = self.union(depth + 1)
            if self.take() != ")":
                raise EventExpressionError("Missing closing parenthesis.")
            return node
        token = self.take()
        if token is None or token in {"|", "&", "-", ")"}:
            raise EventExpressionError("Expected an event id.")
        if token not in self.identifiers:
            raise EventExpressionError(f"Unknown event id: {token}")
        return Node("id", value=token)


def parse_expression(expression, event_ids):
    return _Parser(_tokens(expression), event_ids).parse()


def evaluate_expression(expression, events, universe):
    """Return a frozenset of outcome ids for a validated expression."""
    node = parse_expression(expression, events)
    universe = frozenset(universe)

    def visit(item):
        if item.op == "id": return frozenset(events[item.value])
        if item.op == "~": return universe - visit(item.left)
        left, right = visit(item.left), visit(item.right)
        if item.op == "|": return left | right
        if item.op == "&": return left & right
        if item.op == "-": return left - right
        raise EventExpressionError("Unsupported operator.")
    return visit(node)


def display_expression(expression):
    tokens = _tokens(expression)
    identifiers = {token for token in tokens if re.fullmatch(r"[A-Za-z][A-Za-z0-9_]{0,31}", token)}
    node = _Parser(tokens, identifiers).parse()

    def render(item):
        if item.op == "id": return item.value
        if item.op == "~":
            child = render(item.left)
            return f"{child}ᶜ" if item.left.op == "id" else f"({child})ᶜ"
        symbols = {"|": "∪", "&": "∩", "-": "−"}
        return f"{render(item.left)} {symbols[item.op]} {render(item.right)}"
    return render(node)
