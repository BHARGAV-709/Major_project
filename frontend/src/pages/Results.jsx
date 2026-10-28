import React, { useState, useEffect } from 'react';
import { useLocation } from 'react-router-dom';
import { 
  BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer, Legend 
} from 'recharts';
import { Trophy, RefreshCw, BarChart3, Award, DollarSign, Download, Cpu, HardDrive, Zap, Calendar, ArrowRight, ListOrdered } from 'lucide-react';
import { runBenchmark } from '../services/api';

export default function Results() {
  const location = useLocation();
  const [data, setData] = useState(location.state?.benchmarkSummary || null);
  const [loading, setLoading] = useState(false);
  const [selectedAlgoForSchedule, setSelectedAlgoForSchedule] = useState('');
  const [errorMsg, setErrorMsg] = useState(null);

  useEffect(() => {
    if (!data) {
      fetchBenchmark();
    } else if (data.detailed_results && data.detailed_results.length > 0) {
      setSelectedAlgoForSchedule(data.detailed_results[0].algorithm);
    }
  }, []);

  const fetchBenchmark = async () => {
    setLoading(true);
    setErrorMsg(null);
    try {
      const res = await runBenchmark({
        scenario: 'MEDIUM',
        max_jobs: 50,
        algorithms: ['FCFS', 'SJF', 'Priority', 'EDF', 'Greedy', 'GA', 'PSO', 'SA', 'Q-Learning', 'DQN']
      });
      setData(res.data);
      if (res.data?.detailed_results?.length > 0) {
        setSelectedAlgoForSchedule(res.data.detailed_results[0].algorithm);
      }
    } catch (err) {
      console.error(err);
      const detail = err.response?.data?.detail || err.message || 'Failed to fetch benchmark results.';
      setErrorMsg(detail);
    } finally {
      setLoading(false);
    }
  };

  const summary = data?.benchmark_summary || [];
  const detailedResults = data?.detailed_results || [];
  const topRank = summary.length > 0 ? summary[0] : null;

  // Selected schedule object
  const activeDetail = detailedResults.find(r => r.algorithm === selectedAlgoForSchedule) || detailedResults[0];
  
  // Sort schedule strictly by start_time to get exact execution order sequence (#1, #2, #3...)
  const rawSchedule = activeDetail?.schedule || [];
  const orderedSchedule = [...rawSchedule].sort((a, b) => a.start_time - b.start_time);

  // Totals for active schedule
  const totalCpuAllocated = orderedSchedule.reduce((sum, j) => sum + (j.cpu_cores || 0), 0);
  const totalRamAllocatedMb = orderedSchedule.reduce((sum, j) => sum + (j.memory_mb || 0), 0);
  const totalGpuAllocated = orderedSchedule.reduce((sum, j) => sum + (j.gpu_units || 0), 0);

  // CSV Export functionality
  const downloadCSV = () => {
    if (!orderedSchedule || orderedSchedule.length === 0) return;
    const headers = [
      "Execution_Order", "Job_ID", "Job_Type", "Assigned_Server", "Arrival_Time_s", "Start_Time_s", 
      "Finish_Time_s", "Runtime_s", "Waiting_Time_s", "CPU_Cores", "Memory_MB", "GPU_Units", "SLA_Status", "Cost_$"
    ];
    const rows = orderedSchedule.map((j, idx) => [
      `Order #${idx + 1}`, j.job_id, j.job_type, j.resource_id, j.arrival_time, j.start_time,
      j.finish_time, j.runtime, j.waiting_time, j.cpu_cores, j.memory_mb, j.gpu_units, j.sla_status, j.cost_budget
    ]);
    
    const csvContent = "data:text/csv;charset=utf-8," + [headers.join(","), ...rows.map(e => e.join(","))].join("\n");
    const encodedUri = encodeURI(csvContent);
    const link = document.createElement("a");
    link.setAttribute("href", encodedUri);
    link.setAttribute("download", `job_execution_order_${selectedAlgoForSchedule || 'optimal'}.csv`);
    document.body.appendChild(link);
    link.click();
    document.body.removeChild(link);
  };

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex flex-col md:flex-row md:items-center justify-between gap-4 bg-white border border-slate-200 p-6 rounded-xl shadow-xs">
        <div>
          <h1 className="text-xl font-bold text-slate-900 tracking-tight">Benchmark Analytics & Job Scheduling Results</h1>
          <p className="text-xs text-slate-500 mt-1">
            Comparative performance matrix and sequential job execution order (Which job executes 1st, 2nd, 3rd, and resource allocation)
          </p>
        </div>
        <button
          onClick={fetchBenchmark}
          className="flex items-center gap-2 bg-white hover:bg-slate-50 text-slate-700 text-xs font-semibold px-4 py-2.5 rounded-lg border border-slate-300 shadow-xs"
        >
          <RefreshCw className={`w-4 h-4 ${loading ? 'animate-spin' : ''}`} />
          <span>Re-run Benchmark</span>
        </button>
      </div>

      {errorMsg && (
        <div className="bg-rose-50 border border-rose-200 text-rose-800 p-4 rounded-xl text-xs flex items-center gap-2">
          <span>{errorMsg}</span>
        </div>
      )}

      {/* Winner Highlight Card */}
      {topRank && (
        <div className="bg-gradient-to-r from-brand-600 to-indigo-600 text-white rounded-xl p-6 shadow-md flex items-center justify-between">
          <div className="space-y-1">
            <div className="inline-flex items-center gap-1.5 bg-white/20 px-3 py-1 rounded-full text-xs font-semibold uppercase tracking-wider">
              <Trophy className="w-4 h-4 text-amber-300" />
              #1 Ranked Optimal Algorithm: {topRank.algorithm}
            </div>
            <h2 className="text-2xl font-extrabold tracking-tight pt-1">
              Efficiency Score: {topRank.efficiency_score} / 100
            </h2>
            <p className="text-xs text-brand-100 max-w-xl">
              {topRank.algorithm} achieved the optimal scheduling order with {topRank.makespan}s makespan, {topRank.overall_utilization}% resource utilization, and {topRank.sla_violation_rate}% SLA violation rate.
            </p>
          </div>
        </div>
      )}

      {/* SEQUENTIAL JOB EXECUTION ORDER & RESOURCE ALLOCATION (User Requested Feature) */}
      <div className="bg-white border border-slate-200 rounded-xl p-5 shadow-xs space-y-4">
        <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4 border-b border-slate-100 pb-3">
          <div>
            <h3 className="text-sm font-bold text-slate-900 flex items-center gap-2">
              <ListOrdered className="w-4 h-4 text-brand-600" />
              Optimal Job Execution Sequence Order (Step #1, Step #2, Step #3 ...)
            </h3>
            <p className="text-xs text-slate-500">
              Analysed job execution order based on cluster resource availability (CPU, RAM Memory/Database, GPU)
            </p>
          </div>

          <div className="flex items-center gap-3">
            {/* Select Algorithm for Schedule */}
            <div className="flex items-center gap-2 text-xs">
              <span className="text-slate-500 font-medium">Select Algorithm:</span>
              <select 
                value={selectedAlgoForSchedule || (topRank?.algorithm || '')}
                onChange={(e) => setSelectedAlgoForSchedule(e.target.value)}
                className="border border-slate-300 rounded-md px-3 py-1.5 text-xs text-slate-900 font-bold bg-white focus:outline-none focus:border-brand-500"
              >
                {summary.map(r => (
                  <option key={r.algorithm} value={r.algorithm}>
                    #{r.rank} {r.algorithm} ({r.efficiency_score} pts)
                  </option>
                ))}
              </select>
            </div>

            {/* Export CSV button */}
            <button
              onClick={downloadCSV}
              className="flex items-center gap-1.5 bg-brand-50 hover:bg-brand-100 text-brand-700 border border-brand-200 text-xs font-semibold px-3 py-1.5 rounded-md transition-colors"
            >
              <Download className="w-3.5 h-3.5" />
              <span>Export Order CSV</span>
            </button>
          </div>
        </div>

        {/* Visual Job Execution Sequence Banner Flow */}
        <div className="bg-slate-50 p-3.5 rounded-xl border border-slate-200 space-y-2">
          <div className="text-[11px] font-bold text-slate-600 uppercase tracking-wider">
            Execution Flow Sequence ({selectedAlgoForSchedule || 'Optimal'} Strategy)
          </div>
          <div className="overflow-x-auto pb-1">
            <div className="flex items-center gap-2 min-w-[700px]">
              {orderedSchedule.slice(0, 10).map((j, idx) => (
                <React.Fragment key={j.job_id}>
                  <div className="bg-white border border-slate-200 p-2.5 rounded-lg text-center shadow-2xs shrink-0 w-28">
                    <div className="text-[10px] font-bold text-brand-600">ORDER #{idx + 1}</div>
                    <div className="text-xs font-bold text-slate-900 mt-0.5">{j.job_id}</div>
                    <div className="text-[10px] text-slate-500 truncate">{j.job_type}</div>
                    <div className="text-[9px] font-mono text-slate-400 mt-1">{j.start_time}s → {j.finish_time}s</div>
                  </div>
                  {idx < Math.min(9, orderedSchedule.length - 1) && (
                    <ArrowRight className="w-4 h-4 text-slate-400 shrink-0" />
                  )}
                </React.Fragment>
              ))}
              {orderedSchedule.length > 10 && (
                <span className="text-xs text-slate-500 font-semibold shrink-0 pl-2">
                  + {orderedSchedule.length - 10} more jobs...
                </span>
              )}
            </div>
          </div>
        </div>

        {/* Resource totals for active schedule */}
        <div className="grid grid-cols-1 sm:grid-cols-5 gap-3 bg-white p-3 rounded-xl border border-slate-200 text-xs">
          <div>
            <span className="text-slate-500 font-medium">Scheduled / Completed:</span>
            <span className="font-bold text-slate-900 ml-1 font-mono">{orderedSchedule.length} Jobs</span>
          </div>
          <div>
            <span className="text-slate-500 font-medium">Completion Rate:</span>
            <span className="font-bold text-brand-600 ml-1 font-mono">
              {activeDetail?.total_jobs 
                ? `${((orderedSchedule.length / activeDetail.total_jobs) * 100).toFixed(1)}%` 
                : '100.0%'}
            </span>
          </div>
          <div>
            <span className="text-slate-500 font-medium">Total CPU:</span>
            <span className="font-bold text-brand-600 ml-1 font-mono">{totalCpuAllocated} Cores</span>
          </div>
          <div>
            <span className="text-slate-500 font-medium">Total RAM:</span>
            <span className="font-bold text-emerald-600 ml-1 font-mono">{(totalRamAllocatedMb / 1024.0).toFixed(1)} GB</span>
          </div>
          <div>
            <span className="text-slate-500 font-medium">Total GPU:</span>
            <span className="font-bold text-indigo-600 ml-1 font-mono">{totalGpuAllocated} Units</span>
          </div>
        </div>

        {/* Rejected Infeasible Jobs Banner (if any) */}
        {activeDetail?.rejected_jobs && activeDetail.rejected_jobs.length > 0 && (
          <div className="bg-rose-50 border border-rose-200 rounded-xl p-4">
            <div className="flex items-center gap-2 mb-1">
              <AlertTriangle className="w-4 h-4 text-rose-600" />
              <h4 className="text-xs font-bold text-rose-900 uppercase tracking-wide">
                Permanently Infeasible Jobs Rejected ({activeDetail.rejected_jobs.length})
              </h4>
            </div>
            <p className="text-xs text-rose-700 mb-2">
              The following submitted jobs exceeded total cluster capacity and were rejected prior to execution:
            </p>
            <div className="overflow-x-auto">
              <table className="w-full text-left text-xs font-mono">
                <thead>
                  <tr className="border-b border-rose-200 text-rose-800 text-[10px] uppercase font-bold">
                    <th className="py-1 px-2">Job ID</th>
                    <th className="py-1 px-2">Type</th>
                    <th className="py-1 px-2">Requested Demands</th>
                    <th className="py-1 px-2">Terminal Status</th>
                    <th className="py-1 px-2">Reason</th>
                  </tr>
                </thead>
                <tbody className="divide-y divide-rose-100 text-rose-900">
                  {activeDetail.rejected_jobs.map((rj) => (
                    <tr key={rj.job_id}>
                      <td className="py-1 px-2 font-bold">{rj.job_id}</td>
                      <td className="py-1 px-2 font-sans">{rj.job_type}</td>
                      <td className="py-1 px-2">{rj.cpu_cores} Cores / {rj.memory_mb} MB / {rj.gpu_units} GPU</td>
                      <td className="py-1 px-2 font-bold text-rose-700">{rj.status}</td>
                      <td className="py-1 px-2 font-sans text-rose-600">{rj.reason}</td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          </div>
        )}

        {/* Complete Schedule Table with Explicit Execution Order # */}
        <div className="overflow-x-auto max-h-[450px]">
          <table className="w-full text-left border-collapse min-w-[1050px]">
            <thead className="sticky top-0 bg-slate-100 text-[11px] font-semibold text-slate-600 uppercase border-b border-slate-200 z-10">
              <tr>
                <th className="py-2.5 px-3">Exec Order</th>
                <th className="py-2.5 px-3">Job ID</th>
                <th className="py-2.5 px-3">Job Type</th>
                <th className="py-2.5 px-3">Assigned Server</th>
                <th className="py-2.5 px-3">CPU Cores</th>
                <th className="py-2.5 px-3">RAM Memory / Database</th>
                <th className="py-2.5 px-3">GPU Units</th>
                <th className="py-2.5 px-3">Arrival → Start → Finish</th>
                <th className="py-2.5 px-3">Runtime</th>
                <th className="py-2.5 px-3">Wait Time</th>
                <th className="py-2.5 px-3">SLA Status</th>
                <th className="py-2.5 px-3">Cost ($)</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-slate-100 text-xs font-mono">
              {orderedSchedule.map((item, idx) => (
                <tr key={item.job_id} className="hover:bg-slate-50/80 transition-colors">
                  <td className="py-2.5 px-3 font-bold text-brand-600">
                    <span className="bg-brand-50 px-2 py-0.5 rounded border border-brand-200">
                      Order #{idx + 1}
                    </span>
                  </td>
                  <td className="py-2.5 px-3 font-bold text-slate-900">{item.job_id}</td>
                  <td className="py-2.5 px-3 font-sans font-medium text-slate-700">{item.job_type}</td>
                  <td className="py-2.5 px-3 font-medium text-slate-600">{item.resource_id}</td>
                  <td className="py-2.5 px-3 font-bold text-brand-600">{item.cpu_cores} Cores</td>
                  <td className="py-2.5 px-3 font-medium text-emerald-600">
                    {item.memory_mb >= 1024 ? `${(item.memory_mb / 1024.0).toFixed(1)} GB` : `${item.memory_mb} MB`}
                  </td>
                  <td className="py-2.5 px-3 font-bold text-indigo-600">{item.gpu_units} GPU</td>
                  <td className="py-2.5 px-3 text-slate-700">
                    {item.arrival_time}s → <span className="font-bold">{item.start_time}s</span> → {item.finish_time}s
                  </td>
                  <td className="py-2.5 px-3">{item.runtime}s</td>
                  <td className="py-2.5 px-3 text-amber-600">{item.waiting_time}s</td>
                  <td className="py-2.5 px-3 font-sans">
                    <span className={`px-2 py-0.5 rounded text-[10px] font-bold ${
                      item.sla_status === 'MET' ? 'bg-emerald-50 text-emerald-700 border border-emerald-200' : 'bg-rose-50 text-rose-700 border border-rose-200'
                    }`}>
                      {item.sla_status}
                    </span>
                  </td>
                  <td className="py-2.5 px-3 text-slate-900">${item.cost_budget}</td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </div>

      {/* Comparison Charts */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* Resource Utilization Comparison Bar Chart */}
        <div className="bg-white border border-slate-200 rounded-xl p-5 shadow-xs">
          <h3 className="text-sm font-bold text-slate-900 mb-1">Resource Utilization (%)</h3>
          <p className="text-xs text-slate-500 mb-4">CPU, RAM, and GPU cluster active occupancy</p>
          <div className="h-72">
            <ResponsiveContainer width="100%" height="100%">
              <BarChart data={summary} margin={{ top: 10, right: 10, left: -20, bottom: 0 }}>
                <CartesianGrid strokeDasharray="3 3" vertical={false} stroke="#f1f5f9" />
                <XAxis dataKey="algorithm" tick={{ fontSize: 10, fill: '#64748b' }} />
                <YAxis tick={{ fontSize: 10, fill: '#64748b' }} domain={[0, 100]} />
                <Tooltip contentStyle={{ fontSize: '12px', borderRadius: '8px' }} />
                <Legend wrapperStyle={{ fontSize: '11px' }} />
                <Bar dataKey="cpu_utilization" name="CPU Util %" fill="#3b82f6" radius={[4, 4, 0, 0]} />
                <Bar dataKey="memory_utilization" name="RAM Util %" fill="#10b981" radius={[4, 4, 0, 0]} />
                <Bar dataKey="gpu_utilization" name="GPU Util %" fill="#6366f1" radius={[4, 4, 0, 0]} />
              </BarChart>
            </ResponsiveContainer>
          </div>
        </div>

        {/* SLA Violation Rate & Total Cost Bar Chart */}
        <div className="bg-white border border-slate-200 rounded-xl p-5 shadow-xs">
          <h3 className="text-sm font-bold text-slate-900 mb-1">SLA Violation Rate (%) & Total Cost ($)</h3>
          <p className="text-xs text-slate-500 mb-4">Lower percentages and costs indicate superior SLA compliance</p>
          <div className="h-72">
            <ResponsiveContainer width="100%" height="100%">
              <BarChart data={summary} margin={{ top: 10, right: 10, left: -20, bottom: 0 }}>
                <CartesianGrid strokeDasharray="3 3" vertical={false} stroke="#f1f5f9" />
                <XAxis dataKey="algorithm" tick={{ fontSize: 10, fill: '#64748b' }} />
                <YAxis tick={{ fontSize: 10, fill: '#64748b' }} />
                <Tooltip contentStyle={{ fontSize: '12px', borderRadius: '8px' }} />
                <Legend wrapperStyle={{ fontSize: '11px' }} />
                <Bar dataKey="sla_violation_rate" name="SLA Violation %" fill="#ef4444" radius={[4, 4, 0, 0]} />
                <Bar dataKey="total_cost" name="Total Cost ($)" fill="#f59e0b" radius={[4, 4, 0, 0]} />
              </BarChart>
            </ResponsiveContainer>
          </div>
        </div>
      </div>

      {/* Comprehensive Benchmark Table */}
      <div className="bg-white border border-slate-200 rounded-xl p-5 shadow-xs">
        <h3 className="text-sm font-bold text-slate-900 mb-3">Complete Side-by-Side Algorithm Ranking Matrix</h3>
        <div className="overflow-x-auto">
          <table className="w-full text-left border-collapse">
            <thead>
              <tr className="bg-slate-100 text-[11px] font-semibold text-slate-600 uppercase border-b border-slate-200">
                <th className="py-2.5 px-3">Rank</th>
                <th className="py-2.5 px-3">Algorithm</th>
                <th className="py-2.5 px-3">Exec Time (s)</th>
                <th className="py-2.5 px-3">Makespan (s)</th>
                <th className="py-2.5 px-3">Avg Wait (s)</th>
                <th className="py-2.5 px-3">Overall Util %</th>
                <th className="py-2.5 px-3">SLA Violation %</th>
                <th className="py-2.5 px-3">Total Cost ($)</th>
                <th className="py-2.5 px-3">Score</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-slate-100 text-xs">
              {summary.map((r) => (
                <tr key={r.algorithm} className="hover:bg-slate-50">
                  <td className="py-2.5 px-3 font-mono font-bold text-slate-900">#{r.rank}</td>
                  <td className="py-2.5 px-3 font-semibold text-slate-900">{r.algorithm}</td>
                  <td className="py-2.5 px-3 font-mono text-slate-500">{r.execution_time_sec}s</td>
                  <td className="py-2.5 px-3 font-mono font-semibold">{r.makespan}s</td>
                  <td className="py-2.5 px-3 font-mono">{r.avg_waiting_time}s</td>
                  <td className="py-2.5 px-3 font-mono text-brand-600 font-bold">{r.overall_utilization}%</td>
                  <td className={`py-2.5 px-3 font-mono font-semibold ${r.sla_violation_rate > 10 ? 'text-rose-600' : 'text-emerald-600'}`}>
                    {r.sla_violation_rate}%
                  </td>
                  <td className="py-2.5 px-3 font-mono">${r.total_cost}</td>
                  <td className="py-2.5 px-3">
                    <span className="bg-brand-50 text-brand-700 font-bold px-2 py-0.5 rounded text-[11px] border border-brand-100">
                      {r.efficiency_score}
                    </span>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </div>
    </div>
  );
}
