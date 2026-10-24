from fastapi import FastAPI

app = FastAPI(title="Saarthi Bank Backend")


@app.get("/health")
def health():
    return {"status": "ok"}