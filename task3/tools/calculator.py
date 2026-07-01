"""Safe math expression evaluator using AST (no eval())."""

import ast
import operator
from langchain_core.tools import tool

ALLOWED_OPS = {
    ast.Add: operator.add,
    ast.Sub: operator.sub,
    ast.Mult: operator.mul,
    ast.Div: operator.truediv,
    ast.Pow: operator.pow,
    ast.USub: operator.neg,
}


def safe_eval(node):
    """Recursively evaluate an AST node using only whitelisted operators."""
    if isinstance(node, ast.Constant) and isinstance(node.value, (int, float)):
        return node.value
    if isinstance(node, ast.BinOp) and type(node.op) in ALLOWED_OPS:
        left = safe_eval(node.left)
        right = safe_eval(node.right)
        return ALLOWED_OPS[type(node.op)](left, right)
    if isinstance(node, ast.UnaryOp) and type(node.op) in ALLOWED_OPS:
        return ALLOWED_OPS[type(node.op)](safe_eval(node.operand))
    raise ValueError(f"Unsupported: {ast.dump(node)}")


@tool
def calculator(expression: str) -> str:
    """
    Evaluate a math expression safely. Supports +, -, *, /, **, and percentages.
    Examples: '250 * 0.15', '5000 / 12', '2 ** 10'
    """
    try:
        tree = ast.parse(expression, mode="eval")
        result = safe_eval(tree.body)
        return f"Result: {result}"
    except ZeroDivisionError:
        return "Error: Division by zero."
    except Exception as e:
        return f"Error: Could not evaluate '{expression}'. {e}"
