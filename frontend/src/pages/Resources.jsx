import React, { useState } from 'react';
import { Cpu, HardDrive, Zap, Server, CheckCircle2, ShieldAlert } from 'lucide-react';

export default function Resources() {
  const [cpuCores, setCpuCores] = useState(40);
  const [memoryGb, setMemoryGb] = useState(256);
  const [gpuUnits, setGpuUnits] = useState(8);
  const [bandwidthMbps, setBandwidthMbps] = useState(10000);

  // Test Job Feasibility Checker
  const [testCpu, setTestCpu] = useState(8);
  const [testRamGb, setTestRamGb] = useState(32);
  const [testGpu, setTestGpu] = useState(2);

  const isFeasible = (testCpu <= cpuCores) && (testRamGb <= memoryGb) && (testGpu <= gpuUnits);

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex flex-col md:flex-row md:items-center justify-between gap-4 bg-white border border-slate-200 p-6 rounded-xl shadow-xs">
        <div>
          <h1 className="text-xl font-bold text-slate-900 tracking-tight">Cluster Resource Manager</h1>
          <p className="text-xs text-slate-500 mt-1">
            Configure enterprise cluster multi-dimensional capacity (CPU Cores, RAM, GPU Units, Network Bandwidth)
          </p>
        </div>
      </div>

      {/* Cluster Resource Configuration Controls */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
        <div className="bg-white border border-slate-200 rounded-xl p-5 shadow-xs">
          <div className="flex items-center gap-2 mb-3">
            <Cpu className="w-5 h-5 text-brand-600" />
            <h3 className="text-sm font-bold text-slate-900">Total CPU Cores</h3>
          </div>
          <input 
            type="range" 
            min="8" 
            max="128" 
            value={cpuCores} 
            onChange={(e) => setCpuCores(parseInt(e.target.value))}
            className="w-full h-2 bg-slate-200 rounded-lg appearance-none cursor-pointer accent-brand-600"
          />
          <div className="flex justify-between items-center mt-3 text-xs">
            <span className="text-slate-500 font-medium">Capacity</span>
            <span className="font-bold text-slate-900 text-sm font-mono">{cpuCores} Cores</span>
          </div>
        </div>

        <div className="bg-white border border-slate-200 rounded-xl p-5 shadow-xs">
          <div className="flex items-center gap-2 mb-3">
            <HardDrive className="w-5 h-5 text-emerald-600" />
            <h3 className="text-sm font-bold text-slate-900">Total RAM Memory</h3>
          </div>
          <input 
            type="range" 
            min="32" 
            max="1024" 
            step="32"
            value={memoryGb} 
            onChange={(e) => setMemoryGb(parseInt(e.target.value))}
            className="w-full h-2 bg-slate-200 rounded-lg appearance-none cursor-pointer accent-emerald-600"
          />
          <div className="flex justify-between items-center mt-3 text-xs">
            <span className="text-slate-500 font-medium">Capacity</span>
            <span className="font-bold text-slate-900 text-sm font-mono">{memoryGb} GB</span>
          </div>
        </div>

        <div className="bg-white border border-slate-200 rounded-xl p-5 shadow-xs">
          <div className="flex items-center gap-2 mb-3">
            <Zap className="w-5 h-5 text-indigo-600" />
            <h3 className="text-sm font-bold text-slate-900">GPU Accelerators</h3>
          </div>
          <input 
            type="range" 
            min="0" 
            max="32" 
            value={gpuUnits} 
            onChange={(e) => setGpuUnits(parseInt(e.target.value))}
            className="w-full h-2 bg-slate-200 rounded-lg appearance-none cursor-pointer accent-indigo-600"
          />
          <div className="flex justify-between items-center mt-3 text-xs">
            <span className="text-slate-500 font-medium">Capacity</span>
            <span className="font-bold text-slate-900 text-sm font-mono">{gpuUnits} Units</span>
          </div>
        </div>
      </div>

      {/* Interactive Resource Feasibility Checker */}
      <div className="bg-white border border-slate-200 rounded-xl p-5 shadow-xs space-y-4">
        <h3 className="text-sm font-bold text-slate-900 border-b border-slate-100 pb-2">
          Resource Allocation Feasibility Verifier
        </h3>
        <p className="text-xs text-slate-500">
          Verify whether a candidate analytics job's resource demands can fit within current cluster capacity.
        </p>

        <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
          <div>
            <label className="text-xs font-semibold text-slate-700 block mb-1">Requested CPU Cores</label>
            <input 
              type="number" 
              value={testCpu} 
              onChange={(e) => setTestCpu(parseInt(e.target.value) || 0)}
              className="w-full border border-slate-300 rounded-lg p-2 text-xs font-mono"
            />
          </div>
          <div>
            <label className="text-xs font-semibold text-slate-700 block mb-1">Requested RAM (GB)</label>
            <input 
              type="number" 
              value={testRamGb} 
              onChange={(e) => setTestRamGb(parseInt(e.target.value) || 0)}
              className="w-full border border-slate-300 rounded-lg p-2 text-xs font-mono"
            />
          </div>
          <div>
            <label className="text-xs font-semibold text-slate-700 block mb-1">Requested GPU Units</label>
            <input 
              type="number" 
              value={testGpu} 
              onChange={(e) => setTestGpu(parseInt(e.target.value) || 0)}
              className="w-full border border-slate-300 rounded-lg p-2 text-xs font-mono"
            />
          </div>
        </div>

        <div className={`p-4 rounded-xl border flex items-center justify-between text-xs font-semibold ${
          isFeasible 
            ? 'bg-emerald-50 border-emerald-200 text-emerald-800' 
            : 'bg-rose-50 border-rose-200 text-rose-800'
        }`}>
          <div className="flex items-center gap-2">
            {isFeasible ? <CheckCircle2 className="w-5 h-5 text-emerald-600" /> : <ShieldAlert className="w-5 h-5 text-rose-600" />}
            <span>{isFeasible ? 'RESOURCE ALLOCATION FEASIBLE: Job fits in cluster.' : 'INFEASIBLE ALLOCATION: Insufficient cluster capacity.'}</span>
          </div>
          <span className="font-mono">
            Available: {cpuCores - testCpu} CPU | {memoryGb - testRamGb}GB RAM | {gpuUnits - testGpu} GPU
          </span>
        </div>
      </div>
    </div>
  );
}
