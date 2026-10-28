import os
import shutil
import pandas as pd
from fastapi import APIRouter, UploadFile, File, Form, Depends, HTTPException
from typing import List, Dict, Any, Optional
from pydantic import BaseModel

from app.config import RAW_DATASET_PATH, PROCESSED_DATA_DIR, DEFAULT_CLUSTER_CONFIG
from app.preprocessing import PreprocessingPipeline
from app.workload import WorkloadLoader, WorkloadGenerator, Job
from app.scheduler import SchedulingDecisionEngine
from app.evaluation import PerformanceEvaluator, BenchmarkRunner
from app.database import get_db, DatasetRecord, ExperimentRecord
from sqlalchemy.orm import Session

router = APIRouter()

# Schema definitions
class SimulationRequest(BaseModel):
    scenario: str = "DATASET"  # DATASET, LIGHT, MEDIUM, HEAVY, BURSTY, OVERLOADED
    max_jobs: int = 100
    algorithm: str = "FCFS"
    cluster_config: Dict[str, Any] = DEFAULT_CLUSTER_CONFIG
    algo_params: Optional[Dict[str, Any]] = None

class PreprocessRequest(BaseModel):
    missing_strategy: str = "impute_mean"
    outlier_method: str = "iqr"
    scale_method: str = "minmax"

class BenchmarkRequest(BaseModel):
    scenario: str = "MEDIUM"
    max_jobs: int = 100
    algorithms: List[str] = ["FCFS", "SJF", "Priority", "EDF", "Greedy", "GA", "PSO", "SA", "Q-Learning", "DQN"]
    cluster_config: Dict[str, Any] = DEFAULT_CLUSTER_CONFIG
    algo_params: Optional[Dict[str, Any]] = None

@router.get("/status")
def get_system_status():
    dataset_exists = os.path.exists(RAW_DATASET_PATH)
    return {
        "status": "ONLINE",
        "dataset_found": dataset_exists,
        "dataset_path": str(RAW_DATASET_PATH),
        "cluster_defaults": DEFAULT_CLUSTER_CONFIG,
        "algorithms": SchedulingDecisionEngine.ALGORITHMS
    }

@router.get("/dataset/preview")
def preview_dataset(max_rows: int = 50):
    if not os.path.exists(RAW_DATASET_PATH):
        raise HTTPException(status_code=404, detail="Raw dataset file not found.")
    
    df = pd.read_csv(RAW_DATASET_PATH, nrows=max_rows)
    # Replace NaN with None for valid JSON serialization
    clean_df = df.where(pd.notnull(df), None)
    
    total_df = pd.read_csv(RAW_DATASET_PATH)
    missing_sum = int(total_df.isnull().sum().sum())
    dup_sum = int(total_df.duplicated().sum())

    return {
        "filename": "container_scheduling_dataset_10000.csv",
        "total_rows": len(total_df),
        "total_columns": len(total_df.columns),
        "columns": list(total_df.columns),
        "missing_values": missing_sum,
        "duplicates": dup_sum,
        "preview_rows": clean_df.to_dict(orient="records"),
        "dtypes": {col: str(dtype) for col, dtype in total_df.dtypes.items()}
    }

@router.post("/dataset/upload")
async def upload_dataset(file: UploadFile = File(...)):
    if not file.filename.endswith('.csv'):
        raise HTTPException(status_code=400, detail="Only CSV files allowed.")
    
    save_path = PROCESSED_DATA_DIR / f"uploaded_{file.filename}"
    with open(save_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)
        
    df = pd.read_csv(save_path)
    return {
        "message": f"Successfully uploaded {file.filename}",
        "rows": len(df),
        "columns": len(df.columns),
        "path": str(save_path)
    }

@router.post("/preprocessing/run")
def run_preprocessing(req: PreprocessRequest):
    if not os.path.exists(RAW_DATASET_PATH):
        raise HTTPException(status_code=404, detail="Raw dataset file not found.")
    
    pipeline = PreprocessingPipeline()
    res = pipeline.run_full_pipeline(
        filepath_or_df=RAW_DATASET_PATH,
        missing_strategy=req.missing_strategy,
        outlier_method=req.outlier_method,
        scale_method=req.scale_method
    )
    
    output_path = PROCESSED_DATA_DIR / "container_scheduling_dataset_10000_cleaned.csv"
    pipeline.cleaned_df.to_csv(output_path, index=False)

    return {
        "summary": res,
        "saved_cleaned_path": str(output_path),
        "sample_cleaned_rows": pipeline.cleaned_df.head(10).to_dict(orient="records")
    }

@router.post("/workload/generate")
def generate_workload(scenario: str = "MEDIUM", num_jobs: int = 100, seed: int = 42):
    jobs = WorkloadGenerator.generate_scenario(scenario=scenario, num_jobs=num_jobs, seed=seed)
    return {
        "scenario": scenario,
        "count": len(jobs),
        "jobs": [j.to_dict() for j in jobs]
    }

