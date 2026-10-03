from fastapi import FastAPI

app = FastAPI(
    title="VantaWave ML",
    version="0.2.0",
    description="Wi-Fi security and machine-learning research platform.",
)

@app.get("/")
def root():
    return {
        "project": "VantaWave ML",
        "version": "0.2.0",
        "status": "running",
        "docs": "/docs",
        "health": "/health",
        "message": "VantaWave ML API is online.",
    }

@app.get("/health")
def health():
    return {
        "status": "ok",
        "project": "VantaWave ML",
        "version": "0.2.0",
    }
