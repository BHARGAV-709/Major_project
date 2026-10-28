# Execution, Startup, and Demonstration Guide

This guide provides instructions to install dependencies, run the backend and frontend servers, execute automated tests, and reproduce project demonstration workflows.

---

## 1. System Requirements & Prerequisites

- **Operating System**: Windows 10/11, macOS 12+, or Ubuntu 20.04+ LTS
- **Python**: Version 3.10.x (Recommended: Python 3.10.0+)
- **Node.js**: Version 18.x or 20.x LTS
- **Package Managers**: `pip` and `npm` (v9+)

---

## 2. Backend Setup & Startup

### Step 2.1: Virtual Environment Configuration
From the project root directory:

**Windows PowerShell:**
```powershell
python -m venv venv
.\venv\Scripts\Activate.ps1
```

**Linux / macOS:**
```bash
python3 -m venv venv
source venv/bin/activate
```

### Step 2.2: Install Backend Dependencies
```bash
pip install fastapi uvicorn sqlalchemy pydantic numpy torch scikit-learn pandas pytest httpx anyio
```

### Step 2.3: Launch FastAPI Development Server
Ensure the `PYTHONPATH` points to the `backend` directory so that all internal package imports (`app.workload`, `app.simulation`, etc.) resolve properly:

**Windows PowerShell:**
```powershell
$env:PYTHONPATH="backend"
uvicorn app.main:app --host 127.0.0.1 --port 8000 --reload
```

**Linux / macOS:**
```bash
export PYTHONPATH="backend"
uvicorn app.main:app --host 127.0.0.1 --port 8000 --reload
```

The backend server will initialize on `http://127.0.0.1:8000`. Interactive OpenAPI documentation will be accessible at `http://127.0.0.1:8000/docs`.

---

## 3. Frontend Setup & Startup

From the project root directory, navigate into the `frontend` directory:

```bash
cd frontend
npm install
```

### Option A: Development Server (HMR enabled)
```bash
npm run dev
```
Accessible at `http://127.0.0.1:5173` (or `3000`).

### Option B: Production Build & Preview
```bash
npm run build
npm run preview -- --port 3000 --host 127.0.0.1
```
Accessible at `http://127.0.0.1:3000`.

---

## 4. Automated Testing & Verification Commands

### Execute Full Pytest Suite (40 Tests)
From the project root directory:

**Windows PowerShell:**
```powershell
$env:PYTHONPATH="backend"
pytest backend -v
```

**Linux / macOS:**
```bash
PYTHONPATH=backend pytest backend -v
```

### Run Benchmark Discrepancy & Scaling Validation
```bash
python run_standard_benchmark.py
```
This generates and refreshes `standardized_benchmark_results.json` using standardized 25-job scenario workloads across master seed 42 and stochastic evaluation seeds 10, 20, 30, 40, 50.

---

## 5. End-to-End Demonstration Workflow

1. **Dashboard Overview (`/`)**:
   - Inspect cluster health and aggregate resource allocation metrics across algorithms.
2. **Dataset & Preprocessing (`/dataset`, `/preprocessing`)**:
   - Preview raw Google trace rows (`container_scheduling_dataset_10000_cleaned.csv`).
   - Trigger the 8-step automated preprocessing pipeline (mean imputation, IQR outlier clipping, min-max scaling).
3. **Discrete-Event Simulation (`/simulation`)**:
   - Select algorithm (e.g., `PSO` or `Q-Learning`), workload scenario (`MEDIUM`), and job count (`25` or `50`).
   - Click **Run Single Simulation**.
   - Inspect the interactive Gantt chart, server assignment slots, and status bar (`Submitted`, `Completed`, `Rejected`, `Completion Rate %`).
4. **Benchmark Comparison (`/results`)**:
   - Review side-by-side rankings of all 10 algorithms sorted by composite efficiency score.
   - Inspect sequential job execution order (`Order #1, #2, #3...`).
   - Click **Export Order CSV** to download the execution sequence with timestamps and resource allocations.

