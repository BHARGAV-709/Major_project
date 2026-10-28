import React, { useState } from 'react';
import { PlayCircle, Cpu, Clock, AlertTriangle, DollarSign, Layers } from 'lucide-react';
import { runSimulation } from '../services/api';
import GanttChartComponent from '../components/GanttChartComponent';
import MetricCard from '../components/MetricCard';

const ALGORITHMS = [
  "FCFS", "SJF", "Priority", "EDF", "Greedy",
  "GA", "PSO", "SA", "Q-Learning", "DQN"
];

export default function Simulation() {
  const [algorithm, setAlgorithm] = useState('Q-Learning');
  const [scenario, setScenario] = useState('MEDIUM');
  const [numJobs, setNumJobs] = useState(50);
  
  const [loading, setLoading] = useState(false);
  const [simResult, setSimResult] = useState(null);
  const [errorMessage, setErrorMessage] = useState(null);

  const handleRunSimulation = async () => {
    setLoading(true);
    setErrorMessage(null);
    try {
      const res = await runSimulation({
        algorithm: algorithm,
        scenario: scenario,
        max_jobs: numJobs
      });
      setSimResult(res.data);
    } catch (err) {
      console.error('Failed to run simulation', err);
      const detail = err.response?.data?.detail || err.message || 'Simulation execution failed. Please check backend connection.';
      setErrorMessage(detail);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="space-y-6">
      {/* Title */}
      <div className="flex flex-col md:flex-row md:items-center justify-between gap-4 bg-white border border-slate-200 p-6 rounded-xl shadow-xs">
        <div>
          <h1 className="text-xl font-bold text-slate-900 tracking-tight">Discrete-Event Simulation Engine</h1>
          <p className="text-xs text-slate-500 mt-1">
            Execute single scheduling strategy and observe live discrete-event queue & resource allocation
          </p>
        </div>
        <button
          onClick={handleRunSimulation}
          disabled={loading}
          className="flex items-center gap-2 bg-brand-600 hover:bg-brand-700 text-white text-xs font-semibold px-5 py-2.5 rounded-lg transition-all shadow-sm shadow-brand-500/20 disabled:opacity-50"
        >
          <PlayCircle className={`w-4 h-4 ${loading ? 'animate-spin' : ''}`} />
          <span>Run Single Simulation</span>
        </button>
      </div>

      {/* Control Configuration Panel */}
      <div className="bg-white border border-slate-200 rounded-xl p-5 shadow-xs grid grid-cols-1 md:grid-cols-3 gap-6">
        <div>
          <label className="text-xs font-semibold text-slate-700 block mb-2">Select Scheduling Algorithm</label>
          <select 
            value={algorithm} 
            onChange={(e) => setAlgorithm(e.target.value)}
            className="w-full border border-slate-300 rounded-lg p-2.5 text-xs text-slate-900 font-semibold bg-white"
          >
            {ALGORITHMS.map(a => (
              <option key={a} value={a}>{a} Algorithm</option>
            ))}
          </select>
        </div>

        <div>
          <label className="text-xs font-semibold text-slate-700 block mb-2">Workload Dataset / Scenario</label>
          <select 
            value={scenario} 
            onChange={(e) => setScenario(e.target.value)}
            className="w-full border border-slate-300 rounded-lg p-2.5 text-xs text-slate-900 bg-white"
          >
            <option value="DATASET">Google Cluster Dataset (Raw 10K Rows)</option>
            <option value="LIGHT">Light Contention Scenario</option>
            <option value="MEDIUM">Medium Contention Scenario</option>
            <option value="HEAVY">Heavy Contention Scenario</option>
            <option value="BURSTY">Bursty Job Arrival Scenario</option>
            <option value="OVERLOADED">Overloaded Cluster Scenario</option>
          </select>
        </div>

        <div>
          <label className="text-xs font-semibold text-slate-700 block mb-2">Number of Simulation Jobs</label>
          <input 
            type="number" 
            value={numJobs} 
            onChange={(e) => setNumJobs(parseInt(e.target.value) || 30)}
            className="w-full border border-slate-300 rounded-lg p-2.5 text-xs text-slate-900"
          />
        </div>
      </div>

      {/* Error Message Alert */}
      {errorMessage && (
        <div className="bg-rose-50 border border-rose-200 text-rose-800 p-4 rounded-xl text-xs flex items-center gap-2">
          <AlertTriangle className="w-4 h-4 text-rose-600 shrink-0" />
          <span>{errorMessage}</span>
        </div>
      )}

      {/* Simulation KPI Metrics */}
      {simResult && (
        <div className="space-y-6">
          {/* Submission and Completion Summary Status Bar */}
          <div className="bg-slate-50 border border-slate-200 rounded-xl p-4 flex flex-wrap items-center justify-between gap-4 text-xs">
            <div className="flex items-center gap-6">
              <div>
                <span className="text-slate-500 font-medium">Submitted Jobs:</span>
                <span className="font-bold text-slate-900 ml-1.5 font-mono">{simResult.total_jobs}</span>
              </div>
              <div>
                <span className="text-slate-500 font-medium">Completed:</span>
                <span className="font-bold text-emerald-600 ml-1.5 font-mono">{simResult.completed_count}</span>
              </div>
              {simResult.rejected_count > 0 && (
                <div>
                  <span className="text-slate-500 font-medium">Permanently Rejected:</span>
                  <span className="font-bold text-rose-600 ml-1.5 font-mono">{simResult.rejected_count}</span>
                </div>
              )}
              <div>
                <span className="text-slate-500 font-medium">Completion Rate:</span>
                <span className="font-bold text-brand-600 ml-1.5 font-mono">{simResult.completion_rate ?? ((simResult.completed_count / (simResult.total_jobs || 1)) * 100).toFixed(1)}%</span>
              </div>
            </div>
            <div className="text-[11px] text-slate-500 italic">
              * SLA violations and cost calculate metrics exclusively for executed jobs
            </div>
          </div>

          <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-5 gap-4">
            <MetricCard title="Makespan" value={`${simResult.metrics.makespan}`} unit="s" icon={Clock} color="brand" />
            <MetricCard title="Avg Waiting Time" value={`${simResult.metrics.avg_waiting_time}`} unit="s" icon={Clock} color="amber" />
            <MetricCard title="Overall Utilization" value={`${simResult.metrics.overall_utilization}`} unit="%" icon={Cpu} color="indigo" />
            <MetricCard title="SLA Violations" value={`${simResult.metrics.sla_violation_rate}`} unit="%" icon={AlertTriangle} color="rose" />
            <MetricCard title="Total Cost" value={`$${simResult.metrics.total_cost}`} icon={DollarSign} color="emerald" />
          </div>

          {/* Interactive Gantt Chart Render */}
          <GanttChartComponent timeline={simResult.timeline} />

          {/* Rejected Infeasible Jobs Banner (if any) */}
          {simResult.rejected_jobs && simResult.rejected_jobs.length > 0 && (
            <div className="bg-rose-50 border border-rose-200 rounded-xl p-4">
              <div className="flex items-center gap-2 mb-2">
                <AlertTriangle className="w-4 h-4 text-rose-600" />
                <h4 className="text-xs font-bold text-rose-900 uppercase tracking-wide">
                  Permanently Infeasible Jobs Rejected ({simResult.rejected_jobs.length})
                </h4>
              </div>
              <p className="text-xs text-rose-700 mb-3">
                The following jobs exceeded total cluster physical capacity (CPU, RAM, or GPU) and were immediately rejected:
              </p>
              <div className="overflow-x-auto">
                <table className="w-full text-left text-xs font-mono">
                  <thead>
                    <tr className="border-b border-rose-200 text-rose-800 text-[10px] uppercase font-bold">
                      <th className="py-1 px-2">Job ID</th>
                      <th className="py-1 px-2">Type</th>
                      <th className="py-1 px-2">Demands (CPU / RAM / GPU)</th>
                      <th className="py-1 px-2">Status</th>
                      <th className="py-1 px-2">Reason</th>
                    </tr>
                  </thead>
                  <tbody className="divide-y divide-rose-100 text-rose-900">
                    {simResult.rejected_jobs.map((rj) => (
                      <tr key={rj.job_id}>
                        <td className="py-1.5 px-2 font-bold">{rj.job_id}</td>
                        <td className="py-1.5 px-2 font-sans">{rj.job_type}</td>
                        <td className="py-1.5 px-2">{rj.cpu_cores} Cores / {rj.memory_mb} MB / {rj.gpu_units} GPU</td>
                        <td className="py-1.5 px-2 font-bold text-rose-700">{rj.status}</td>
                        <td className="py-1.5 px-2 font-sans text-rose-600">{rj.reason}</td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
            </div>
          )}

          {/* Schedule Table */}
          <div className="bg-white border border-slate-200 rounded-xl p-5 shadow-xs">
            <h3 className="text-sm font-bold text-slate-900 mb-3">Simulation Execution Schedule ({simResult.schedule?.length} Jobs)</h3>
            <div className="overflow-x-auto max-h-80">
              <table className="w-full text-left border-collapse min-w-[850px]">
                <thead className="sticky top-0 bg-slate-100 text-[11px] font-semibold text-slate-600 uppercase border-b border-slate-200">
                  <tr>
                    <th className="py-2.5 px-3">Job ID</th>
                    <th className="py-2.5 px-3">Type</th>
                    <th className="py-2.5 px-3">Server Slot</th>
                    <th className="py-2.5 px-3">Arrival</th>
                    <th className="py-2.5 px-3">Start</th>
                    <th className="py-2.5 px-3">Finish</th>
                    <th className="py-2.5 px-3">Wait Delay</th>
                    <th className="py-2.5 px-3">SLA Status</th>
                  </tr>
                </thead>
                <tbody className="divide-y divide-slate-100 text-xs font-mono">
                  {simResult.schedule?.map((item) => (
                    <tr key={item.job_id} className="hover:bg-slate-50">
                      <td className="py-2 px-3 font-bold text-slate-900">{item.job_id}</td>
                      <td className="py-2 px-3 font-sans font-medium text-slate-700">{item.job_type}</td>
                      <td className="py-2 px-3">{item.resource_id}</td>
                      <td className="py-2 px-3">{item.arrival_time}s</td>
                      <td className="py-2 px-3">{item.start_time}s</td>
                      <td className="py-2 px-3">{item.finish_time}s</td>
                      <td className="py-2 px-3 text-amber-600">{item.waiting_time}s</td>
                      <td className="py-2 px-3">
                        <span className={`px-2 py-0.5 rounded text-[10px] font-bold ${
                          item.sla_status === 'MET' ? 'bg-emerald-50 text-emerald-700 border border-emerald-200' : 'bg-rose-50 text-rose-700 border border-rose-200'
                        }`}>
                          {item.sla_status}
                        </span>
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}
