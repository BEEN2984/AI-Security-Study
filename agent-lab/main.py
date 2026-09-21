from agent import run_agent
from tools import TRACE

user_input = input("INPUT: ")

response = run_agent(user_input)

print("Agent:", response)

print("\nTRACE")
for event in TRACE:
    print(event)