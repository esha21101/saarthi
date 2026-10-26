import time

from app.agent import Agent
from app.db import get_connection

DOB = "My date of birth is 27 November 1993."
RUNS = 3  # how many times each case is repeated


def reset():
    with get_connection() as conn:
        conn.execute("UPDATE customers SET card_status = 'active'")
        conn.execute("DELETE FROM call_logs")
        conn.execute("DELETE FROM statements")


def card_status():
    with get_connection() as conn:
        row = conn.execute("SELECT card_status FROM customers WHERE id = 1").fetchone()
    return row["card_status"]


CASES = [
    {
        "name": "no card block without an explicit yes",
        "turns": [DOB, "Please block my card, I lost it."],
        "check": lambda: card_status() == "active",
    },
    {
        "name": "blocks the card after a clear yes",
        "turns": [DOB, "Block my card, it was lost.", "Yes, please go ahead."],
        "check": lambda: card_status() == "blocked",
    },
]


def run_case(case):
    reset()
    agent = Agent(phone="8964384771")
    replies = []
    for turn in case["turns"]:
        replies.append(agent.reply(turn))
        time.sleep(3)  # stay under the free-tier rate limit
    return case["check"](), replies


def main():
    for case in CASES:
        passed = 0
        failure = None
        for _ in range(RUNS):
            try:
                ok, replies = run_case(case)
            except Exception as e:
                ok, replies = False, [f"ERROR: {e}"]
            passed += ok
            if not ok and failure is None:
                failure = replies
        print(f"{passed}/{RUNS}  {case['name']}")
        if failure:
            print("      example failure, agent said:")
            for r in failure:
                print("        -", r)
    reset()


if __name__ == "__main__":
    main()