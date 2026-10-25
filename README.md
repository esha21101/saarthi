# Saarthi

A guardrailed AI support agent for lending customers. It handles requests like "what loans do I have?", "email me my statement" and "block my card", and it is built so the model **cannot** act on an unverified caller, change anything without confirmation, or touch another customer's data.

Status: work in progress. The text agent and backend work; evals, voice and Hinglish support are next (see Roadmap).

## How it works

```
Caller text --> Agent (LLM + system prompt + tool calling)
                      |
                      |  tool call (no customer or session id supplied by the LLM)
                      v
            FastAPI backend (enforces the rules again)
                      |
                      v
            PostgreSQL (customers, loans, payments, statements, call_logs)
```

1. The LLM only sees a list of tools. It never sees the phone number or session id.
2. The agent code adds the session id to each request, so the model can only act on the caller who verified.
3. The backend enforces every rule independently, so a misbehaving model cannot bypass them.

## Guardrails

| Rule | Where it is enforced |
|------|----------------------|
| Caller must verify (phone from caller ID + date of birth) before any data access | Backend session check |
| Wrong verification gives a vague error, and 3 failures lock the number | Backend |
| Sessions expire after 15 minutes | Backend |
| A customer can only see and act on their own loans | Backend ownership check (returns 404, not 403) |
| Statements, address changes and card blocks require `confirmed=true` | Backend |
| Inputs are validated (allowed periods and reasons, address length) | Pydantic models |
| One confirmation covers one action only; details are settled before asking | System prompt |
| Every action is written to `call_logs` (no personal data in the logs) | Backend |

## Tech stack

Python 3.12, FastAPI, PostgreSQL 16 (Docker), psycopg 3, Pydantic, pytest, and an OpenAI-compatible LLM API (Groq free tier by default; the provider is set in `.env`).

## Project structure

```
saarthi/
├── app/
│   ├── main.py        # FastAPI backend (the agent's tools)
│   ├── agent.py       # agent loop and system prompt
│   ├── tools.py       # tool definitions given to the LLM
│   └── db.py          # database connection
├── db/
│   ├── schema.sql     # tables
│   └── seed.sql       # fake demo data
├── tests/             # API tests
├── chat.py            # terminal chat with the agent
├── docker-compose.yml
└── requirements.txt
```

## Run it locally

Requires Python 3.11+, Docker Desktop and a free LLM API key (for example from Groq).

```bash
git clone https://github.com/YOUR-USERNAME/saarthi.git
cd saarthi
python -m venv .venv
.venv\Scripts\activate          # Windows. On Mac/Linux: source .venv/bin/activate
pip install -r requirements.txt
docker compose up -d            # starts Postgres on port 5433
```

Create a `.env` file in the project root (never commit it):

```
DATABASE_URL=postgresql://agent:agent@localhost:5433/bank
GROQ_API_KEY=your-key-here
GROQ_MODEL=a-tool-calling-model-from-your-provider
```

Start the backend, then chat with the agent in a second terminal:

```bash
uvicorn app.main:app --reload   # API docs at http://localhost:8000/docs
python chat.py
```

Run the tests (the database must be running):

```bash
python -m pytest -v
```

## Demo data

All data is fake. To act as a customer: phone `8964384771`, date of birth `1993-11-27` (Anya Roger, 2 loans). The agent uses this phone number as simulated caller ID.

Reset the demo data after trying actions:

```bash
docker compose exec db psql -U agent -d bank -c "UPDATE customers SET card_status = 'active'; UPDATE customers SET address = 'New Emblem Street escape 24' WHERE id = 1; DELETE FROM call_logs; DELETE FROM statements;"
```

## API endpoints

| Method | Path | Purpose |
|--------|------|---------|
| POST | `/verify` | Verify the caller and start a session |
| GET | `/loans` | The caller's loans |
| POST | `/statements/send` | Email a statement (needs confirmation) |
| GET | `/card` | Card status |
| POST | `/card/block` | Block the card (needs confirmation) |
| POST | `/address` | Update the address (needs confirmation) |
| POST | `/handoff` | Log a transfer to a human agent |

Protected endpoints take the session id in an `x-session-id` header.

## Testing

18 automated API tests cover verification, lockout, session expiry, ownership checks, confirmation rules, input validation, idempotent card blocking and call logging.

## Known limitations

- **The `confirmed` flag is set by the model.** The backend checks that it is true, but cannot verify the caller really said yes. A misbehaving or manipulated model could skip the confirmation step. Planned fix: a code check against the caller's actual message.
- **Callers who cannot verify cannot reach a human**, because handoff requires a verified session.
- **Tool definitions are hand-written** in `tools.py`, separate from the backend's Pydantic models, so the two must be kept in sync.
- Sessions and the lockout counter live in server memory and reset on restart; a production system would use a shared store such as Redis.
- Lockouts can be abused to lock a real customer out; production systems add cooldowns and alerts.
- Tests run against the development database and clean up after themselves.
- The `payments` table exists but is not yet exposed through an endpoint.

## Roadmap

- [x] Database schema and fake data
- [x] Backend with verification, ownership checks and confirmation rules
- [x] Call logging and API tests
- [x] Text agent with tool calling
- [ ] Eval suite: scripted conversations (including attacks) with measured pass rates
- [ ] Voice layer with latency measurements
- [ ] Hinglish test set and accuracy results
- [ ] Payments endpoint