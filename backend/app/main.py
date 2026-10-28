from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.config import CORS_ORIGINS
from app.api.routes import router

app = FastAPI(
    title="Resource Allocation and Scheduling Optimization API",
    description="Backend API for Enterprise Analytics Cluster Workload Scheduling (Heuristics, Metaheuristics, and RL)",
    version="1.0.0"
)

# Enable CORS for React frontend (configurable via CORS_ORIGINS environment variable)
app.add_middleware(
    CORSMiddleware,
    allow_origins=CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(router, prefix="/api")

@app.get("/")
def root():
    return {
        "project": "Resource Allocation and Scheduling Optimization for Enterprise Analytics",
        "docs": "/docs",
        "api_status": "RUNNING"
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("app.main:app", host="127.0.0.1", port=8000, reload=True)
