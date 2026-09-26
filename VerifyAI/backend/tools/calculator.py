import ast
import operator
import math

class Calculator:
    def evaluate(self, expression: str) -> dict:
        allowed_operators = {
            ast.Add: operator.add,
            ast.Sub: operator.sub,
            ast.Mult: operator.mul,
            ast.Div: operator.truediv,
            ast.Pow: operator.pow,
            ast.Mod: operator.mod,
            ast.USub: operator.neg
        }
        
        allowed_functions = {
            'sqrt': math.sqrt,
            'abs': abs
        }

        def eval_node(node):
            if isinstance(node, ast.Constant):
                return node.value
            elif isinstance(node, ast.BinOp):
                left = eval_node(node.left)
                right = eval_node(node.right)
                if type(node.op) in allowed_operators:
                    return allowed_operators[type(node.op)](left, right)
            elif isinstance(node, ast.UnaryOp):
                operand = eval_node(node.operand)
                if type(node.op) in allowed_operators:
                    return allowed_operators[type(node.op)](operand)
            elif isinstance(node, ast.Call):
                if isinstance(node.func, ast.Name) and node.func.id in allowed_functions:
                    args = [eval_node(arg) for arg in node.args]
                    return allowed_functions[node.func.id](*args)
            raise ValueError(f"Unsupported syntax: {ast.dump(node)}")

        try:
            tree = ast.parse(expression, mode='eval')
            result = eval_node(tree.body)
            return {
                "expression": expression,
                "result": result,
                "success": True,
                "error": None
            }
        except Exception as e:
            return {
                "expression": expression,
                "result": None,
                "success": False,
                "error": str(e)
            }
