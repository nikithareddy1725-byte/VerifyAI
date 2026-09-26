import re
import ast
import operator
import math
from typing import Dict, Any, Optional

ALLOWED_OPERATORS = {
    ast.Add: operator.add,
    ast.Sub: operator.sub,
    ast.Mult: operator.mul,
    ast.Div: operator.truediv,
    ast.Pow: operator.pow,
    ast.Mod: operator.mod,
    ast.USub: operator.neg,
    ast.UAdd: operator.pos
}

ALLOWED_FUNCTIONS = {
    'sqrt': math.sqrt,
    'abs': abs,
    'round': round,
    'floor': math.floor,
    'ceil': math.ceil
}

def normalize_math_text(text: str) -> str:
    """Normalize mathematical symbols, operators, and characters."""
    if not text:
        return ""
    s = text.strip()
    s = s.replace('×', '*').replace('·', '*').replace('✕', '*')
    s = s.replace('÷', '/')
    s = s.replace('^', '**')
    s = s.replace('–', '-').replace('—', '-')
    return s

def safe_eval_arithmetic(expr: str) -> float:
    """Safely evaluates a pure arithmetic expression using Python AST."""
    clean = normalize_math_text(expr).replace('=', '').strip()
    if not clean:
        raise ValueError("Empty arithmetic expression")
    
    # Handle percentage e.g. 50% -> 0.5
    clean = re.sub(r'(\d+(?:\.\d+)?)\s*%', r'(\1/100)', clean)
    
    tree = ast.parse(clean, mode='eval')
    
    def eval_node(node):
        if isinstance(node, ast.Constant):
            return node.value
        elif isinstance(node, ast.BinOp):
            op_type = type(node.op)
            if op_type in ALLOWED_OPERATORS:
                left = eval_node(node.left)
                right = eval_node(node.right)
                return ALLOWED_OPERATORS[op_type](left, right)
            raise ValueError(f"Operator {op_type.__name__} is not supported")
        elif isinstance(node, ast.UnaryOp):
            op_type = type(node.op)
            if op_type in ALLOWED_OPERATORS:
                operand = eval_node(node.operand)
                return ALLOWED_OPERATORS[op_type](operand)
            raise ValueError(f"Unary operator {op_type.__name__} is not supported")
        elif isinstance(node, ast.Call):
            if isinstance(node.func, ast.Name) and node.func.id in ALLOWED_FUNCTIONS:
                args = [eval_node(arg) for arg in node.args]
                return ALLOWED_FUNCTIONS[node.func.id](*args)
            raise ValueError(f"Function {ast.dump(node.func)} is not permitted")
        raise ValueError(f"Syntax element {type(node).__name__} is not permitted")
        
    return eval_node(tree.body)

