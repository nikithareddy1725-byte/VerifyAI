import urllib.request
import json
import time

time.sleep(2)
url = "http://localhost:8000/api/verify"

test_cases = [
    {"query": "3+5", "desc": "TEST 1: 3+5"},
    {"query": "25*16", "desc": "TEST 2: 25*16"},
    {"query": "3x+5=14", "desc": "TEST 3: 3x+5=14"},
    {"query": "2x-7=9", "desc": "TEST 4: 2x-7=9"},
    {"query": "3x+5=", "desc": "TEST 5: 3x+5="},
    {"query": "What is the capital of India?", "desc": "TEST 6: Capital of India"},
    {"query": "Is water's chemical formula H2O?", "desc": "TEST 7: Water H2O formula"}
]

for tc in test_cases:
    payload = json.dumps({"input_text": tc["query"], "task_type": "auto"}).encode("utf-8")
    req = urllib.request.Request(url, data=payload, headers={"Content-Type": "application/json"})
    try:
        with urllib.request.urlopen(req) as resp:
            data = json.loads(resp.read().decode("utf-8"))
            print(f"=== {tc['desc']} ===")
            print(f"Status Code: {resp.status}")
            print(f"Intent:      {data.get('intent')}")
            print(f"Profile:     {data.get('profile')}")
            print(f"Status:      {data.get('status')}")
            print(f"Answer:      {data.get('answer')}")
            if data.get('message'):
                print(f"Message:     {data.get('message')}")
            print(f"Decision:    {data.get('final_decision')}")
            print()
    except Exception as e:
        print(f"=== {tc['desc']} FAILED: {e} ===")
