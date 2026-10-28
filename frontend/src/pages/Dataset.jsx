import React, { useState, useEffect } from 'react';
import { Database, Upload, FileText, CheckCircle2, AlertTriangle, RefreshCw } from 'lucide-react';
import { getDatasetPreview, uploadDataset } from '../services/api';

export default function Dataset() {
  const [dataInfo, setDataInfo] = useState(null);
  const [loading, setLoading] = useState(false);
  const [uploading, setUploading] = useState(false);
  const [uploadMsg, setUploadMsg] = useState(null);
  const [errorMsg, setErrorMsg] = useState(null);

  useEffect(() => {
    fetchPreview();
  }, []);

  const fetchPreview = async () => {
    setLoading(true);
    setErrorMsg(null);
    try {
      const res = await getDatasetPreview(50);
      setDataInfo(res.data);
    } catch (err) {
      console.error('Failed to preview dataset', err);
      const detail = err.response?.data?.detail || err.message || 'Failed to preview dataset.';
      setErrorMsg(detail);
    } finally {
      setLoading(false);
    }
  };

  const handleFileUpload = async (e) => {
    const file = e.target.files[0];
    if (!file) return;

    const formData = new FormData();
    formData.append('file', file);

    setUploading(true);
    setUploadMsg(null);
    setErrorMsg(null);
    try {
      const res = await uploadDataset(formData);
      setUploadMsg(`Uploaded ${file.name} successfully (${res.data.rows} rows).`);
      fetchPreview();
    } catch (err) {
      const detail = err.response?.data?.detail || err.message || 'Failed to upload file.';
      setErrorMsg(detail);
    } finally {
      setUploading(false);
    }
  };

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex flex-col md:flex-row md:items-center justify-between gap-4 bg-white border border-slate-200 p-6 rounded-xl shadow-xs">
        <div>
          <h1 className="text-xl font-bold text-slate-900 tracking-tight">Dataset Management & Ingestion</h1>
          <p className="text-xs text-slate-500 mt-1">
            Google Cluster Workload Trace / Container Scheduling Dataset (10,000 Rows)
          </p>
        </div>

        {/* Upload Form */}
        <div className="flex items-center gap-3">
          <label className="flex items-center gap-2 bg-white hover:bg-slate-50 text-slate-700 text-xs font-semibold px-4 py-2.5 rounded-lg border border-slate-300 transition-all cursor-pointer shadow-xs">
            <Upload className="w-4 h-4 text-brand-600" />
            <span>Upload Custom CSV</span>
            <input type="file" accept=".csv" onChange={handleFileUpload} className="hidden" />
          </label>
          <button 
            onClick={fetchPreview}
            className="p-2.5 rounded-lg border border-slate-300 bg-white hover:bg-slate-50 text-slate-600 text-xs font-semibold"
            title="Refresh"
          >
            <RefreshCw className={`w-4 h-4 ${loading ? 'animate-spin' : ''}`} />
          </button>
        </div>
      </div>

      {uploadMsg && (
        <div className="bg-brand-50 border border-brand-200 text-brand-700 px-4 py-3 rounded-xl text-xs font-medium flex items-center gap-2">
          <CheckCircle2 className="w-4 h-4 text-brand-600" />
          <span>{uploadMsg}</span>
        </div>
      )}

      {errorMsg && (
        <div className="bg-rose-50 border border-rose-200 text-rose-800 px-4 py-3 rounded-xl text-xs font-medium flex items-center gap-2">
          <AlertTriangle className="w-4 h-4 text-rose-600" />
          <span>{errorMsg}</span>
        </div>
      )}

      {/* Dataset Summary Cards */}
      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
        <div className="bg-white border border-slate-200 p-5 rounded-xl">
          <div className="text-xs font-semibold text-slate-500 uppercase">Total Row Count</div>
          <div className="text-2xl font-bold text-slate-900 mt-2">{dataInfo?.total_rows || '10,000'}</div>
          <div className="text-xs text-slate-500 mt-1">Scheduling records</div>
        </div>
        <div className="bg-white border border-slate-200 p-5 rounded-xl">
          <div className="text-xs font-semibold text-slate-500 uppercase">Total Feature Columns</div>
          <div className="text-2xl font-bold text-slate-900 mt-2">{dataInfo?.total_columns || '26'}</div>
          <div className="text-xs text-slate-500 mt-1">Numerical & Categorical</div>
        </div>
        <div className="bg-white border border-slate-200 p-5 rounded-xl">
          <div className="text-xs font-semibold text-slate-500 uppercase">Missing Values</div>
          <div className="text-2xl font-bold text-emerald-600 mt-2">{dataInfo?.missing_values ?? '0'}</div>
          <div className="text-xs text-slate-500 mt-1">Detected missing cells</div>
        </div>
        <div className="bg-white border border-slate-200 p-5 rounded-xl">
          <div className="text-xs font-semibold text-slate-500 uppercase">Duplicate Records</div>
          <div className="text-2xl font-bold text-emerald-600 mt-2">{dataInfo?.duplicates ?? '0'}</div>
          <div className="text-xs text-slate-500 mt-1">Identified duplicate rows</div>
        </div>
      </div>

      {/* Dataset Table Preview */}
      <div className="bg-white border border-slate-200 rounded-xl p-5 shadow-xs">
        <div className="flex items-center justify-between mb-4 border-b border-slate-100 pb-3">
          <div>
            <h3 className="text-sm font-bold text-slate-900">Dataset Rows Preview</h3>
            <p className="text-xs text-slate-500">Displaying top 50 scheduling job records</p>
          </div>
          <span className="text-xs font-mono bg-slate-100 px-2.5 py-1 rounded text-slate-600">
            {dataInfo?.filename || 'container_scheduling_dataset_10000.csv'}
          </span>
        </div>

        {loading ? (
          <div className="py-12 text-center text-slate-400 text-xs">Loading dataset preview...</div>
        ) : (
          <div className="overflow-x-auto max-h-96">
            <table className="w-full text-left border-collapse min-w-[1200px]">
              <thead className="sticky top-0 bg-slate-100 text-[11px] font-semibold text-slate-600 uppercase border-b border-slate-200">
                <tr>
                  {dataInfo?.columns?.slice(0, 12).map((col) => (
                    <th key={col} className="py-2.5 px-3 truncate">{col}</th>
                  ))}
                </tr>
              </thead>
              <tbody className="divide-y divide-slate-100 text-xs font-mono">
                {dataInfo?.preview_rows?.map((row, idx) => (
                  <tr key={idx} className="hover:bg-slate-50">
                    {dataInfo?.columns?.slice(0, 12).map((col) => (
                      <td key={col} className="py-2 px-3 text-slate-700 truncate max-w-[150px]">
                        {row[col] !== null ? String(row[col]) : '-'}
                      </td>
                    ))}
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        )}
      </div>
    </div>
  );
}
