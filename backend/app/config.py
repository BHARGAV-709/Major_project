import os
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent.parent
DATA_DIR = BASE_DIR / "data"
RAW_DATA_DIR = DATA_DIR / "raw"
PROCESSED_DATA_DIR = DATA_DIR / "processed"
SYNTHETIC_DATA_DIR = DATA_DIR / "synthetic"
RESULTS_DIR = BASE_DIR / "results"

RAW_DATASET_PATH = BASE_DIR / "Dataset-2" / "container_scheduling_dataset_10000.csv"
DEFAULT_PROCESSED_PATH = PROCESSED_DATA_DIR / "container_scheduling_dataset_10000_cleaned.csv"

# Ensure directories exist
for folder in [DATA_DIR, RAW_DATA_DIR, PROCESSED_DATA_DIR, SYNTHETIC_DATA_DIR, RESULTS_DIR]:
    folder.mkdir(parents=True, exist_ok=True)

DEFAULT_CLUSTER_CONFIG = {
    "cpu_cores": 40,
    "memory_gb": 256,
    "gpu_units": 8,
    "bandwidth_mbps": 10000,
    "power_limit_watts": 5000
}

COST_RATES = {
    "cpu_core_per_sec": 0.00005,
    "memory_gb_per_sec": 0.00001,
    "gpu_unit_per_sec": 0.0002,
    "sla_violation_penalty": 25.0
}

# CORS Configuration
CORS_ORIGINS = [origin.strip() for origin in os.getenv(
    "CORS_ORIGINS",
    "http://localhost:3000,http://127.0.0.1:3000,http://localhost:5173,http://127.0.0.1:5173,*"
).split(",") if origin.strip()]
