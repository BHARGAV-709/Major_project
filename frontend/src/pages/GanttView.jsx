import React, { useState, useEffect } from 'react';
import GanttChartComponent from '../components/GanttChartComponent';
import { runSimulation } from '../services/api';
import { PlayCircle, Filter } from 'lucide-react';

export default function GanttView() {
  const [algorithm, setAlgorithm] = useState('Q-Learning');
  const [scenario, setScenario] = useState('MEDIUM');
  const [numJobs, setNumJobs] = useState(40);
  
  const [loading, setLoading] = useState(false);
  const [timelineData, setTimelineData] = useState([]);
  const [errorMsg, setErrorMsg] = useState(null);

  useEffect(() => {
    fetchTimeline();
  }, []);

  const fetchTimeline = async () => {
    setLoading(true);
    setErrorMsg(null);
    try {
      const res = await runSimulation({
        algorithm: algorithm,
        scenario: scenario,
        max_jobs: numJobs
      });
      setTimelineData(res.data.timeline || []);
    } catch (err) {
      console.error(err);
      const detail = err.response?.data?.detail || err.message || 'Failed to fetch timeline.';
      setErrorMsg(detail);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="space-y-6">
      <div className="flex flex-col md:flex-row md:items-center justify-between gap-4 bg-white border border-slate-200 p-6 rounded-xl shadow-xs">
        <div>
          <h1 className="text-xl font-bold text-slate-900 tracking-tight">Interactive Gantt Chart Studio</h1>
          <p className="text-xs text-slate-500 mt-1">
            Visualizing Job Allocation Slots & Execution Spans Across Multi-Server Cluster Nodes
          </p>
        </div>

        <div className="flex items-center gap-3">
          <select 
            value={algorithm} 
            onChange={(e) => setAlgorithm(e.target.value)}
            className="border border-slate-300 rounded-lg p-2 text-xs font-semibold bg-white"
          >
            {["FCFS", "SJF", "Priority", "EDF", "Greedy", "GA", "PSO", "SA", "Q-Learning", "DQN"].map(a => (
              <option key={a} value={a}>{a}</option>
            ))}
          </select>
          <button
            onClick={fetchTimeline}
            disabled={loading}
            className="flex items-center gap-2 bg-brand-600 hover:bg-brand-700 text-white text-xs font-semibold px-4 py-2 rounded-lg transition-all shadow-xs"
          >
            <PlayCircle className="w-4 h-4" />
            <span>Generate Gantt</span>
          </button>
        </div>
      </div>

      {errorMsg && (
        <div className="bg-rose-50 border border-rose-200 text-rose-800 p-4 rounded-xl text-xs flex items-center gap-2">
          <span>{errorMsg}</span>
        </div>
      )}

      <GanttChartComponent timeline={timelineData} />
    </div>
  );
}
