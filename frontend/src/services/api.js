import axios from 'axios';

// Configurable API Base URL: checks Vite env variable, falls back to relative '/api' or local backend
const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || 'http://127.0.0.1:8000/api';

const api = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json',
  },
});

export const getSystemStatus = () => api.get('/status');
export const getDatasetPreview = (maxRows = 50) => api.get(`/dataset/preview?max_rows=${maxRows}`);
export const uploadDataset = (formData) => api.post('/dataset/upload', formData, {
  headers: { 'Content-Type': 'multipart/form-data' }
});
export const runPreprocessing = (params) => api.post('/preprocessing/run', params);
export const generateWorkload = (scenario, numJobs, seed) => 
  api.post(`/workload/generate?scenario=${scenario}&num_jobs=${numJobs}&seed=${seed}`);
export const runSimulation = (payload) => api.post('/simulation/run', payload);
export const runBenchmark = (payload) => api.post('/benchmark/run', payload);
export const getExperimentHistory = () => api.get('/experiments/history');

export default api;
