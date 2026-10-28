import React, { useState } from 'react';
import { SlidersHorizontal, CheckCircle2, Play, AlertCircle, FileCheck, Layers } from 'lucide-react';
import { runPreprocessing } from '../services/api';

export default function Preprocessing() {
  const [missingStrategy, setMissingStrategy] = useState('impute_mean');
  const [outlierMethod, setOutlierMethod] = useState('iqr');
  const [scaleMethod, setScaleMethod] = useState('minmax');
  
  const [loading, setLoading] = useState(false);
  const [result, setResult] = useState(null);
  const [errorMsg, setErrorMsg] = useState(null);

  const handleRunPipeline = async () => {
    setLoading(true);
    setErrorMsg(null);
    try {
      const res = await runPreprocessing({
        missing_strategy: missingStrategy,
        outlier_method: outlierMethod,
        scale_method: scaleMethod
      });
      setResult(res.data);
    } catch (err) {
      console.error('Failed to run preprocessing pipeline', err);
      const detail = err.response?.data?.detail || err.message || 'Preprocessing pipeline failed.';
      setErrorMsg(detail);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="space-y-6">
      {/* Title */}
      <div className="flex flex-col md:flex-row md:items-center justify-between gap-4 bg-white border border-slate-200 p-6 rounded-xl shadow-xs">
        <div>
          <h1 className="text-xl font-bold text-slate-900 tracking-tight">Data Preprocessing & Cleaning Pipeline</h1>
          <p className="text-xs text-slate-500 mt-1">
            8-Step Data Pipeline: Load → Explore → Missing Values → Duplicates → Outliers → Encoding → Scaling → Validation
          </p>
        </div>
        <button
          onClick={handleRunPipeline}
          disabled={loading}
          className="flex items-center gap-2 bg-brand-600 hover:bg-brand-700 text-white text-xs font-semibold px-5 py-2.5 rounded-lg transition-all shadow-sm shadow-brand-500/20 disabled:opacity-50"
        >
          <Play className={`w-4 h-4 ${loading ? 'animate-spin' : ''}`} />
          <span>{loading ? 'Processing...' : 'Run 8-Step Preprocessing'}</span>
        </button>
      </div>

      {/* Configurations */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
        <div className="bg-white border border-slate-200 rounded-xl p-5 shadow-xs">
          <h3 className="text-xs font-bold text-slate-900 uppercase tracking-wider mb-2">Step 3: Missing Value Handling</h3>
          <select 
            value={missingStrategy} 
            onChange={(e) => setMissingStrategy(e.target.value)}
            className="w-full border border-slate-300 rounded-lg p-2.5 text-xs text-slate-700 bg-white"
          >
            <option value="impute_mean">Impute Numeric with Mean / Mode</option>
            <option value="impute_median">Impute Numeric with Median</option>
            <option value="drop">Drop Rows with Missing Values</option>
          </select>
        </div>

        <div className="bg-white border border-slate-200 rounded-xl p-5 shadow-xs">
          <h3 className="text-xs font-bold text-slate-900 uppercase tracking-wider mb-2">Step 5: Outlier Treatment</h3>
          <select 
            value={outlierMethod} 
            onChange={(e) => setOutlierMethod(e.target.value)}
            className="w-full border border-slate-300 rounded-lg p-2.5 text-xs text-slate-700 bg-white"
          >
            <option value="iqr">Interquartile Range (IQR 1.5x Capping)</option>
            <option value="zscore">Z-Score Normalization Capping (&gt;3 Std)</option>
          </select>
        </div>

        <div className="bg-white border border-slate-200 rounded-xl p-5 shadow-xs">
          <h3 className="text-xs font-bold text-slate-900 uppercase tracking-wider mb-2">Step 7: Numerical Feature Scaling</h3>
          <select 
            value={scaleMethod} 
            onChange={(e) => setScaleMethod(e.target.value)}
            className="w-full border border-slate-300 rounded-lg p-2.5 text-xs text-slate-700 bg-white"
          >
            <option value="minmax">MinMax Scaling (0.0 to 1.0)</option>
            <option value="standard">Standard Scaling (Mean 0, Std 1)</option>
          </select>
        </div>
      </div>

      {/* Error Message */}
      {errorMsg && (
        <div className="bg-rose-50 border border-rose-200 text-rose-800 p-4 rounded-xl text-xs flex items-center gap-2">
          <AlertCircle className="w-4 h-4 text-rose-600 shrink-0" />
          <span>{errorMsg}</span>
        </div>
      )}

      {/* Execution Results Summary */}
      {result && (
        <div className="space-y-6">
          <div className="bg-emerald-50 border border-emerald-200 rounded-xl p-4 flex items-center justify-between text-xs text-emerald-800">
            <div className="flex items-center gap-2 font-semibold">
              <CheckCircle2 className="w-5 h-5 text-emerald-600" />
              <span>Pipeline Status: {result.summary.validation.status}</span>
            </div>
            <span className="font-mono bg-white px-2.5 py-1 rounded border border-emerald-200 text-emerald-700">
              Cleaned Rows: {result.summary.cleaned_rows}
            </span>
          </div>

          <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
            <div className="bg-white border border-slate-200 p-4 rounded-xl">
              <div className="text-[11px] font-semibold text-slate-500 uppercase">Missing Values Fixed</div>
              <div className="text-xl font-bold text-slate-900 mt-1">{result.summary.missing_values_handled}</div>
            </div>
            <div className="bg-white border border-slate-200 p-4 rounded-xl">
              <div className="text-[11px] font-semibold text-slate-500 uppercase">Duplicates Removed</div>
              <div className="text-xl font-bold text-slate-900 mt-1">{result.summary.duplicates_removed}</div>
            </div>
            <div className="bg-white border border-slate-200 p-4 rounded-xl">
              <div className="text-[11px] font-semibold text-slate-500 uppercase">CPU Range Check</div>
              <div className="text-xl font-bold text-emerald-600 mt-1">CPU &gt; 0 Valid</div>
            </div>
            <div className="bg-white border border-slate-200 p-4 rounded-xl">
              <div className="text-[11px] font-semibold text-slate-500 uppercase">RAM Range Check</div>
              <div className="text-xl font-bold text-emerald-600 mt-1">RAM &gt; 0 Valid</div>
            </div>
          </div>

          {/* Cleaned Dataset Preview */}
          <div className="bg-white border border-slate-200 rounded-xl p-5 shadow-xs">
            <h3 className="text-sm font-bold text-slate-900 mb-3">Cleaned & Encoded Dataset Sample</h3>
            <div className="overflow-x-auto">
              <table className="w-full text-left border-collapse min-w-[900px]">
                <thead className="bg-slate-100 text-[11px] font-semibold text-slate-600 uppercase border-b border-slate-200">
                  <tr>
                    <th className="py-2.5 px-3">Container_ID</th>
                    <th className="py-2.5 px-3">Tenant_ID</th>
                    <th className="py-2.5 px-3">Requested_CPU</th>
                    <th className="py-2.5 px-3">Requested_Memory_MB</th>
                    <th className="py-2.5 px-3">Execution_Start_Time_ms</th>
                    <th className="py-2.5 px-3">Makespan_ms</th>
                    <th className="py-2.5 px-3">Optimal_Scheduling</th>
                  </tr>
                </thead>
                <tbody className="divide-y divide-slate-100 text-xs font-mono">
                  {result.sample_cleaned_rows?.map((r, i) => (
                    <tr key={i} className="hover:bg-slate-50">
                      <td className="py-2 px-3">{r.Container_ID}</td>
                      <td className="py-2 px-3">{r.Tenant_ID}</td>
                      <td className="py-2 px-3 font-semibold text-brand-600">{r.Requested_CPU_Cores}</td>
                      <td className="py-2 px-3">{r.Requested_Memory_MB}</td>
                      <td className="py-2 px-3">{r.Execution_Start_Time_ms}</td>
                      <td className="py-2 px-3">{r.Makespan_ms}</td>
                      <td className="py-2 px-3">{r.Optimal_Scheduling}</td>
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
