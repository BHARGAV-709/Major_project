import React, { useState } from 'react';

export default function GanttChartComponent({ timeline = [] }) {
  const [selectedServer, setSelectedServer] = useState('ALL');

  if (!timeline || timeline.length === 0) {
    return (
      <div className="bg-white border border-slate-200 rounded-xl p-8 text-center text-slate-400 text-sm">
        No simulation timeline data available. Run a simulation to display the Gantt chart.
      </div>
    );
  }

  const maxTime = Math.max(...timeline.map(t => t.finish_time), 1.0);
  const servers = Array.from(new Set(timeline.map(t => t.server_id || 1))).sort((a,b) => a - b);

  const filteredTimeline = selectedServer === 'ALL' 
    ? timeline 
    : timeline.filter(t => (t.server_id || 1) === parseInt(selectedServer));

  const getJobColor = (jobType) => {
    switch (jobType) {
      case 'ML Training': return 'bg-indigo-500 border-indigo-600 text-white';
      case 'Data Pipeline': return 'bg-brand-500 border-brand-600 text-white';
      case 'BI Query': return 'bg-emerald-500 border-emerald-600 text-white';
      case 'Batch Analytics': return 'bg-amber-500 border-amber-600 text-white';
      default: return 'bg-slate-600 border-slate-700 text-white';
    }
  };

  return (
    <div className="bg-white border border-slate-200 rounded-xl p-5 shadow-xs">
      <div className="flex items-center justify-between mb-4 border-b border-slate-100 pb-3">
        <div>
          <h3 className="text-sm font-bold text-slate-900">Cluster Resource Gantt Timeline</h3>
          <p className="text-xs text-slate-500">Visualizing Job Execution Slots Across Cluster Server Nodes</p>
        </div>

        {/* Server filter */}
        <div className="flex items-center gap-2 text-xs">
          <span className="text-slate-500 font-medium">Filter Server:</span>
          <select 
            value={selectedServer}
            onChange={(e) => setSelectedServer(e.target.value)}
            className="border border-slate-200 rounded-md px-2.5 py-1 text-xs text-slate-700 focus:outline-none focus:border-brand-500 bg-white"
          >
            <option value="ALL">All Server Nodes ({servers.length})</option>
            {servers.map(s => (
              <option key={s} value={s}>Server #{s}</option>
            ))}
          </select>
        </div>
      </div>

      {/* Legend */}
      <div className="flex flex-wrap items-center gap-4 mb-4 text-xs font-medium">
        <div className="flex items-center gap-1.5"><div className="w-3 h-3 rounded bg-indigo-500" /> ML Training</div>
        <div className="flex items-center gap-1.5"><div className="w-3 h-3 rounded bg-brand-500" /> Data Pipeline</div>
        <div className="flex items-center gap-1.5"><div className="w-3 h-3 rounded bg-emerald-500" /> BI Query</div>
        <div className="flex items-center gap-1.5"><div className="w-3 h-3 rounded bg-amber-500" /> Batch Analytics</div>
      </div>

      {/* Gantt Canvas */}
      <div className="overflow-x-auto">
        <div className="min-w-[800px] space-y-3">
          {/* Time axis header */}
          <div className="flex border-b border-slate-200 pb-1 text-[11px] text-slate-400 font-mono">
            <div className="w-24 shrink-0">Server Node</div>
            <div className="flex-1 flex justify-between">
              <span>0s</span>
              <span>{Math.round(maxTime * 0.25)}s</span>
              <span>{Math.round(maxTime * 0.5)}s</span>
              <span>{Math.round(maxTime * 0.75)}s</span>
              <span>{Math.round(maxTime)}s</span>
            </div>
          </div>

          {/* Rows by Server */}
          {servers.filter(s => selectedServer === 'ALL' || s === parseInt(selectedServer)).map(serverId => {
            const serverJobs = filteredTimeline.filter(t => (t.server_id || 1) === serverId);
            return (
              <div key={serverId} className="flex items-center gap-2 group hover:bg-slate-50 p-1 rounded-lg transition-colors">
                <div className="w-24 shrink-0 text-xs font-semibold text-slate-700 font-mono">
                  Server #{serverId}
                </div>
                <div className="flex-1 bg-slate-100 rounded-md h-8 relative border border-slate-200 overflow-hidden">
                  {serverJobs.map((item, idx) => {
                    const leftPct = (item.start_time / maxTime) * 100;
                    const widthPct = Math.max(0.5, ((item.finish_time - item.start_time) / maxTime) * 100);
                    return (
                      <div
                        key={idx}
                        style={{ left: `${leftPct}%`, width: `${widthPct}%` }}
                        className={`absolute top-0 bottom-0 border-l border-r px-1 flex items-center justify-center text-[10px] font-medium truncate cursor-pointer transition-transform hover:scale-y-105 z-10 ${getJobColor(item.job_type)}`}
                        title={`Job ID: ${item.job_id}\nType: ${item.job_type}\nStart: ${item.start_time}s\nFinish: ${item.finish_time}s\nRuntime: ${item.runtime}s\nCPU: ${item.cpu}, RAM: ${item.memory_mb}MB\nSLA: ${item.sla_violated ? 'VIOLATED' : 'MET'}`}
                      >
                        {item.job_id}
                      </div>
                    );
                  })}
                </div>
              </div>
            );
          })}
        </div>
      </div>
    </div>
  );
}