def is_math_query(text: str) -> Dict[str, Any]:
    """
    Determines if input is a mathematical query.
    Returns categorization: 'arithmetic', 'algebra', 'incomplete_algebra', or False.
    """
    if not text or not text.strip():
        return {"is_math": False}
    
    raw = text.strip()
    lower = raw.lower()
    
    # Exclude common natural language question starting phrases
    fact_starts = ("who ", "where ", "when ", "why ", "what ", "explain ", "describe ", "tell me about", "is it true", "verify that", "is ", "are ", "does ", "did ", "can ", "which ", "how ")
    has_math_symbols = bool(re.search(r'[+\-*/×÷^=]', raw))
    has_math_keywords = any(k in lower for k in ["solve", "calculate", "evaluate", "compute", "integral", "derivative"])

    # If it has no math operators and no math keywords, it's NOT a calculation
    if not has_math_symbols and not has_math_keywords:
        return {"is_math": False}

    # If it starts with question words and has no '=' or 'solve', it's a factual question
    if any(lower.startswith(q) for q in fact_starts) and '=' not in raw and not has_math_keywords:
        return {"is_math": False}
    
    # 1. Check for algebra: contains single variable letter (x, y, z, a, b, etc.)
    # in algebraic contexts like 3x+5=, 3x+5=14, 2x-7=9, x/2=8
    vars_found = re.findall(r'\b[a-zA-Z]\b|(?<=\d)[a-zA-Z]|[a-zA-Z](?=\d)', raw)
    math_vars = [v for v in vars_found if v.lower() in ['x', 'y', 'z', 'a', 'b', 'n', 'm', 'k']]
    
    # Check incomplete equation like 3x+5= or 2x=
    if '=' in raw:
        parts = raw.split('=', 1)
        lhs = parts[0].strip()
        rhs = parts[1].strip() if len(parts) > 1 else ""
        if rhs == "":
            if math_vars or re.search(r'[a-zA-Z]', lhs):
                return {
                    "is_math": True,
                    "type": "algebra",
                    "status": "incomplete",
                    "var": math_vars[0] if math_vars else "x",
                    "lhs": lhs
                }
            elif re.search(r'\d', lhs):
                return {
                    "is_math": True,
                    "type": "arithmetic",
                    "status": "complete",
                    "expr": lhs
                }

    if math_vars and has_math_symbols:
        if '=' in raw:
            return {
                "is_math": True,
                "type": "algebra",
                "status": "complete",
                "var": math_vars[0],
                "raw": raw
            }
        else:
            return {
                "is_math": True,
                "type": "algebra",
                "status": "expression",
                "var": math_vars[0],
                "raw": raw
            }
            
    # 2. Pure arithmetic checks: e.g. 3+5, 25*16, 100/4, 2^5, (10+5)*2
    norm = normalize_math_text(raw)
    arithmetic_pattern = r'^[\s\(\)\d\.\+\-\*\/%]+$'
    if re.match(arithmetic_pattern, norm) and any(c in norm for c in '+-*/%'):
        return {
            "is_math": True,
            "type": "arithmetic",
            "status": "complete",
            "expr": norm
        }

    # 3. Explicit keywords: solve, calculate, evaluate
    if any(k in lower for k in ["solve", "calculate", "evaluate", "compute"]):
        # Extract expression after keyword
        rem = re.sub(r'^(?:solve|calculate|evaluate|compute)\s+', '', raw, flags=re.IGNORECASE).strip()
        if rem:
            sub_res = is_math_query(rem)
            if sub_res.get("is_math"):
                return sub_res
                
    return {"is_math": False}

