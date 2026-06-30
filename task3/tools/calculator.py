"""
Calculator Tool
Evaluates math expressions safely using Python's AST module.
Handles: addition, subtraction, multiplication, division, percentages.
"""

import ast
import operator
from langchain_core.tools import tool

# Map AST node types to actual Python operators
ALLOWED_OPS = {
    ast.Add: operator.add,
    ast.Sub: operator.sub,
    ast.Mult: operator.mul,
    ast.Div: operator.truediv,
    ast.Pow: operator.pow,
    ast.USub: operator.neg,
}


def safe_eval(node):
    """Walk the AST tree and compute the result safely (no eval())."""
    # Plain number
    if isinstance(node, ast.Constant) and isinstance(node.value, (int, float)):
        return node.value
    # Binary operation like 2 + 3
    if isinstance(node, ast.BinOp) and type(node.op) in ALLOWED_OPS:
        left = safe_eval(node.left)
        right = safe_eval(node.right)
        return ALLOWED_OPS[type(node.op)](left, right)
    # Unary operation like -5
    if isinstance(node, ast.UnaryOp) and type(node.op) in ALLOWED_OPS:
        return ALLOWED_OPS[type(node.op)](safe_eval(node.operand))
    raise ValueError(f"Unsupported: {ast.dump(node)}")


@tool
def calculator(expression: str) -> str:
    """
    Evaluates a math expression and returns the result.
    Use this for any arithmetic: addition, subtraction, multiplication,
    division, powers, percentages.

    Examples:
      '250 * 0.15' for 15% of 250
      '5000 / 12' for monthly payment
      '100 + 50' for addition
    """
    try:
        tree = ast.parse(expression, mode="eval")
        result = safe_eval(tree.body)
        return f"Result: {result}"
    except ZeroDivisionError:
        return "Error: Division by zero."
    except Exception as e:
        return f"Error: Could not evaluate '{expression}'. {e}"
