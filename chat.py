from app.agent import Agent

agent = Agent(phone="8964384771")   # simulated caller ID
print("Saarthi: Hello, this is Saarthi. How can I help you today?")
while True:
    text = input("You: ").strip()
    if text.lower() in {"quit", "exit"}:
        break
    print("Saarthi:", agent.reply(text))