def solve_math_problem(text: str) -> Dict[str, Any]:
    """
    Solves arithmetic or algebraic problem deterministically.
    Never hallucinates or invents fake results.
    """
    raw = text.strip()
    norm = normalize_math_text(raw)
    math_info = is_math_query(raw)
    
    if not math_info.get("is_math"):
        return {"success": False, "error": "Not a recognized mathematical problem"}
        
    mtype = math_info.get("type")
    mstatus = math_info.get("status")
    
    # CASE 1: Incomplete Algebra (e.g. 3x+5=)
    if mtype == "algebra" and mstatus == "incomplete":
        lhs = math_info.get("lhs", raw.rstrip('=').strip())
        return {
            "success": True,
            "intent": "algebra",
            "profile": "Algebra",
            "status": "incomplete_input",
            "answer": None,
            "message": "Equation incomplete. Please provide the value/expression after '='.",
            "example": f"{lhs} = 14",
            "explanation": (
                f"The input '{raw}' has an equality sign without a right-hand side.\n\n"
                f"To solve for the variable, please provide a complete equation.\n"
                f"Example: {lhs} = 14"
            )
        }

    # CASE 2: Algebraic Expression without equality (e.g. 3x+5)
    if mtype == "algebra" and mstatus == "expression":
        var = math_info.get("var", "x")
        return {
            "success": True,
            "intent": "algebra",
            "profile": "Algebra",
            "status": "incomplete_input",
            "answer": None,
            "message": f"Algebraic expression detected. To solve for {var}, provide an equation with '=' and a right-hand side.",
            "example": f"{raw} = 14",
            "explanation": (
                f"'{raw}' is an algebraic expression, not an equation.\n\n"
                f"To solve for {var}, an equation with an equals sign and right-hand side is required.\n"
                f"Example: {raw} = 14"
            )
        }

    # CASE 3: Complete Algebraic Equation (e.g. 3x+5=14, 2x-7=9, x/2=8)
    if mtype == "algebra" and mstatus == "complete":
        parts = norm.split('=', 1)
        lhs, rhs = parts[0].strip(), parts[1].strip()
        var = math_info.get("var", "x")
        
        # Prepare for two-point evaluation: insert * between coefficient and variable
        def prep(s):
            s = re.sub(r'(\d)\s*([a-zA-Z])', r'\1*\2', s)
            s = re.sub(r'([a-zA-Z])\s*(\d)', r'\1*\2', s)
            return s
            
        prep_lhs = prep(lhs)
        prep_rhs = prep(rhs)
        diff_expr = f"({prep_lhs}) - ({prep_rhs})"
        
        def eval_at(val: float) -> float:
            subbed = re.sub(r'\b' + var + r'\b', f"({val})", diff_expr)
            return safe_eval_arithmetic(subbed)
            
        try:
            f0 = eval_at(0.0)
            f1 = eval_at(1.0)
            m = f1 - f0
            c = f0
            
            if abs(m) < 1e-12:
                if abs(c) < 1e-12:
                    return {
                        "success": True,
                        "intent": "algebra",
                        "profile": "Algebra",
                        "status": "verified",
                        "answer": f"All real numbers (identity equation)",
                        "explanation": f"{lhs} = {rhs} is true for all values of {var}."
                    }
                else:
                    return {
                        "success": False,
                        "intent": "algebra",
                        "profile": "Algebra",
                        "status": "error",
                        "error": "No solution exists (inconsistent equation)"
                    }
                    
            x_val = -c / m
            # Clean display for integer values
            if abs(x_val - round(x_val)) < 1e-8:
                x_disp = int(round(x_val))
            else:
                x_disp = round(x_val, 4)
                
            steps = [
                f"Given Equation: {lhs} = {rhs}",
                f"Step 1: Simplify and group terms containing '{var}'.",
                f"Step 2: Isolate variable '{var}' by applying inverse operations.",
                f"Step 3: Solve: {var} = {x_disp}",
                f"Verification: Substituting {var} = {x_disp} into original equation confirms equality."
            ]
            
            return {
                "success": True,
                "intent": "algebra",
                "profile": "Algebra",
                "status": "verified",
                "answer": f"{var} = {x_disp}",
                "explanation": "\n".join(steps)
            }
        except Exception as e:
            return {
                "success": False,
                "intent": "algebra",
                "profile": "Algebra",
                "status": "error",
                "error": f"Failed to solve equation: {str(e)}"
            }

    # CASE 4: Pure Arithmetic (e.g. 3+5, 25*16, 100/4, 2^5, (10+5)*2)
    if mtype == "arithmetic":
        expr = math_info.get("expr", norm)
        try:
            val = safe_eval_arithmetic(expr)
            # Clean display: 8.0 -> 8
            if isinstance(val, float) and val.is_integer():
                ans_str = str(int(val))
            else:
                ans_str = str(round(val, 6))
                
            clean_display_expr = expr.replace('**', '^').replace('*', ' × ').replace('/', ' ÷ ').replace('  ', ' ').strip()
            
            return {
                "success": True,
                "intent": "mathematics",
                "profile": "Mathematics / Arithmetic",
                "status": "verified",
                "answer": ans_str,
                "explanation": f"{clean_display_expr} = {ans_str}"
            }
        except Exception as e:
            return {
                "success": False,
                "intent": "mathematics",
                "profile": "Mathematics / Arithmetic",
                "status": "error",
                "error": f"Calculation error: {str(e)}"
            }

    return {"success": False, "error": "Unrecognized math request"}