@router.post("/simulation/run")
def run_simulation(req: SimulationRequest, db: Session = Depends(get_db)):
    if req.algorithm.upper() not in [a.upper() for a in SchedulingDecisionEngine.ALGORITHMS]:
        raise HTTPException(status_code=400, detail=f"Unknown algorithm: '{req.algorithm}'. Supported: {SchedulingDecisionEngine.ALGORITHMS}")

    valid_scenarios = ["DATASET", "LIGHT", "MEDIUM", "HEAVY", "BURSTY", "OVERLOADED"]
    if req.scenario.upper() not in valid_scenarios:
        raise HTTPException(status_code=400, detail=f"Unknown scenario: '{req.scenario}'. Supported: {valid_scenarios}")

    if req.scenario.upper() == "DATASET":
        jobs = WorkloadLoader.load_from_csv(RAW_DATASET_PATH, max_jobs=req.max_jobs)
    else:
        jobs = WorkloadGenerator.generate_scenario(scenario=req.scenario, num_jobs=req.max_jobs)

    exec_res = SchedulingDecisionEngine.execute_algorithm(
        algorithm_name=req.algorithm,
        jobs=jobs,
        cluster_config=req.cluster_config,
        algo_params=req.algo_params
    )

    metrics = PerformanceEvaluator.calculate_metrics(
        schedule=exec_res["schedule"],
        cluster_config=req.cluster_config
    )

    # Save experiment record to database
    exp_record = ExperimentRecord(
        experiment_name=f"SingleSim-{req.algorithm}-{req.scenario}",
        scenario_type=req.scenario,
        algorithm_name=req.algorithm,
        num_jobs=len(jobs),
        cluster_config=req.cluster_config,
        metrics=metrics,
        execution_time_sec=exec_res["execution_time_sec"]
    )
    db.add(exp_record)
    db.commit()

    completed_cnt = exec_res.get("completed_count", len(exec_res["schedule"]))
    rejected_cnt = exec_res.get("rejected_count", 0)
    total_cnt = exec_res.get("total_jobs", len(jobs))
    completion_rate = round((completed_cnt / total_cnt) * 100.0, 2) if total_cnt > 0 else 0.0

    return {
        "algorithm": req.algorithm,
        "scenario": req.scenario,
        "execution_time_sec": exec_res["execution_time_sec"],
        "completed_count": completed_cnt,
        "rejected_count": rejected_cnt,
        "total_jobs": total_cnt,
        "completion_rate": completion_rate,
        "metrics": metrics,
        "timeline": exec_res["timeline"],
        "resource_history": exec_res["resource_history"],
        "schedule": exec_res["schedule"],
        "rejected_jobs": exec_res.get("rejected_jobs", []),
        "extra": exec_res.get("extra", {})
    }

@router.post("/benchmark/run")
def run_benchmark(req: BenchmarkRequest, db: Session = Depends(get_db)):
    if req.scenario.upper() == "DATASET":
        jobs = WorkloadLoader.load_from_csv(RAW_DATASET_PATH, max_jobs=req.max_jobs)
    else:
        jobs = WorkloadGenerator.generate_scenario(scenario=req.scenario, num_jobs=req.max_jobs)

    benchmark_results = BenchmarkRunner.run_benchmark(
        jobs=jobs,
        cluster_config=req.cluster_config,
        algorithms=req.algorithms,
        algo_params=req.algo_params
    )

    # Save top algorithm benchmark summary to DB
    for res in benchmark_results:
        rec = ExperimentRecord(
            experiment_name=f"Benchmark-{req.scenario}-{res['algorithm']}",
            scenario_type=req.scenario,
            algorithm_name=res["algorithm"],
            num_jobs=len(jobs),
            cluster_config=req.cluster_config,
            metrics=res["metrics"],
            execution_time_sec=res["execution_time_sec"]
        )
        db.add(rec)
    db.commit()

    return {
        "scenario": req.scenario,
        "job_count": len(jobs),
        "cluster_config": req.cluster_config,
        "benchmark_summary": [
            {
                "rank": r["rank"],
                "algorithm": r["algorithm"],
                "execution_time_sec": r["execution_time_sec"],
                "makespan": r["metrics"]["makespan"],
                "avg_waiting_time": r["metrics"]["avg_waiting_time"],
                "overall_utilization": r["metrics"]["overall_utilization"],
                "cpu_utilization": r["metrics"]["cpu_utilization"],
                "memory_utilization": r["metrics"]["memory_utilization"],
                "gpu_utilization": r["metrics"]["gpu_utilization"],
                "sla_violation_rate": r["metrics"]["sla_violation_rate"],
                "total_cost": r["metrics"]["total_cost"],
                "efficiency_score": r["metrics"]["efficiency_score"]
            }
            for r in benchmark_results
        ],
        "detailed_results": benchmark_results
    }

@router.get("/experiments/history")
def get_experiment_history(db: Session = Depends(get_db)):
    records = db.query(ExperimentRecord).order_by(ExperimentRecord.created_at.desc()).limit(50).all()
    return [
        {
            "id": r.id,
            "experiment_name": r.experiment_name,
            "scenario": r.scenario_type,
            "algorithm": r.algorithm_name,
            "num_jobs": r.num_jobs,
            "metrics": r.metrics,
            "execution_time_sec": r.execution_time_sec,
            "created_at": r.created_at.isoformat() if r.created_at else None
        }
        for r in records
    ]
