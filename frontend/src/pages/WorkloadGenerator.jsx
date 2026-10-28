import React, { useState } from 'react';
import { Layers, Play, Settings, Cpu, HardDrive, Zap } from 'lucide-react';
import { generateWorkload } from '../services/api';

const SCENARIOS = [
  { id: 'LIGHT', name: 'Light Load', desc: 'Low resource contention, long inter-arrival times' },
  { id: 'MEDIUM', name: 'Medium Load', desc: 'Balanced operational resource contention' },
  { id: 'HEAVY', name: 'Heavy Load', desc: 'High CPU/RAM demand and tight SLA deadlines' },
  { id: 'BURSTY', name: 'Bursty Traffic', desc: 'Sudden high-density job arrival spikes' },
  { id: 'OVERLOADED', name: 'Overloaded Cluster', desc: 'Workload demand exceeds total cluster capacity' },
];

export default function WorkloadGenerator() {
  const [scenario, setScenario] = useState('MEDIUM');
  const [numJobs, setNumJobs] = useState(100);
  const [seed, setSeed] = useState(42);
  
  const [loading, setLoading] = useState(false);
  const [generatedData, setGeneratedData] = useState(null);
  const [errorMsg, setErrorMsg] = useState(null);

  const handleGenerate = async () => {
    setLoading(true);
    setErrorMsg(null);
    try {
      const res = await generateWorkload(scenario, numJobs, seed);
      setGeneratedData(res.data);
    } catch (err) {
      console.error('Failed to generate workload', err);
      const detail = err.response?.data?.detail || err.message || 'Failed to generate workload.';
      setErrorMsg(detail);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex flex-col md:flex-row md:items-center justify-between gap-4 bg-white border border-slate-200 p-6 rounded-xl shadow-xs">
        <div>
          <h1 className="text-xl font-bold text-slate-900 tracking-tight">Synthetic Workload Scenario Generator</h1>
          <p className="text-xs text-slate-500 mt-1">
            Generate controlled experimentation scenarios: LIGHT, MEDIUM, HEAVY, BURSTY, OVERLOADED
          </p>
        </div>
        <button
          onClick={handleGenerate}
          disabled={loading}
          className="flex items-center gap-2 bg-brand-600 hover:bg-brand-700 text-white text-xs font-semibold px-5 py-2.5 rounded-lg transition-all shadow-sm shadow-brand-500/20 disabled:opacity-50"
        >
          <Play className={`w-4 h-4 ${loading ? 'animate-spin' : ''}`} />
          <span>Generate Workload</span>
        </button>
      </div>

      {/* Scenario Selection Grid */}
      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-5 gap-3">
        {SCENARIOS.map((sc) => (
          <div
            key={sc.id}
            onClick={() => setScenario(sc.id)}
            className={`p-4 rounded-xl border cursor-pointer transition-all ${
              scenario === sc.id
                ? 'bg-brand-50 border-brand-500 shadow-sm ring-1 ring-brand-500'
                : 'bg-white border-slate-200 hover:border-slate-300 hover:bg-slate-50'
            }`}
          >
            <div className="text-xs font-bold text-slate-900">{sc.name}</div>
            <div className="text-[11px] text-slate-500 mt-1 line-clamp-2">{sc.desc}</div>
          </div>
        ))}
      </div>

      {/* Parameter Controls */}
      <div className="bg-white border border-slate-200 rounded-xl p-5 shadow-xs grid grid-cols-1 md:grid-cols-3 gap-6">
        <div>
          <label className="text-xs font-semibold text-slate-700 block mb-2">Number of Jobs</label>
          <input 
            type="number" 
            value={numJobs} 
            onChange={(e) => setNumJobs(parseInt(e.target.value) || 50)} 
            className="w-full border border-slate-300 rounded-lg p-2.5 text-xs text-slate-900"
          />
        </div>
        <div>
          <label className="text-xs font-semibold text-slate-700 block mb-2">Random Seed (Reproducibility)</label>
          <input 
            type="number" 
            value={seed} 
            onChange={(e) => setSeed(parseInt(e.target.value) || 42)} 
            className="w-full border border-slate-300 rounded-lg p-2.5 text-xs text-slate-900"
          />
        </div>
        <div>
          <label className="text-xs font-semibold text-slate-700 block mb-2">Workload Types Included</label>
          <div className="text-xs text-slate-500 pt-2 font-medium">
            Data Pipelines, BI Queries, ML Training, Batch Jobs
          </div>
        </div>
      </div>

      {/* Error Alert */}
      {errorMsg && (
        <div className="bg-rose-50 border border-rose-200 text-rose-800 p-4 rounded-xl text-xs flex items-center gap-2">
          <span>{errorMsg}</span>
        </div>
      )}

      {/* Generated Jobs Preview Table */}
      {generatedData && (
        <div className="bg-white border border-slate-200 rounded-xl p-5 shadow-xs">
          <div className="flex items-center justify-between mb-4 border-b border-slate-100 pb-3">
            <div>
              <h3 className="text-sm font-bold text-slate-900">Generated Workload Jobs ({generatedData.count})</h3>
              <p className="text-xs text-slate-500">Scenario: <span className="font-semibold text-brand-600">{generatedData.scenario}</span></p>
            </div>
          </div>

          <div className="overflow-x-auto max-h-96">
            <table className="w-full text-left border-collapse min-w-[900px]">
              <thead className="sticky top-0 bg-slate-100 text-[11px] font-semibold text-slate-600 uppercase border-b border-slate-200">
                <tr>
                  <th className="py-2.5 px-3">Job ID</th>
                  <th className="py-2.5 px-3">Type</th>
                  <th className="py-2.5 px-3">Arrival (s)</th>
                  <th className="py-2.5 px-3">CPU Cores</th>
                  <th className="py-2.5 px-3">RAM (MB)</th>
                  <th className="py-2.5 px-3">GPU Units</th>
                  <th className="py-2.5 px-3">Runtime (s)</th>
                  <th className="py-2.5 px-3">Priority</th>
                  <th className="py-2.5 px-3">Deadline (s)</th>
                  <th className="py-2.5 px-3">SLA Class</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-slate-100 text-xs font-mono">
                {generatedData.jobs?.slice(0, 50).map((j) => (
                  <tr key={j.job_id} className="hover:bg-slate-50">
                    <td className="py-2 px-3 font-bold text-slate-900">{j.job_id}</td>
                    <td className="py-2 px-3 font-sans font-medium text-slate-700">{j.job_type}</td>
                    <td className="py-2 px-3">{j.arrival_time}s</td>
                    <td className="py-2 px-3 font-semibold text-brand-600">{j.cpu_cores}</td>
                    <td className="py-2 px-3">{j.memory_mb}</td>
                    <td className="py-2 px-3 text-indigo-600 font-bold">{j.gpu_units}</td>
                    <td className="py-2 px-3">{j.runtime}s</td>
                    <td className="py-2 px-3">{j.priority}</td>
                    <td className="py-2 px-3 text-amber-600">{j.deadline}s</td>
                    <td className="py-2 px-3 font-sans font-medium text-slate-600">{j.sla_class}</td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </div>
      )}
    </div>
  );
}
