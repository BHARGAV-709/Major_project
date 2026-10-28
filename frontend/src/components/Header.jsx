import React, { useState, useEffect } from 'react';
import { Activity, CheckCircle2, Server, Bell, RefreshCw } from 'lucide-react';
import { getSystemStatus } from '../services/api';

export default function Header() {
  const [status, setStatus] = useState(null);
  const [loading, setLoading] = useState(false);

  const fetchStatus = async () => {
    setLoading(true);
    try {
      const res = await getSystemStatus();
      setStatus(res.data);
    } catch (err) {
      setStatus({ status: 'OFFLINE' });
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchStatus();
  }, []);

  return (
    <header className="h-16 bg-white border-b border-slate-200 px-6 flex items-center justify-between sticky top-0 z-20 shadow-2xs">
      <div>
        <h2 className="text-sm font-semibold text-slate-900 tracking-tight">
          Resource Allocation & Scheduling Optimization Engine
        </h2>
        <p className="text-xs text-slate-500">Discrete-Event Cluster Simulation & Multi-Algorithm Benchmarking</p>
      </div>

      <div className="flex items-center gap-4">
        {/* Connection Status Badge */}
        <div className="flex items-center gap-2 bg-slate-50 border border-slate-200 px-3 py-1.5 rounded-full text-xs">
          <div className={`w-2 h-2 rounded-full ${status?.status === 'ONLINE' ? 'bg-emerald-500 animate-pulse' : 'bg-rose-500'}`} />
          <span className="font-medium text-slate-700">
            Backend: {status?.status || 'Checking...'}
          </span>
          <button 
            onClick={fetchStatus} 
            className="text-slate-400 hover:text-slate-600 transition-colors ml-1"
            title="Refresh connection"
          >
            <RefreshCw className={`w-3 h-3 ${loading ? 'animate-spin' : ''}`} />
          </button>
        </div>

        {/* Dataset Status Badge */}
        <div className="hidden md:flex items-center gap-2 bg-brand-50 border border-brand-100 text-brand-700 px-3 py-1.5 rounded-full text-xs font-medium">
          <Server className="w-3.5 h-3.5" />
          <span>Cluster Capacity: 40 CPU / 256GB / 8 GPU</span>
        </div>
      </div>
    </header>
  );
}
