import sys
sys.path.insert(0, '.')
from tools.equation_solver import solve_math_problem

test_cases = [
    '3+5',
    '25 * 16',
    '100 / 4',
    '2^5',
    '(10+5)*2',
    '3x+5=14',
    '2x-7=9',
    'x/2=8',
    '3x+5=',
    '3x+5',
    'What is the capital of India?'
]

for tc in test_cases:
    res = solve_math_problem(tc)
    print(f"=== INPUT: {tc} ===")
    if res.get("success"):
        print(f"Intent:  {res.get('intent')}")
        print(f"Profile: {res.get('profile')}")
        print(f"Status:  {res.get('status')}")
        print(f"Answer:  {res.get('answer')}")
        if res.get('message'):
            print(f"Message: {res.get('message')}")
        if res.get('explanation'):
            print(f"Explanation:\n{res.get('explanation')}")
    else:
        print(f"Not math: {res.get('error')}")
    print()
