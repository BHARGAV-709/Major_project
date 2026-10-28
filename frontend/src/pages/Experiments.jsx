import React, { useState } from 'react';
import { FlaskConical, Play, CheckCircle2, Layers } from 'lucide-react';
import { runBenchmark } from '../services/api';
import { useNavigate } from 'react-router-dom';

const ALL_ALGOS = ["FCFS", "SJF", "Priority", "EDF", "Greedy", "GA", "PSO", "SA", "Q-Learning", "DQN"];

export default function Experiments() {
  const [scenario, setScenario] = useState('MEDIUM');
  const [numJobs, setNumJobs] = useState(100);
  const [selectedAlgos, setSelectedAlgos] = useState(ALL_ALGOS);
  
  const [loading, setLoading] = useState(false);
  const [statusMsg, setStatusMsg] = useState('');
  const [errorMsg, setErrorMsg] = useState(null);
  const navigate = useNavigate();

  const toggleAlgo = (algo) => {
    if (selectedAlgos.includes(algo)) {
      if (selectedAlgos.length > 1) {
        setSelectedAlgos(selectedAlgos.filter(a => a !== algo));
      }
    } else {
      setSelectedAlgos([...selectedAlgos, algo]);
    }
  };

  const handleRunExperiment = async () => {
    setLoading(true);
    setStatusMsg('Running multi-algorithm benchmark experiment...');
    setErrorMsg(null);
    try {
      const res = await runBenchmark({
        scenario: scenario,
        max_jobs: numJobs,
        algorithms: selectedAlgos
      });
      setStatusMsg('Benchmark completed successfully!');
      // Navigate to Results page after short delay
      setTimeout(() => {
        navigate('/results', { state: { benchmarkSummary: res.data } });
      }, 800);
    } catch (err) {
      const detail = err.response?.data?.detail || err.message || 'Experiment run failed.';
      setErrorMsg(detail);
      setStatusMsg('');
      console.error(err);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="space-y-6">
      <div className="flex flex-col md:flex-row md:items-center justify-between gap-4 bg-white border border-slate-200 p-6 rounded-xl shadow-xs">
        <div>
          <h1 className="text-xl font-bold text-slate-900 tracking-tight">Multi-Algorithm Benchmark Suite</h1>
          <p className="text-xs text-slate-500 mt-1">
            Execute fair comparative experiment across Heuristics, Metaheuristics, and RL under identical conditions
          </p>
        </div>
        <button
          onClick={handleRunExperiment}
          disabled={loading}
          className="flex items-center gap-2 bg-brand-600 hover:bg-brand-700 text-white text-xs font-semibold px-6 py-2.5 rounded-lg transition-all shadow-sm shadow-brand-500/20 disabled:opacity-50"
        >
          <FlaskConical className={`w-4 h-4 ${loading ? 'animate-spin' : ''}`} />
          <span>{loading ? 'Executing Suite...' : 'Launch Benchmark Suite'}</span>
        </button>
      </div>

      {statusMsg && (
        <div className="bg-brand-50 border border-brand-200 text-brand-700 px-4 py-3 rounded-xl text-xs font-medium flex items-center gap-2">
          <CheckCircle2 className="w-4 h-4 text-brand-600" />
          <span>{statusMsg}</span>
        </div>
      )}

      {errorMsg && (
        <div className="bg-rose-50 border border-rose-200 text-rose-800 px-4 py-3 rounded-xl text-xs font-medium flex items-center gap-2">
          <span>{errorMsg}</span>
        </div>
      )}

      {/* Select Algorithms */}
      <div className="bg-white border border-slate-200 rounded-xl p-5 shadow-xs space-y-3">
        <h3 className="text-sm font-bold text-slate-900">Include Algorithms in Benchmark</h3>
        <div className="flex flex-wrap gap-2">
          {ALL_ALGOS.map((algo) => {
            const isSelected = selectedAlgos.includes(algo);
            return (
              <button
                key={algo}
                onClick={() => toggleAlgo(algo)}
                className={`px-3.5 py-1.5 rounded-lg text-xs font-semibold transition-all border ${
                  isSelected
                    ? 'bg-brand-50 text-brand-700 border-brand-300 ring-1 ring-brand-300'
                    : 'bg-slate-50 text-slate-500 border-slate-200 hover:bg-slate-100'
                }`}
              >
                {isSelected ? '✓ ' : '+ '}{algo}
              </button>
            );
          })}
        </div>
      </div>

      {/* Scenario & Job Parameters */}
      <div className="bg-white border border-slate-200 rounded-xl p-5 shadow-xs grid grid-cols-1 md:grid-cols-2 gap-6">
        <div>
          <label className="text-xs font-semibold text-slate-700 block mb-2">Workload Scenario</label>
          <select 
            value={scenario} 
            onChange={(e) => setScenario(e.target.value)}
            className="w-full border border-slate-300 rounded-lg p-2.5 text-xs text-slate-900 bg-white"
          >
            <option value="DATASET">Google Cluster Workload Trace (Raw Dataset)</option>
            <option value="LIGHT">Light Contention Scenario</option>
            <option value="MEDIUM">Medium Contention Scenario</option>
            <option value="HEAVY">Heavy Contention Scenario</option>
            <option value="BURSTY">Bursty Traffic Spike Scenario</option>
            <option value="OVERLOADED">Overloaded Cluster Scenario</option>
          </select>
        </div>

        <div>
          <label className="text-xs font-semibold text-slate-700 block mb-2">Total Jobs per Experiment</label>
          <input 
            type="number" 
            value={numJobs} 
            onChange={(e) => setNumJobs(parseInt(e.target.value) || 50)} 
            className="w-full border border-slate-300 rounded-lg p-2.5 text-xs text-slate-900"
          />
        </div>
      </div>
    </div>
  );
}
